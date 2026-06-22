## Draco 几何压缩

Draco 是 Google 开源的高效 3D 几何压缩库，专为网格和点云数据的传输与存储优化设计。它将模型文件体积压缩至 **原来的 5%~20%**，解码速度极快，是 Web 3D 应用的标准压缩方案。

### 核心原理

Draco 的核心思路是**对网格数据进行量化和熵编码**，而非简单的 zlib/gzip 字节流压缩——后者对浮点几何数据几乎没有效果。

#### 1. 顶点位置量化（Position Quantization）

顶点坐标通常是 32 位浮点数（每顶点 12 字节）。Draco 首先计算模型的包围盒，然后将顶点归一化到包围盒内的整数网格：

$$v_q = \left\lfloor \frac{v - v_{\min}}{v_{\max} - v_{\min}} \cdot (2^b - 1) + 0.5 \right\rfloor$$

其中 $b$ 为量化位深（通常 8~14 位），$v_q$ 为整数坐标。

> 这样每个顶点坐标从 96 位压缩到 $3b$ 位（如 b=10 即为 30 位），体积缩小 3~10 倍。

解码时反量化恢复近似浮点位置：

$$v' = v_{\min} + \frac{v_q}{2^b - 1} \cdot (v_{\max} - v_{\min})$$

#### 2. 边断裂器（Edgebreaker）连通性压缩

三角面片的顶点索引占用大量空间。Draco 使用 Edgebreaker 算法，将网格拓扑编码为 CLERS 符号序列：

| 符号 | 含义 |
|:---|:---|
| **C** | 新顶点，创建三角形 |
| **L** | 左邻接，闭合左侧 |
| **R** | 右邻接，闭合右侧 |
| **E** | 边界 |
| **S** | 分裂，创建新边界 |

每个三角形只需 1~2 位编码，远小于原始索引的 96 位/面。

#### 3. 平行四边形预测（Parallelogram Prediction）

相邻顶点通常位于近似平行四边形顶点上。Draco 利用这一规律对量化后的顶点残差编码：

$$\hat{v}_k = v_{k-1} + v_{k-2} - v_{k-3}$$

仅存储预测残差 $\Delta = v_k - \hat{v}_k$，残差很小（通常 0~3），熵编码效率极高。

#### 4. 熵编码（Entropy Coding）

量化后的整数序列和残差通过 **rANS**（范围非对称数字系统）进行熵编码。rANS 兼具算术编码的压缩率和 Huffman 编码的速度。

### Draco 在 GLTF/GLB 中的应用

GLTF 2.0 规范原生支持 Draco 压缩扩展 `KHR_draco_mesh_compression`。压缩后的 GLB 文件中：

- **bufferView** 指向压缩的 Draco 数据
- **extension** 声明中记录量化参数
- **accessor** 信息保留原始语义（位置/法线/UV）

Three.js 中解码仅需一行：

```javascript
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');
gltfLoader.setDRACOLoader(dracoLoader);
```

### 压缩效果参考

| 模型 | 原始大小 | Draco 压缩后 | 压缩率 |
|:---|:---|:---|:---|
| Littlest Tokyo | ~40 MB (OBJ) | **3.9 MB** (GLB) | **10%** |
| 典型建筑场景 | 25 MB | 2.5 MB | 10% |
| 角色模型 | 8 MB | 1.2 MB | 15% |

### 参考

- Galligan et al. (2018). "Google Draco: 3D Data Compression." Google.
- `KHR_draco_mesh_compression` GLTF Extension Specification.
- Edgebreaker: Rossignac (1999). "Edgebreaker: Connectivity compression for triangle meshes." *IEEE TVCG*.
