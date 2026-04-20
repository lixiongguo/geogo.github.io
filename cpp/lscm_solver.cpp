/**
 * LSCM Solver - WebAssembly + Eigen Implementation
 * 
 * 基于 Eigen 稀疏矩阵的 LSCM UV 展开求解器。
 * 使用 SimplicialLDLT (稀疏 Cholesky 分解) 求解 A^TA x = A^Tb。
 * 
 * 编译方式:
 *   em++ lscm_solver.cpp -o ../assets/wasm/lscm_solver.js \
 *     -O3 -std=c++17 \
 *     -I/path/to/eigen \
 *     --bind \
 *     -s MODULARIZE=1 \
 *     -s EXPORT_NAME="LCMSolver" \
 *     -s ALLOW_MEMORY_GROWTH=1 \
 *     -s TOTAL_MEMORY=256MB
 */

#include <emscripten/bind.h>
#include <Eigen/Eigen>
#include <Eigen/Sparse>
#include <vector>
#include <cmath>
#include <chrono>

// 不使用 using namespace Eigen，避免类型名冲突
using SparseMat = Eigen::SparseMatrix<double>;
using Trip = Eigen::Triplet<double>;
using SpLDLT = Eigen::SimplicialLDLT<SparseMat>;
using VecXd = Eigen::VectorXd;
using MatXd = Eigen::MatrixXd;
using ComputationInfo = Eigen::ComputationInfo;

/**
 * 计算局部三角形的 LSCM 梯度权重
 */
std::vector<double> buildLocalTriangle(
    const double p0[3], const double p1[3], const double p2[3],
    double grad[3][2]
) {
    double e1[3] = { p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2] };
    double e2[3] = { p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2] };
    
    // 叉积 e1 × e2
    double cross[3] = {
        e1[1] * e2[2] - e1[2] * e2[1],
        e1[2] * e2[0] - e1[0] * e2[2],
        e1[0] * e2[1] - e1[1] * e2[0]
    };
    double area2 = std::sqrt(cross[0] * cross[0] + cross[1] * cross[1] + cross[2] * cross[2]);
    
    if (area2 < 1e-10) {
        return { 0.0 };
    }
    
    // 归一化得到法向量
    double nx = cross[0] / area2;
    double ny = cross[1] / area2;
    double nz = cross[2] / area2;
    
    // xAxis = normalize(e1)
    double len_e1 = std::sqrt(e1[0] * e1[0] + e1[1] * e1[1] + e1[2] * e1[2]);
    if (len_e1 < 1e-10) return { 0.0 };
    double ux = e1[0] / len_e1;
    double uy = e1[1] / len_e1;
    double uz = e1[2] / len_e1;
    
    // yAxis = normal × xAxis
    double vx = ny * uz - nz * uy;
    double vy = nz * ux - nx * uz;
    double vz = nx * uy - ny * ux;
    
    // 局部坐标
    double x0 = 0, y0 = 0;
    double x1 = len_e1, y1 = 0;
    double x2 = e2[0] * ux + e2[1] * uy + e2[2] * uz;
    double y2 = e2[0] * vx + e2[1] * vy + e2[2] * vz;
    
    // 有符号面积
    double signedArea2 = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0);
    if (std::abs(signedArea2) < 1e-10) return { 0.0 };
    
    // 梯度权重 (伴随矩阵行列式形式)
    grad[0][0] = (y1 - y2) / signedArea2;  grad[0][1] = (x2 - x1) / signedArea2;
    grad[1][0] = (y2 - y0) / signedArea2;  grad[1][1] = (x0 - x2) / signedArea2;
    grad[2][0] = (y0 - y1) / signedArea2;  grad[2][1] = (x1 - x0) / signedArea2;
    
    return { 1.0, std::abs(signedArea2) * 0.5 };
}

/**
 * 求解 LSCM
 * 
 * @param positions 顶点位置数组 (n × 3)，扁平化格式 [x0,y0,z0, x1,y1,z1, ...]
 * @param faces     三角形面数组 (m × 3)，索引格式 [i0,i1,i2, ...]
 * @param anchor0   第一个锚点索引
 * @param anchor1   第二个锚点索引
 * @return JS 对象 { uv: Float64Array, time_ms: double }
 */
