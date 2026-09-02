# SDF 高亏格曲面 → Marching Cubes → 三角网格

用**有符号距离场（Signed Distance Field, SDF）**隐式表达高亏格（genus ≥ 1）闭合曲面，
并通过**手写 Marching Cubes** 提取等值面，输出为 OBJ 三角网格。

仅依赖 `numpy`，不引入 `skimage` / `trimesh` 等库。算法核心（SDF 构造、MC 查找表、
线性插值、OBJ 写出）全部自实现。

## 目录内容

| 文件 | 说明 |
|---|---|
| `sdf_to_mesh.py` | 主程序：SDF 定义 + Marching Cubes + OBJ 输出 + CLI |
| `README.md` | 本文档 |

## 1. 技术背景

### 1.1 什么是 SDF

SDF 是一个标量场函数 `d = f(p)`，输入三维点 `p`，返回该点到隐式曲面的带符号距离：

- `d < 0`：点在曲面**内部**；
- `d = 0`：点在**曲面**上（零等值面 / iso-surface）；
- `d > 0`：点在**外部**。

曲面本身不需要参数化，只需要一个能求值的场函数即可，非常适合做 CSG 布尔运算与
无拓扑信息约束的形状表达。

### 1.2 什么是亏格（genus）

亏格是闭合曲面上**贯通孔**的数量。球为 genus 0，环面（甜甜圈）为 genus 1，
多环面连通体为 genus N。它与**欧拉示性数** `χ` 的关系为：

```
χ = V − E + F          (V 顶点数, E 边数, F 面数)
genus = (2 − χ) / 2
```

因此 genus ≥ 1 即「高亏格」。

### 1.3 为什么要用 Marching Cubes

隐式曲面（SDF 的零等值面）无法直接渲染/打印，需要转成显式三角网格。
Marching Cubes（Lorensen & Cline, 1987）把空间切成体素网格，逐个立方体按
「8 个角点相对等值面的正负号组合」查表生成三角形，是隐式曲面网格化的经典算法。

## 2. 算法实现

### 2.1 环面 SDF

```python
def sd_torus(p, R, r):
    q = np.sqrt(p[..., 0] ** 2 + p[..., 2] ** 2) - R
    return np.sqrt(q * q + p[..., 1] ** 2) - r
```

- `R`：环半径（中心到管道轴线）；
- `r`：管道截面半径；
- 环面轴线沿 **y** 轴，孔沿 y 方向贯通。

### 2.2 高亏格构造：genus 个环面沿 z 轴相交堆叠

单个环面只有 genus = 1。要得到 genus = N，把 N 个环面沿 z 轴等距堆叠，
并保证**相邻管道相交**，再取并集融合为单一连通体：

```python
d = 1.5 * r                       # 相邻中心距 < 2r，管道必然相交
z0 = -(genus - 1) * d / 2.0       # 整体居中于原点
centers = [z0 + i * d for i in range(genus)]
```

每个环面贡献一个沿 z 方向的贯通孔，故连通体的亏格 = N。

### 2.3 两种并集模式

| 模式 | CLI | 并集算子 | 效果 |
|---|---|---|---|
| A: CSG 并集 | `--mode torus` | `min(d1, d2, ...)` (hard min) | 相交处有硬接缝，SDF 分段连续 |
| B: 光滑并集 | `--mode analytic` | 多项式 smooth min | 相交处平滑圆润过渡，处处解析 |

smooth min（Polynomial smooth min, IQ）：

```python
def _smooth_min(a, b, k=0.15):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b + h * (a - b) - k * h * (1.0 - h)
```

- `k` 控制过渡带宽：`k → 0` 退化为 hard min；`k` 过大则并集会膨胀、零等值面外扩。

### 2.4 Marching Cubes

实现要点（`marching_cubes()`，非共享顶点方案，Lorensen 标准三角表）：

1. 在 `(N+1)^3` 的体素网格上采样 SDF 场值；
2. 遍历每个立方体，取 8 个角点场值，与等值面 `iso=0.0` 比较得到 8 位 case 索引；
3. case 为 0 或 255（立方体完全同侧）直接跳过；
4. 对 12 条边中两端异号的边，用**线性插值**求交点：
   ```
   t = (iso − va) / (vb − va)
   ```
5. 按 256 项 `_TRI_TABLE` 查找该 case 应生成的三角形（每项以 `-1` 结尾）；
6. 收集顶点与三角形索引，写出 OBJ。

### 2.5 OBJ 输出

OBJ 格式：`v x y z` 定义顶点（1 起始），`f i j k` 定义三角面（索引从 1 开始）。

## 3. 使用方法

```
usage: sdf_to_mesh.py [--mode {torus,analytic}] [--genus N]
                      [--res N] [--bounds B] [--out FILE]
```

