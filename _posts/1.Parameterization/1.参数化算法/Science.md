 ## EPICS

EPICS (Experimental Physics and Industrial Control System) 

EPICS的典型应用是 Gemini激光控制系统

- **Central Laser Facility**（CLF）
   隶属于英国**科学技术设施委员会**（STFC），位于**卢瑟福·阿普尔顿实验室**（RAL），是英国国家级激光研究基础设施，为学术界和工业界提供多种先进激光平台。

- **Gemini 激光系统**

  - 是 CLF 运行的一台**超高强度、双光束皮秒钛宝石**（Ti:Sapphire）。

  - **峰值功率**：高达 **~2 × 0.5 PW**（即每束 0.5 拍瓦，共两束），聚焦强度可达 1021 W/cm21021 W/cm2 以上。

  - **用途**：用于**激光等离子体物理、电子/质子加速、实验室天体物理、高能量密度科学**等前沿研究

- **Gemini 激光控制系统**

  - 监控和控制激光器数千个硬件参数（如镜片位置、泵浦能量、真空状态、诊断设备）

  - 实现**实验自动化**（自动对准、能量优化、数据采集同步）

  - 保障**操作安全**（联锁、权限管理、故障诊断）

  - 提供**用户友好的操作界面**（供科学家远程或现场运行实验）

    

![image-20251014140507961](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251014140507961.png)

EPICS包含两个主要部分IOC以及OPI

在EPICS（Experimental Physics and Industrial Control System）架构中，**IOC（Input/Output Controller）** 和 **OPI（Operator Interface）** 是两个核心组件，共同构成分布式控制系统的骨架。它们通过**Channel Access（CA）协议**实现通信（**在分布式控制系统中实时传输过程变量（Process Variable, PV）数据**），形成客户端-服务器模型。



### CA协议 vs. 传统工业协议（对比优势）

| 协议                    | 适用场景     | CA协议优势                                 |
| ----------------------- | ------------ | ------------------------------------------ |
| **Modbus**              | 工厂流水线   | 无实时性保障，数据量小（<100 PV）          |
| **OPC UA**              | 工业自动化   | 通用但缺乏科研级数据模型（如自定义PV结构） |
| **TCP/IP + 自定义协议** | 小型系统     | 需重复开发，难以标准化                     |
| **✅ CA协议**            | 大型科学设施 | **专为高可靠性、高并发控制设计**           |



![image-20251014193018582](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251014193018582.png)

### **Kafka 在 EPICS 中的核心作用**

1. **数据缓冲与异步处理**

   - **高吞吐量数据管道**：EPICS 的 IOC（Input/Output Controller）生成实时数据（如设备状态、传感器读数），通过 Kafka 作为消息队列缓冲数据，避免数据洪峰冲击后端系统。
   - **异步解耦**：生产者（IOC）将数据发布至 Kafka Topic，消费者（数据分析服务、数据库、可视化界面）按需订阅，实现 IOC 与数据处理模块的解耦，提升系统弹性。

2. **跨系统集成与协议转换**

   - 异构系统桥接

     ：Kafka 作为“数据总线”，连接 EPICS 与其他系统（如 Hadoop、Spark、时序数据库）。例如：

     - EPICS PVs（过程变量） → Kafka Producer → 实时流处理（Flink/Spark） → 可视化面板。
     - Kafka 支持多种协议适配器（如 MQTT、HTTP），可将非 EPICS 设备数据接入 EPICS 控制网络。

3. **实验数据流水线**

   - 同步辐射应用案例

     ：

     - **数据采集层**：IOC 从探测器（如 SIS3820 定标器）读取高频数据 → 发送至 Kafka Topic（如 `beamline_raw_data`）。
     - **处理层**：流处理引擎消费 Kafka 数据，进行实时降噪、校准或特征提取。
     - **存储层**：处理结果写入 HDFS 或时序数据库（如 InfluxDB），供离线分析。

4. **容灾与数据持久化**

   - Kafka 的持久化机制（日志保留策略）确保实验数据不丢失，即使消费者服务宕机也可回溯数据。
   - 支持多副本机制，保障高可用性（如上海光源 BL07U 光束线数据备份）

NTP（Network Time Protocol）在EPICS（Experimental Physics and Industrial Control System）中的应用主要体现在为分布式控制系统提供高精度时间同步，确保实验设备、数据采集节点和操作界面的时间一致性。以下是其核心应用方向及技术实现

## BlueSky


 它通过 **Ophyd 与 EPICS 深度集成**，将 EPICS 强大的设备控制能力与 Python 的灵活性、可编程性结合起来，正在成为新一代大科学装置（尤其是光源、中子源）的标准实验平台。

![image-20251014104426948](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251014104426948.png)

**BlueSky** 是一个开源项目，由**美国能源部（DOE）下属多个国家实验室的科学家和软件工程师共同开发和维护**，并非由单一公司或个人主导。以下是其主要开发者和贡献机构的概况：

| 机构                                                         | 贡献重点                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Brookhaven National Laboratory (BNL)** （布鲁克海文国家实验室） | - BlueSky 最初发起者 - NSLS-II 同步辐射光源的主力开发团队 - 核心架构、RunEngine、Databroker 设计 |
| **Argonne National Laboratory (ANL)** （阿贡国家实验室）     | - Ophyd 硬件抽象层的主要开发者 - APS（先进光子源）线站集成 - Bluesky-queueserver、自动化实验 |
| **Lawrence Berkeley National Laboratory (LBNL)** （劳伦斯伯克利国家实验室） | - 数据管理、与科学计算生态（如 Dask、SciPy）集成 - ALS（先进光源）应用 |
| **SLAC National Accelerator Laboratory** （SLAC 国家加速器实验室） | - 在 LCLS 自由电子激光装置中应用 BlueSky - 高速数据采集与实时分析集成 |

**代码托管**：https://github.com/bluesky 

**许可证**：BSD 3-Clause（宽松开源，允许商业使用）

![image-20251014105159285](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251014105159285.png)

## 核心问题自检清单

| 问题                                                         | 若答案为“是”，则 BlueSky 更适用 |
| ------------------------------------------------------------ | ------------------------------- |
| 1. 实验是否需要**复杂、可编程的扫描逻辑**（如多维扫描、条件分支、自适应测量）？ | ✅                               |
| 2. 是否希望**科学家能自主编写/修改实验流程**，而不依赖控制组？ | ✅                               |
| 3. 装置是否已使用 **EPICS**（或可接入标准控制协议）？        | ✅（非必须，但极大降低集成成本） |
| 4. 是否重视**实验数据的完整性、可追溯性和 FAIR 原则**（可查找、可访问、可互操作、可重用）？ | ✅                               |
| 5. 是否有**Python 编程能力**的用户或支持团队？               | ✅                               |
| 6. 是否计划开展**高通量、自动化或 AI 驱动的自主实验**？      | ✅                               |