emscripten::val solve_lscm(
    emscripten::val positions_val,
    emscripten::val faces_val,
    int anchor0,
    int anchor1
) {
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // 从 JS 复制数据到本地向量
    std::vector<double> positions = emscripten::vecFromJSArray<double>(positions_val);
    std::vector<int> faces = emscripten::vecFromJSArray<int>(faces_val);
    
    int n = positions.size() / 3;  // 顶点数
    int m = faces.size() / 3;       // 面数
    
    if (n < 3 || m < 1) {
        return emscripten::val::object();
    }
    
    // 固定顶点映射
    std::map<int, std::array<double, 2>> fixed;
    fixed[anchor0] = { 0.0, 0.0 };
    fixed[anchor1] = { 1.0, 0.0 };
    
    // 自由变量映射
    std::map<int, int> freeMap;
    int freeCount = 0;
    for (int i = 0; i < n; i++) {
        if (fixed.find(i) == fixed.end()) {
            freeMap[i] = freeCount++;
        }
    }
    
    int varCount = freeCount * 2;  // 每个自由顶点有 u, v 两个变量
    if (varCount == 0) {
        return emscripten::val::object();
    }
    
    // 使用 Triplet 构建稀疏矩阵
    std::vector<Trip> triplets;
    triplets.reserve(m * 12);  // 每个面贡献 4 个非零项 (两个方程)
    
    // 右端向量
    VecXd rhs(varCount);
    rhs.setZero();
    
    // 遍历所有三角形
    for (int f = 0; f < m; f++) {
        int idx0 = faces[f * 3 + 0];
        int idx1 = faces[f * 3 + 1];
        int idx2 = faces[f * 3 + 2];
        
        double p0[3] = { positions[idx0 * 3], positions[idx0 * 3 + 1], positions[idx0 * 3 + 2] };
        double p1[3] = { positions[idx1 * 3], positions[idx1 * 3 + 1], positions[idx1 * 3 + 2] };
        double p2[3] = { positions[idx2 * 3], positions[idx2 * 3 + 1], positions[idx2 * 3 + 2] };
        
        double grad[3][2];
        auto result = buildLocalTriangle(p0, p1, p2, grad);
        if (result[0] == 0.0) continue;  // 退化三角形
        
        double weight = std::sqrt(result[1]);
        
        // LSCM 方程: 对于每个顶点角, 累积梯度贡献
        // 方程 1: dC1/du * w, dC1/dv * (-w)
        // 方程 2: dC1/du * w, dC1/dv * w
        for (int c = 0; c < 3; c++) {
            int vid = (c == 0) ? idx0 : (c == 1) ? idx1 : idx2;
            double du = grad[c][0] * weight;
            double dv = grad[c][1] * weight;
            
            auto addCoeff = [&](int varIdx, double coeff, bool isU) {
                if (fixed.find(vid) != fixed.end()) {
                    // 固定顶点: 移到右端
                    double fixedVal = fixed[vid][isU ? 0 : 1];
                    rhs(varIdx) -= coeff * fixedVal;
                } else {
                    int mappedIdx = freeMap[vid] * 2 + (isU ? 0 : 1);
                    triplets.emplace_back(varIdx, mappedIdx, coeff);
                }
            };
            
            // 方程 1: u 分量, v 分量取负
            addCoeff(0, du, true);
            addCoeff(0, -dv, false);
            
            // 方程 2: v 分量, u 分量取正
            if (varCount > 1) {
                addCoeff(1, dv, true);
                addCoeff(1, du, false);
            }
        }
    }
    
    // 构建稀疏矩阵 A^TA (通过组装)
    // 注意: 这里使用简化的方式, 直接构建稠密子块后转稀疏
    // 对于大型网格, 应该使用 A^T * A 的稀疏结构
    
    // 实际上更高效的方式是直接构建 A, 然后计算 A^T * A
    // 这里先用简化版本: 构建 A 的三元组, 然后计算 A^T * A
    
    std::vector<Trip> ataTriplets;
    ataTriplets.reserve(varCount * 20);  // 估计非零元数量
    
    // 重新组装: 对每个三角形贡献到 A^TA
    for (int f = 0; f < m; f++) {
        int idx0 = faces[f * 3 + 0];
        int idx1 = faces[f * 3 + 1];
        int idx2 = faces[f * 3 + 2];
        
        double p0[3] = { positions[idx0 * 3], positions[idx0 * 3 + 1], positions[idx0 * 3 + 2] };
        double p1[3] = { positions[idx1 * 3], positions[idx1 * 3 + 1], positions[idx1 * 3 + 2] };
        double p2[3] = { positions[idx2 * 3], positions[idx2 * 3 + 1], positions[idx2 * 3 + 2] };
        
        double grad[3][2];
        auto result = buildLocalTriangle(p0, p1, p2, grad);
        if (result[0] == 0.0) continue;
        
        double w = std::sqrt(result[1]);
        
        // 收集该三角形的变量索引和权重
        std::vector<std::pair<int, double>> terms;
        double knownU = 0, knownV = 0;
        
        int vids[3] = { idx0, idx1, idx2 };
        for (int c = 0; c < 3; c++) {
            int vid = vids[c];
            double du = grad[c][0] * w;
            double dv = grad[c][1] * w;
            
            if (fixed.find(vid) != fixed.end()) {
                // 固定顶点
                double u0 = fixed[vid][0];
                double v0 = fixed[vid][1];
                knownU += du * v0 - dv * u0;  // LSCM 方程右侧
                knownV += dv * v0 + du * u0;
            } else {
                int base = freeMap[vid] * 2;
                terms.push_back({ base, du });      // u 系数
                terms.push_back({ base + 1, -dv }); // -v 系数
            }
        }
        
        // 累加到 A^TA
        for (auto& a : terms) {
            for (auto& b : terms) {
                ataTriplets.emplace_back(a.first, b.first, a.second * b.second);
            }
            // 右端向量
            rhs(a.first) += a.second * knownU;
        }
        
        // 同理处理 v 方程
        terms.clear();
        knownU = knownV = 0;
        for (int c = 0; c < 3; c++) {
            int vid = vids[c];
            double du = grad[c][0] * w;
            double dv = grad[c][1] * w;
            
            if (fixed.find(vid) != fixed.end()) {
                double u0 = fixed[vid][0];
                double v0 = fixed[vid][1];
                knownV += dv * v0 + du * u0;
            } else {
                int base = freeMap[vid] * 2;
                terms.push_back({ base, dv });      // v 系数
                terms.push_back({ base + 1, du });   // u 系数
            }
        }
        
        for (auto& a : terms) {
            for (auto& b : terms) {
                ataTriplets.emplace_back(a.first + 1, b.first + 1, a.second * b.second);
            }
            rhs(a.first + 1) += a.second * knownV;
        }
    }
    
    // 添加正则化项避免奇异
    for (int i = 0; i < varCount; i++) {
        ataTriplets.emplace_back(i, i, 1e-8);
    }
    
    // 构建稀疏矩阵
    SparseMat ata(varCount, varCount);
    ata.setFromTriplets(ataTriplets.begin(), ataTriplets.end());
    ata.makeCompressed();
    
    // 稀疏 Cholesky 分解求解
    SpLDLT solver;
    solver.compute(ata);
    
    if (solver.info() != ComputationInfo::Success) {
        // 求解失败, 尝试增加正则化
        ata.diagonal().array() += 1e-4;
        solver.compute(ata);
    }
    
    VecXd sol = solver.solve(rhs);
    
    if (solver.info() != ComputationInfo::Success) {
        // 最终回退: 使用稠密求解
        MatXd ataDense = MatXd(ata);
        sol = ataDense.colPivHouseholderQr().solve(rhs);
    }
    
    // 组装结果 UV
    std::vector<double> uv(n * 2);
    for (int i = 0; i < n; i++) {
        if (fixed.find(i) != fixed.end()) {
            uv[i * 2] = fixed[i][0];
            uv[i * 2 + 1] = fixed[i][1];
        } else {
            int base = freeMap[i] * 2;
            uv[i * 2] = sol(base);
            uv[i * 2 + 1] = sol(base + 1);
        }
    }
    
    // 归一化到 [0, 1]
    double minU = 1e100, maxU = -1e100, minV = 1e100, maxV = -1e100;
    for (int i = 0; i < n; i++) {
        minU = std::min(minU, uv[i * 2]);
        maxU = std::max(maxU, uv[i * 2]);
        minV = std::min(minV, uv[i * 2 + 1]);
        maxV = std::max(maxV, uv[i * 2 + 1]);
    }
    
    double spanU = std::max(maxU - minU, 1e-8);
    double spanV = std::max(maxV - minV, 1e-8);
    double scale = 1.0 / std::max(spanU, spanV);
    
    for (int i = 0; i < n; i++) {
        uv[i * 2] = (uv[i * 2] - minU) * scale;
        uv[i * 2 + 1] = (uv[i * 2 + 1] - minV) * scale;
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    double time_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
    
    // 返回 JS 对象
    emscripten::val result = emscripten::val::object();
    result.set("uv", emscripten::val::array(uv));
    result.set("time_ms", time_ms);
    result.set("n", n);
    result.set("m", m);
    
    return result;
}

// Emscripten 绑定
EMSCRIPTEN_BINDINGS(lscm_module) {
    emscripten::function("solve_lscm", &solve_lscm);
}
