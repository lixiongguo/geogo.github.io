## IK 蜘蛛 — CCD 逆运动学驱动

本 demo 用 **CCD（Cyclic Coordinate Descent，循环坐标下降）** 求解器驱动 8 条三骨节腿，足端目标由简单步态生成；身体用 WASD 在平地上移动。右侧可开关 **IK 链** 黄色折线，观察每帧迭代如何拉近足尖与目标点。

---

### 逆运动学（IK）问题

已知开链骨骼：根关节 $\mathbf{p}_0$（固定在身体上）与 $n-1$ 段定长连杆 $| \mathbf{p}_{i+1}-\mathbf{p}_i | = L_i$，求关节角使末端 $\mathbf{p}_{n-1}$ 到达目标 $\mathbf{t}$。

与正运动学（FK）$\mathbf{p}_i = f(\theta_1,\ldots,\theta_{n-1})$ 相反，IK 一般**无闭式解**（$n>2$ 时），需迭代数值法。

本 demo 每条腿：$n=4$ 个关节（髋 → 膝 → 踝 → 趾尖），3 段骨长 $L_0,L_1,L_2$。

---

### CCD 算法原理

**思想**：从末端向根，逐个关节“转向”末端，使末端方向对准目标；再从前向后**恢复骨长**；重复直至收敛。

对关节 $i$（$i = n-2,\ldots,0$）：

1. 记枢轴 $\mathbf{p}_i$，末端 $\mathbf{p}_{n-1}$，目标 $\mathbf{t}$。
2. 单位向量 $\mathbf{u} = (\mathbf{p}_{n-1}-\mathbf{p}_i)/\|\cdot\|$，$\mathbf{v} = (\mathbf{t}-\mathbf{p}_i)/\|\cdot\|$。
3. 求最小旋转 $\mathbf{R}$ 使 $\mathbf{R}\mathbf{u}=\mathbf{v}$（轴角 / 四元数 `setFromUnitVectors`）。
4. 对 $j=i+1,\ldots,n-1$：$\mathbf{p}_j \leftarrow \mathbf{p}_i + \mathbf{R}(\mathbf{p}_j-\mathbf{p}_i)$。
5. **前向约束**：固定 $\mathbf{p}_0$，依次 $\mathbf{p}_{i+1} = \mathbf{p}_i + L_i \cdot \mathrm{normalize}(\mathbf{p}_{i+1}-\mathbf{p}_i)$。

```
while 未收敛 and 迭代 < maxIter:
  for i = n-2 .. 0:
      旋转关节 i，使末端指向目标
  for i = 0 .. n-2:
      恢复骨长 L[i]
```

**优点**：实现简单、每关节 $O(n)$、无需雅可比矩阵；适合实时角色/机械臂。

**缺点**：可能陷入局部极小；长链或大角度弯曲时收敛慢。本 demo 对每关节加 **最大转角** `maxAngles[i]` 避免腿反折。

---

### 与 FABRIK 的对比

| 方法 | 机制 | 特点 |
|:---|:---|:---|
| **CCD** | 逐关节旋转，再拉直骨长 | 实现极简，本 demo 采用 |
| **FABRIK** | 先向目标“伸手”，再向根“拉回”保持骨长 | 大弯曲更稳，无三角函数 |
| **雅可比转置 / IK** | $\Delta\theta = J^T (\mathbf{t}-\mathbf{p}_{end})$ | 通用，需求导与步长控制 |

---

### 本 demo 中的运动管线

```
身体位姿 (位置 + yaw)
    ↓
每条腿：髋附着点（体坐标 → 世界坐标）
    ↓
步态相位 → 足端目标 t（摆动相抬脚 + 迈步偏移）
    ↓
CCD(关节, 骨长, t) → 更新 4 个关节世界坐标
    ↓
圆柱段 + 关节球体对齐骨骼
```

**步态**：8 条腿相位错开 $0.125$；`cycle < 0.45` 为摆动相（正弦抬脚），否则为支撑相；移动时沿身体前方加 `stride` 偏移，形成交替迈步。

**场景**：草地平面、网格、石块与树桩，阴影 + 雾效；相机 `OrbitControls` 可环绕，移动时目标点跟随蜘蛛。

---

### 操作说明

| 按键 | 功能 |
|:---|:---|
| **W A S D** | 前后左右移动 |
| **Q / E** | 身体原地转向 |
| **速度** | 移动与步频 |
| **IK 迭代** | CCD 每帧循环次数（越大越贴目标，略耗性能） |
| **显示 IK 链** | 黄色折线：髋→趾尖 |
| **重置位置** | 回到场景中心 |

---

### 代码入口

求解器函数 `solveCCD(joints, boneLengths, target, iterations, maxAngles)` 在 `ik-spider.html` 脚本顶部，与上述伪代码一一对应，便于对照阅读。

---

### 参考

- Wang, L.-C. T., & Chen, C.-C. (1991). *A Combined Optimization Method for Solving the Inverse Kinematics Problem of Mechanical Manipulators.* IEEE Trans. RA.
- Aristidou, A., & Lasenby, J. (2011). *FABRIK: A fast, iterative solver for the inverse kinematics problem.* Graphical Models.
- Bouaziz, S., et al. (2012). *Shape-Up* — 局部投影与全局线性步（另一套约束求解范式，可与 IK 对比）。
