/**
 * LSCM Solver - WebAssembly + Eigen Implementation
 * 
 * 基于 Eigen 稀疏矩阵的 LSCM UV 展开求解器。
 * 使用 SimplicialLDLT (稀疏 Cholesky 分解) 求解 A^TA x = A^Tb。
 */

#include <emscripten/bind.h>
#include <Eigen/Eigen>
#include <Eigen/Sparse>
#include <vector>
#include <cmath>
#include <chrono>
#include <algorithm>
#include <iostream>

using SparseMat = Eigen::SparseMatrix<double>;
using Trip = Eigen::Triplet<double>;
using SpLDLT = Eigen::SimplicialLDLT<SparseMat>;
using VecXd = Eigen::VectorXd;

/**
 * 计算局部三角形的 LSCM 梯度权重
 */
bool buildLocalTriangle(
    const double p0[3], const double p1[3], const double p2[3],
    double grad[3][2], double& area
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
        return false;
    }
    
    // 归一化得到法向量
    double nx = cross[0] / area2;
    double ny = cross[1] / area2;
    double nz = cross[2] / area2;
    
    // xAxis = normalize(e1)
    double len_e1 = std::sqrt(e1[0] * e1[0] + e1[1] * e1[1] + e1[2] * e1[2]);
    if (len_e1 < 1e-10) return false;
    double ux = e1[0] / len_e1;
    double uy = e1[1] / len_e1;
    double uz = e1[2] / len_e1;
    
    // yAxis = normal × xAxis
    double vx = ny * uz - nz * uy;
    double vy = nz * ux - nx * uz;
    double vz = nx * uy - ny * ux;
    
    // 局部坐标
    double x1 = len_e1;
    double x2 = e2[0] * ux + e2[1] * uy + e2[2] * uz;
    double y2 = e2[0] * vx + e2[1] * vy + e2[2] * vz;
    
    // 有符号面积
    double signedArea2 = x1 * y2;
    if (std::abs(signedArea2) < 1e-10) return false;
    
    // 梯度权重 (伴随矩阵行列式形式)
    grad[0][0] = -y2 / signedArea2;  grad[0][1] = x2 / signedArea2;
    grad[1][0] = y2 / signedArea2;   grad[1][1] = -x2 / signedArea2;
    grad[2][0] = 0;                  grad[2][1] = -y2 / signedArea2;
    
    area = std::abs(signedArea2) * 0.5;
    return true;
}

/**
 * 求解 LSCM
 */
emscripten::val solve_lscm(
    emscripten::val positions_val,
    emscripten::val faces_val,
    int anchor0,
    int anchor1
) {
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // // 从 JS 复制数据
    std::vector<double> positions = emscripten::vecFromJSArray<double>(positions_val);
    std::vector<int> faces = emscripten::vecFromJSArray<int>(faces_val);
    
    int n = positions.size() / 3;  // 顶点数
    int m = faces.size() / 3;       // 面数
    
    if (n < 3 || m < 1) {
        return emscripten::val::object();
    }
    
    // 固定顶点
    std::map<int, std::array<double, 2>> fixed;
    fixed[anchor0] = { 0.0, 0.0 };
    fixed[anchor1] = { 1.0, 0.0 };
    
    // 自由变量映射
    std::vector<int> freeMap(n, -1);
    int freeCount = 0;
    for (int i = 0; i < n; i++) {
        if (fixed.find(i) == fixed.end()) {
            freeMap[i] = freeCount++;
        }
    }
    
    int varCount = freeCount * 2;  // 每个自由顶点有 u, v 两个变量
    if (varCount < 2) {
        return emscripten::val::object();
    }
    
    // 构建稀疏矩阵
    std::vector<Trip> triplets;
    triplets.reserve(m * 36);  // 每个面最多 36 个非零项
    
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
        double area;
        if (!buildLocalTriangle(p0, p1, p2, grad, area)) {
            continue;
        }
        
        double w = std::sqrt(area);
        
        // 收集每个顶点的变量索引和系数
        struct VarTerm {
            int varIdx;
            double coeff;
        };
        std::vector<VarTerm> uTerms, vTerms;
        double uRhs = 0, vRhs = 0;
        
        int vids[3] = { idx0, idx1, idx2 };
        for (int c = 0; c < 3; c++) {
            int vid = vids[c];
            double du = grad[c][0] * w;
            double dv = grad[c][1] * w;
            
            if (fixed.find(vid) != fixed.end()) {
                // 固定顶点: 移到右端
                double u0 = fixed[vid][0];
                double v0 = fixed[vid][1];
                uRhs += dv * u0 - du * v0;
                vRhs += dv * v0 + du * u0;
            } else {
                int base = freeMap[vid] * 2;
                uTerms.push_back({ base, dv });     // u 方程: dv
                uTerms.push_back({ base + 1, -du }); // u 方程: -du
                vTerms.push_back({ base, -dv });     // v 方程: -dv
                vTerms.push_back({ base + 1, du });  // v 方程: du
            }
        }
        
        // 累加到 A^TA
        for (const auto& a : uTerms) {
            for (const auto& b : uTerms) {
                triplets.emplace_back(a.varIdx, b.varIdx, a.coeff * b.coeff);
            }
            rhs(a.varIdx) += a.coeff * uRhs;
        }
        
        for (const auto& a : vTerms) {
            for (const auto& b : vTerms) {
                triplets.emplace_back(a.varIdx, b.varIdx, a.coeff * b.coeff);
            }
            rhs(a.varIdx) += a.coeff * vRhs;
        }
    }
    
    // 添加正则化项
    for (int i = 0; i < varCount; i++) {
        triplets.emplace_back(i, i, 1e-10);
    }
    
    // 构建稀疏矩阵
    SparseMat ata(varCount, varCount);
    ata.setFromTriplets(triplets.begin(), triplets.end());
    ata.makeCompressed();
    // 稀疏 Cholesky 分解求解
    // SpLDLT solver;
    // solver.compute(ata);
    
    VecXd sol;
    // std::cout << "XXXXX"<< std::endl;
    // if (solver.info() != Eigen::ComputationInfo::Success) {
    //     // 回退: 使用稠密求解
    //     std::cout << "Dense"<< std::endl;
    //     Eigen::MatrixXd ataDense = Eigen::MatrixXd(ata);
    //     sol = ataDense.colPivHouseholderQr().solve(rhs);
    // } else {
    //     std::cout << "Cholesky"<< std::endl;
    //     sol = solver.solve(rhs);
    // }
    Eigen::MatrixXd ataDense = Eigen::MatrixXd(ata);
    sol = ataDense.colPivHouseholderQr().solve(rhs);
    
    // // 组装结果 UV
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
std::cout << "DEBUG: positions.size()=" << positions.size() << std::endl;
    // 返回 JS 对象
    emscripten::val result = emscripten::val::object();
    result.set("uv", emscripten::val::array(uv));
    result.set("time_ms", time_ms);
    
    return result;
}

// Emscripten 绑定
EMSCRIPTEN_BINDINGS(lscm_module) {
    emscripten::function("solve_lscm", &solve_lscm);
}
