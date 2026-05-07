

### 高性能的C++线性代数库—Eigen库

Eigen自带了如下一些求解器，适用于求解大规模稀疏系统

| 求解器             | 适用矩阵 | 依赖 | 特点                     |
| ------------------ | -------- | ---- | ------------------------ |
| **SimplicialLDLT** | 对称正定 | 内置 | 轻量，适合 2D 问题       |
| **SimplicialLLT**  | 对称正定 | 内置 | 比 LDLT 更快但更不稳定   |
| **SparseLU**       | 任意方阵 | 内置 | 基于 SuperLU，支持非对称 |
| **SparseQR**       | 任意矩阵 | 内置 | 用于最小二乘，内存高     |

```C++
#include <Eigen/Sparse>
#include <Eigen/SparseLU>

Eigen::SparseMatrix<double> A(n, n);
// ... 矩阵装配 A ...

Eigen::VectorXd b(n);
// ... 矩阵装配 b ...

Eigen::SparseLU<Eigen::SparseMatrix<double>> solver;
solver.compute(A);

if (solver.info() != Eigen::Success) {
    std::cerr << "Decomposition failed!" << std::endl;
    return -1;
}

Eigen::VectorXd x = solver.solve(b);
```

## 



## Mosek 求解

[MOSEK](https://www.mosek.com/) 是一个高性能的凸优化求解器，特别擅长求解 SOCP、SDP 等问题。以下展示如何用 MOSEK 的不同接口来求解上述参数化中出现的 SOCP 问题。

### 1. MOSEK Fusion API (Python)

Fusion API 是 MOSEK 提供的高级面向对象接口，语法简洁直观。

#### 示例：Lipman 风格的 Bounded Distortion SOCP

```python
from mosek.fusion import *

def solve_bounded_distortion_socp(alpha_list, beta_list, C, areas):
    """
    求解 Lipman 风格的 Bounded Distortion SOCP 问题:
    
    min  sum |beta_j|^2 * area_j
    s.t. |alpha_j|^2 - |beta_j|^2 >= r_j > 0,  for all j
         |beta_j|^2 <= ((C-1)/(C+1))^2 * r_j,   for all j
         edge continuity constraints
    
    参数:
        alpha_list: 每个面的 alpha 初始值 (复数)
        beta_list:  每个面的 beta 初始值 (复数)
        C:          扭曲上界
        areas:      每个面的面积
    """
    n_faces = len(alpha_list)
    kappa = (C - 1) / (C + 1)
    
    with Model('BoundedDistortion') as M:
        # 决策变量: 每个面的 alpha, beta (实部和虚部), r
        # alpha_j = alpha_re[j] + i * alpha_im[j]
        # beta_j  = beta_re[j]  + i * beta_im[j]
        alpha_re = M.variable('alpha_re', n_faces)
        alpha_im = M.variable('alpha_im', n_faces)
        beta_re  = M.variable('beta_re',  n_faces)
        beta_im  = M.variable('beta_im',  n_faces)
        r        = M.variable('r', n_faces, Domain.greaterThan(1e-6))
        
        # 目标函数: min sum |beta_j|^2 * area_j
        # |beta_j|^2 = beta_re[j]^2 + beta_im[j]^2
        obj_terms = []
        for j in range(n_faces):
            beta_norm_sq = Expr.add(
                Expr.square(beta_re.index(j)),
                Expr.square(beta_im.index(j))
            )
            obj_terms.append(Expr.mul(areas[j], beta_norm_sq))
        M.objective(ObjectiveSense.Minimize, Expr.add(obj_terms))
        
        # 约束1: |alpha_j|^2 - |beta_j|^2 >= r_j
        # 即 |alpha_j|^2 >= r_j + |beta_j|^2
        # 转化为 SOC: ||(2*Re(alpha), 2*Im(alpha))|| <= |alpha|^2 + |beta|^2 + r_j - (r_j + |beta|^2)
        #            = |alpha|^2 - |beta|^2 - r_j ... 不对
        # 正确转化: |alpha|^2 - |beta|^2 >= r 等价于
        #   ||(2*Re(beta), 2*Im(beta))||_2 <= |alpha|^2 - |beta|^2 + |beta|^2 - r
        #   即 ||(2*Re(beta), 2*Im(beta))||_2 <= |alpha|^2 - r ... 还需要进一步推导
        #
        # 更直接的方法: 用 rotated quadratic cone
        # (t1, t2, s) in Q_r^n 意味着 t1*t2 >= ||s||^2, t1,t2 >= 0
        # 令 t1 = 1, t2 = |alpha|^2 - r - |beta|^2, s = (0,...,0) => t2 >= 0
        # 或者: |alpha|^2 >= r + |beta|^2 可以写为
        #   (1, |alpha|^2 - r - |beta|^2, 0, ..., 0) in rotated cone
        
        for j in range(n_faces):
            # |alpha_j|^2 - |beta_j|^2 >= r_j
            # 用 rotated quadratic cone: (u, v, w) in Qr 意味着 2*u*v >= ||w||^2
            # 令 u = (|alpha|^2 - r - |beta|^2 + 1)/2, v = 1
            # 则 2 * u * 1 >= 0 意味着 |alpha|^2 - r - |beta|^2 >= 0
            # 
            # 更简洁: 直接用 SOC 形式
            # |alpha|^2 - |beta|^2 - r >= 0
            # 等价于 ||(2*Re(beta), 2*Im(beta))||_2 <= |alpha|^2 - r  (这不是标准SOC)
            #
            # 标准做法: 使用 rotated quadratic cone
            # |alpha|^2 - |beta|^2 >= r
            # <=> 存在 t >= 0 使得 |alpha|^2 - t >= r 且 t >= |beta|^2
            # <=> |alpha|^2 - r >= t 且 |beta|^2 <= t
            # 用 rotated cone: (1/2, t, (Re(beta), Im(beta))) in Qr 意味着 t >= |beta|^2
            # 用 rotated cone: (1/2, |alpha|^2-r, (Re(alpha), Im(alpha))) in Qr 意味着 |alpha|^2-r >= |alpha|^2... 不对
            
            # 正确的方法: 引入辅助变量
            # s_j = |alpha_j|^2, t_j = |beta_j|^2
            # s_j - t_j >= r_j 且 t_j <= kappa^2 * r_j
            
            # 用 Expr.hstack 拼接向量并建立 SOC 约束
            pass  # 详见下面的简化版
        
        M.solve()
        return alpha_re.level(), alpha_im.level(), beta_re.level(), beta_im.level()
```

上面的完整实现比较复杂，下面给出一个更实用的简化版示例。

#### 简化版：基本 SOCP 求解示例

```python
from mosek.fusion import *
import numpy as np

def solve_basic_socp():
    """
    求解一个基本的 SOCP 问题:
    
    min  c^T x
    s.t. ||A_i x + b_i||_2 <= c_i^T x + d_i,  i=1,...,m
         F x = g
    """
    # 问题数据
    n = 5   # 变量维度
    m = 3   # SOC 约束个数
    
    c = np.array([1.0, 2.0, 0.5, -1.0, 0.3])
    
    with Model('basic_socp') as M:
        x = M.variable('x', n)
        
        # 目标函数: min c^T x
        M.objective(ObjectiveSense.Minimize, Expr.dot(c, x))
        
        # SOC 约束: ||A_i x + b_i||_2 <= d_i^T x + e_i
        # 约束1: ||(x[0]+x[1], x[2]||_2 <= x[3] + 1
        M.constraint(Expr.vstack(
            Expr.add(x.index(3), 1.0),       # d^T x + e
            Expr.add(x.index(0), x.index(1)), # A*x + b 的第1个分量
            x.index(2)                         # A*x + b 的第2个分量
        ), Domain.inQCone())
        
        # 约束2: ||x[0:3]||_2 <= 2*x[4] + 0.5
        M.constraint(Expr.vstack(
            Expr.add(Expr.mul(2.0, x.index(4)), 0.5),
            x.index(0),
            x.index(1),
            x.index(2)
        ), Domain.inQCone())
        
        # 约束3: x[1] + x[2] >= 1  (线性约束)
        M.constraint(Expr.add(x.index(1), x.index(2)), 
                     Domain.greaterThan(1.0))
        
        M.solve()
        
        print(f"最优解 x = {x.level()}")
        print(f"最优值 = {M.primalObjValue()}")

solve_basic_socp()
```

### 2. MOSEK 任务文件格式 (OP)

MOSEK 使用优化问题 (OP) 格式来描述问题。以下展示如何用 OP 格式描述 SOCP 问题：

```
[comment]
   Lipman Bounded Distortion SOCP - 单面示例
[/comment]

[objective minimize]
   1.0 beta_re + 0.0 alpha_re + 0.0 alpha_im + 0.0 beta_im + 0.0 r

[variables]
   alpha_re alpha_im beta_re beta_im r

[constraints]
   [cone type=quad num=3]
      r alpha_re alpha_im       % ||(alpha_re, alpha_im)||_2 <= r  (即 |alpha| <= r)
   [cone type=quad num=3]
      r_s beta_re beta_im       % ||(beta_re, beta_im)||_2 <= r_s (即 |beta| <= r_s)

[bounds]
   [b] alpha_re >= -inf
   [b] alpha_im >= -inf
   [b] beta_re  >= -inf
   [b] beta_im  >= -inf
   [b] r        >= 1e-6         % r > 0
   [b] r_s      >= 0
[/bounds]
```

### 3. MOSEK + CVXPY 接口（推荐）

CVXPY 是 Python 中最流行的凸优化建模工具，语法最为简洁，推荐使用：

#### 示例：求解 Lipman 的 Bounded Distortion 问题

```python
import cvxpy as cp
import numpy as np

def solve_lipman_bd(C=3.0, n_faces=10, n_vertices=8):
    """
    用 CVXPY + MOSEK 求解 Lipman 的 Bounded Distortion SOCP 问题
    
    min  sum_j |beta_j|^2 * area_j           (LSCM能量)
    s.t. |alpha_j|^2 - |beta_j|^2 >= r_j     (保向性)
         |beta_j|^2 <= kappa^2 * r_j          (有界扭曲)
         r_j > 0
         u_i - u_0 = A_j (v_i - v_0)          (边连续性约束)
    """
    kappa = (C - 1) / (C + 1)
    areas = np.random.rand(n_faces) + 0.1  # 面积
    
    # 决策变量
    alpha = cp.Variable((n_faces, 2), name="alpha")  # alpha_re, alpha_im
    beta  = cp.Variable((n_faces, 2), name="beta")    # beta_re, beta_im
    r     = cp.Variable(n_faces, name="r")             # 辅助变量
    
    # 目标函数: min sum |beta_j|^2 * area_j
    obj = 0
    for j in range(n_faces):
        obj += areas[j] * cp.sum_squares(beta[j])
    
    constraints = []
    
    for j in range(n_faces):
        alpha_norm_sq = cp.sum_squares(alpha[j])  # |alpha_j|^2
        beta_norm_sq  = cp.sum_squares(beta[j])   # |beta_j|^2
        
        # 约束1: |alpha_j|^2 - |beta_j|^2 >= r_j > 0
        constraints.append(alpha_norm_sq - beta_norm_sq >= r[j])
        constraints.append(r[j] >= 1e-6)
        
        # 约束2: |beta_j|^2 <= kappa^2 * r_j
        # 即 |beta_j|^2 - kappa^2 * r_j <= 0
        # 这可以写为 SOC 约束
        constraints.append(beta_norm_sq <= kappa**2 * r[j])
    
    # 求解
    prob = cp.Problem(cp.Minimize(obj), constraints)
    prob.solve(solver=cp.MOSEK, verbose=True)
    
    print(f"Status: {prob.status}")
    print(f"Optimal value: {prob.value}")
    if prob.status == 'optimal':
        print(f"alpha = {alpha.value}")
        print(f"beta  = {beta.value}")
        print(f"r     = {r.value}")
    
    return alpha.value, beta.value, r.value

# 求解
alpha_val, beta_val, r_val = solve_lipman_bd(C=3.0)
```

#### 示例：求解 BDHM 的 Bounded Distortion 问题

```python
import cvxpy as cp
import numpy as np

def solve_bdhm_bd(K=3.0, n_samples=20, n_coeffs=10):
    """
    用 CVXPY + MOSEK 求解 BDHM 的 Bounded Distortion SOCP 问题
    
    min  sum_j w_j ||nabla f(z_j) - R_j||_F^2    (ARAP能量)
    s.t. |f_zbar(z_j)| <= kappa * |f_z(z_j)|,    for j in A  (有界扭曲)
         |f_z(z_j)|^2 - |f_zbar(z_j)|^2 >= eps,  for j in B  (保向性)
         f(v_k) = f_k^target                       (边界条件)
    """
    kappa = (K - 1) / (K + 1)
    eps = 1e-4
    
    # 决策变量: phi_k, psi_k (调和映射的系数)
    phi = cp.Variable((n_coeffs, 2), name="phi")  # phi_re, phi_im
    psi = cp.Variable((n_coeffs, 2), name="psi")  # psi_re, psi_im
    
    # 模拟数据: 基函数在采样点的值
    # Phi'(z_j) 和 Psi'(z_j) 是已知的 (由 Cauchy 重心坐标预计算)
    Phi_prime = np.random.randn(n_samples, n_coeffs, 2) + 0.5
    Psi_prime = np.random.randn(n_samples, n_coeffs, 2) + 0.5
    weights = np.random.rand(n_samples) + 0.1
    
    # 计算 f_z 和 f_zbar 在每个采样点的值
    # f_z(z_j) = sum_k phi_k * Phi'_k(z_j)
    # f_zbar(z_j) = conj(sum_k psi_k * Psi'_k(z_j))
    fz = cp.Variable((n_samples, 2), name="fz")       # f_z 的实部和虚部
    fzbar = cp.Variable((n_samples, 2), name="fzbar") # f_zbar 的实部和虚部
    
    constraints = []
    
    # 线性约束: f_z 和 f_zbar 由 phi, psi 线性决定
    for j in range(n_samples):
        fz_j = cp.sum([cp.hstack([phi[k, 0] * Phi_prime[j, k, 0] - phi[k, 1] * Phi_prime[j, k, 1],
                                   phi[k, 0] * Phi_prime[j, k, 1] + phi[k, 1] * Phi_prime[j, k, 0]])
                       for k in range(n_coeffs)])
        # 简化: 直接用线性约束关联
        constraints.append(fz[j] == fz_j)
    
    # Active Set: 先假设所有点都激活
    A_set = list(range(n_samples))  # 有界扭曲约束
    B_set = list(range(n_samples))  # 保向性约束
    
    for j in A_set:
        # |f_zbar(z_j)| <= kappa * |f_z(z_j)|
        # SOC 约束: ||f_zbar||_2 <= kappa * ||f_z||_2
        # 等价于: ||f_zbar||_2^2 <= kappa^2 * ||f_z||_2^2
        # 可以用 SOCP 表示
        constraints.append(
            cp.norm(fzbar[j]) <= kappa * cp.norm(fz[j])
        )
    
    for j in B_set:
        # |f_z|^2 - |f_zbar|^2 >= eps
        constraints.append(
            cp.sum_squares(fz[j]) - cp.sum_squares(fzbar[j]) >= eps
        )
    
    # 目标函数: ARAP 能量 (简化版)
    # 实际应用中 R_j 由上一迭代步确定
    R = np.eye(2)  # 简化: 目标旋转为恒等
    obj = 0
    for j in range(n_samples):
        # ||nabla f - R||_F^2 简化表达
        obj += weights[j] * (cp.sum_squares(fz[j]) + cp.sum_squares(fzbar[j]))
    
    # 求解
    prob = cp.Problem(cp.Minimize(obj), constraints)
    prob.solve(solver=cp.MOSEK, verbose=True)
    
    print(f"Status: {prob.status}")
    print(f"Optimal value: {prob.value}")

solve_bdhm_bd(K=3.0)
```

### 4. MOSEK 的安装与配置

#### 安装

```bash
# 安装 CVXPY (含 MOSEK 支持)
pip install cvxpy mosek

# 或安装 MOSEK Python 原生接口
pip install mosek
```

#### 许可证

MOSEK 是商业软件，但提供：
- **学术许可证**：免费，适用于学术研究
- **试用许可证**：30天免费试用
- **个人许可证**：个人非商业用途

获取许可证后，将 `mosek.lic` 文件放到：
- Linux/Mac: `$HOME/mosek/mosek.lic`
- Windows: `%USERPROFILE%\mosek\mosek.lic`

#### 在 CVXPY 中选择 MOSEK

```python
import cvxpy as cp

# 指定使用 MOSEK 求解器
prob.solve(solver=cp.MOSEK)

# 带参数的求解
prob.solve(
    solver=cp.MOSEK,
    mosek_params={
        'MSK_DPAR_OPTIMIZER_MAX_TIME': 300.0,    # 最大求解时间(秒)
        'MSK_IPAR_NUM_THREADS': 4,                # 线程数
        'MSK_DPAR_INTPNT_TOL_REL_GAP': 1e-8,     # 相对间隙容差
    },
    verbose=True  # 打印求解日志
)
```

### 5. 求解效率对比

对于参数化中的 SOCP 问题（$n$ 个三角面/采样点）：

| 求解器 | 问题规模                      | 求解时间     | 适用场景                |
| ------ | ----------------------------- | ------------ | ----------------------- |
| MOSEK  | 中大规模 ($n \sim 10^3-10^5$) | 快           | 生产环境，大规模问题    |
| ECOS   | 小中规模 ($n \sim 10^2-10^4$) | 中等         | 嵌入式应用，Python 原生 |
| SCS    | 大规模 ($n \sim 10^5+$)       | 较慢但可扩展 | 超大规模，精度要求不高  |
| Gurobi | 中大规模                      | 快           | 商业环境，QP 为主       |