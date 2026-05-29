---
name: abfpp-augmented-lagrangian
overview: 用增广拉格朗日法（Augmented Lagrangian）重写 AbfPlusPlus.cpp，实现真正的 ABF++ 角度空间优化，并将方法论记录到数值优化文档中。
todos:
  - id: rewrite-abfpp-header
    content: 重写 AbfPlusPlus.h：保留 Parameterization 继承和 parameterize 接口，新增私有辅助方法声明（buildAngleData、buildConstraintJacobian、augmentedLagrangianSolve、newtonStep、angleToUv）
    status: completed
  - id: rewrite-abfpp-cpp
    content: 重写 AbfPlusPlus.cpp：实现增广拉格朗日 ABF++ 完整算法（角度变量构建、约束 Jacobian、外循环乘子更新、Newton 子问题、角度→UV 重建）
    status: completed
    dependencies:
      - rewrite-abfpp-header
  - id: add-al-doc
    content: 在 2019-04-01-6.附录-6.1 数值优化.md 的 LM 方法之后插入增广拉格朗日法章节，包含一般形式、ABF++ 应用、KKT 系统结构、角度→UV 重建原理
    status: completed
---

## 用户需求

1. 确认当前 `AbfPlusPlus::parameterize()` 只是调用 `LinAbf` 的 damped iterative 版本（并非论文中真正的 ABF++）
2. 用增广拉格朗日法（Augmented Lagrangian）真正实现 ABF++，在角度空间直接优化
3. 将增广拉格朗日法原理及应用记录到数值优化附录文档

## 核心功能

- **角度空间优化**：每个三角形 3 个角 α_i^t 作为优化变量（共 3F 维），目标最小化 (α − β)² / β
- **约束处理**：三角形和约束 α_1+α_2+α_3 = π、内部顶点环绕角=2π、边界顶点环绕角=θ_boundary，全部为线性约束
- **增广拉格朗日外循环**：Newton 法极小化增广拉格朗日函数 → 更新乘子 λ ← λ + ρ·c(α) → 增大惩罚因子 ρ
- **Newton 系统**：因所有约束线性（∇²c_j = 0），Hessian 简化为 Hessian(D) + ρ J^T J，结构极度稀疏，用 Eigen::SimplicialLDLT 求解
- **角度→UV 重建**：优化后的角度确定三角形相似形状，固定边界到圆环，求解稀疏线性系统恢复 UV 坐标
- 保持现有接口 `_solve_abfpp` 不变，WASM 导出不受影响

## 技术栈

- **语言**：C++17（与现有代码一致）
- **线性代数**：Eigen 3.4.0（SparseMatrix、SimplicialLDLT、VectorXd）
- **WASM 编译**：Emscripten（em++），构建脚本 `build_wasm_all.ps1` 已包含 AbfPlusPlus.cpp
- **数据结构**：现有 Mesh 半边结构（HalfEdge/Face/Vertex）

## 实现方案

### 整体策略：在角度空间用增广拉格朗日法直接优化

当前 `AbfPlusPlus::parameterize()` 调用 `LinAbf` 在 UV 空间做迭代重加权，收敛慢且并非论文原算法。真正的 ABF++ (Sheffer et al. 2005) 的核心思路是：

1. **放弃在 UV 空间求解**，转而在角度空间 α_i^t 直接优化
2. 优化完成后，再从角度反推 UV 坐标

### 算法详细步骤

#### Phase 1：构建角度变量映射

- 遍历所有非边界三角形面，为每个面的 3 个角分配全局索引 0…(3F-1)
- 并行计算每角的 3D 目标角度 β_i^t（使用 `angle3D`）
- 建立 corner→vertex 映射，便于构建顶点约束 Jacobian

#### Phase 2：构建约束 Jacobian J

- **三角形约束**（F 行 × 3F 列）：每面一行，三个角位置置 1
- **内部顶点约束**（V_int 行 × 3F 列）：每顶点一行，入射角对应的列置 1
- **边界顶点约束**（V_bnd 行 × 3F 列）：同上，但 RHS 是边界曲率角 θ_v

J 极度稀疏，每行只有 degree(v)+1 个非零元。

#### Phase 3：增广拉格朗日外循环

```
初始化: α ← β（目标角度作为初值）, λ ← 0, ρ ← 1e-3
for iter = 0…maxOuterIter:
    Newton 法极小化 L(α; λ, ρ)
    c = 约束残差向量
    λ ← λ + ρ·c                // 乘子更新
    若 ρ < ρ_max: ρ ← min(ρ * 1.5, ρ_max)  // 惩罚因子递增
    若 ||c||_∞ < ε: break      // 约束满足，收敛
```

#### Phase 4：Newton 子问题求解

增广拉格朗日函数的梯度与 Hessian：

- **梯度**：∇L_i = 2(α_i − β_i)/β_i + Σ_j λ_j·∂c_j/∂α_i + ρ·Σ_j c_j·∂c_j/∂α_i
- **Hessian**：因所有约束都是 α 的线性函数，∇²c_j ≡ 0
∇²L_ii = 2/β_i（对角） + ρ·(J^T J)_ii
- 稀疏 SPD 系统 (D + ρ J^T J) Δα = −∇L，用 SimplicialLDLT 求解
- 加入线搜索确保角度 > 0 且目标下降

#### Phase 5：角度→UV 重建

- 固定最外层边界顶点到单位圆（复用 LinAbf 的 `pinLoopOnCircle`）
- 对每个三角形，已知三个优化角度，可确定其相似形状
- 构造方程：相邻三角形共享边的 UV 向量应一致，形成超定线性系统
- 最小二乘求解得到内点 UV

### 性能分析

- **变量规模**：3F（~3×顶点数），稀疏 Hessian 每行仅 ~20 个非零元
- **瓶颈**：SimplicialLDLT 分解 O(nnz²)，对于 10K 顶点网格约 30K 变量，Hessian 仍高度稀疏
- **加速**：用 `A.selfadjointView<Eigen::Upper>()` 优化稀疏矩阵分解

### 与现有代码的关系

- `AbfPlusPlus.h` 接口不变（`parameterize()` 签名不变）
- 移除对 `LinAbf` 的依赖（`#include "LinAbf.h"` 不再需要）
- 新增私有辅助方法，保持文件内聚
- WASM 导出表 `_solve_abfpp` 已存在，不影响前端调用
- `dampUvUpdate` 和 `computeAngleResidual` 函数因算法改变而移除