| 参数 | 默认 | 说明 |
|---|---|---|
| `--mode` | `torus` | `torus`(CSG 并集) / `analytic`(光滑并集) |
| `--genus` | `3` | 亏格数（正整数） |
| `--res` | `128` | 体素分辨率 N（内存 ~ O(N³)） |
| `--bounds` | 自动 | 包围盒半边长；默认按 genus 自动适配 |
| `--out` | `output.obj` | 输出 OBJ 路径 |

示例：

```bash
python3 sdf_to_mesh.py --mode torus    --genus 3 --res 128 --out genus3_torus.obj
python3 sdf_to_mesh.py --mode analytic --genus 3 --res 128 --out genus3_analytic.obj
python3 sdf_to_mesh.py --mode torus    --genus 5 --res 128 --out genus5_torus.obj
python3 sdf_to_mesh.py --mode analytic --genus 5 --res 128 --out genus5_analytic.obj
```

包围盒自动适配规则（`R=0.6, r=0.3`）：

```python
z_extent     = (genus - 1) * 1.5 * r + r   # 沿 z 轴总延伸
radial_extent = R + r                       # 径向总延伸
b = max(z_extent, radial_extent) + 0.4      # 半边长，留出余量
```

## 4. 生成结果（res=128）

| 文件 | 模式 | 顶点数 | 三角形数 |
|---|---|---|---|
| `genus3_torus.obj` | torus | 139,392 | 46,464 |
| `genus3_analytic.obj` | analytic | 137,736 | 45,912 |
| `genus5_torus.obj` | torus | 75,816 | 25,272 |
| `genus5_analytic.obj` | analytic | 75,072 | 25,024 |

> 注：当前目录只归档脚本；OBJ 可通过上面命令重新生成，
> 或用任意支持 OBJ 的查看器（Blender / MeshLab / Three.js 页面）打开。

## 5. 拓扑验证方法（参考）

> 提示：脚本运行结果直接用肉眼观察即可，以下为需要自动验证时的标准做法。

MC 直接输出的网格是**非共享顶点**结构（每个三角形独占 3 个顶点，`V = 3F`），
此时直接套欧拉公式没有意义。必须**先按坐标焊接顶点**（按空间位置去重）再统计：

```python
χ     = V - E + F
genus = (2 - χ) / 2
```

对于 genus=N 的连通曲面，应有 `χ = 2 − 2N`。

## 6. 实现要点与踩坑记录

| 问题 | 现象 | 解法 |
|---|---|---|
| **包围盒截断** | 曲面超出包围盒，被裁出开放边界，欧拉特征异常（genus 算出负值） | 按 genus 自动计算 bounds，留 0.4 余量，保证曲面完整闭合 |
| **smooth min 参数过大** | 并集过度膨胀，场值全场为负，零等值面消失 | `k = 0.15`（约 r/2），接近 hard min 又不失光滑过渡 |
| **inf 参与 smooth min** | 用 `inf` 初始化累积距离，smooth min 出现 NaN | 首个分量直接赋值，之后才做 smooth min（`d = td if d is None else ...`） |
| **cos 调制径向半径** | 形变曲面实为 genus=1，不构成高亏格 | 弃用，改为多环面相交并集 |
| **非共享顶点** | `V = 3F`，欧拉公式直接算无意义 | 先按坐标焊接顶点再算 χ |

## 7. 局限与改进方向

- **内存/时间**：`res` 三三次方增长，纯 Python 三重循环的 MC 在大分辨率下偏慢；
  可用 `numba` 或按层并行加速，或把体素遍历向量化。
- **拓扑二义性**：标准 MC 三角表在某些配置下有孔洞（ambiguous cases）；
  可换用 Marching Tetrahedra 或补充 MT 表解决。
- **非流形**：输出未做流形修复与法向一致化；OBJ 面朝向由采样顺序决定，
  若需进一步渲染/打印建议用 MeshLab 等工具后处理。
- **顶点数膨胀**：可把 MC 改为共享顶点方案（用 `(voxel, edge)` 哈希去重），
  顶点数可减少约 1/3。
- **其他高亏格曲面**：`make_sdf()` 是插件式入口，可继续添加
  双环面、3-环面平铺、三角剖分曲面（Schwarz P / Gyroid）等解析 SDF。

## 8. 参考

- Lorensen, W. E., & Cline, H. E. (1987). *Marching Cubes: A high resolution 3D surface construction algorithm.* SIGGRAPH.
- Inigo Quilez, *[distance functions](https://iquilezles.org/articles/distfunctions/)* 与 *smooth minimum* 笔记。
- 欧拉公式：`V − E + F = χ`，闭合曲面 `genus = (2 − χ) / 2`。
