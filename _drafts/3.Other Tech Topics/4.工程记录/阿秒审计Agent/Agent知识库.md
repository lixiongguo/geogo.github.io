# Agent 知识库：理解与实践「LangGraph + LlamaIndex 采购审计 Agentic RAG」需要学什么

> 本笔记配套两篇文章：
> - `目标架构总体需求.md`：用 LangGraph + LlamaIndex 构建采购审计 Agentic RAG 系统的设计方案（7 个 Agent、AuditState、SQL/RAG/Excel 双通道、PDF 流水线）。
> - `当前架构与目标架构的差距分析.md`：对现有 FastAPI + 自研 AgentRunner + MCP 项目做只读审查，给出「当前实现 vs 目标架构」的差距表，并按 P0/P1/P2 + 6 个阶段拆出升级路线。
>
> 目标：把读懂这两篇、并真正动手实践所需的知识点梳理成学习地图，附公开可查资料。

---

## 0. 先建立全局认知（为什么需要这些知识）

这套系统的本质是：**用 LLM 做推理与规划，用 Agent 框架做状态机与流程编排，用 RAG/向量库做知识检索，用关系库/对象存储做事实与证据沉淀，最后产出可追溯的审计报告。**

要实践它，需要同时掌握 6 条知识线：

| 知识线 | 在本系统中的作用 | 缺它会导致 |
| --- | --- | --- |
| ① LLM / Agent 基础 | 理解 Tool Calling、规划、推理 | 看不懂「Decision Agent 为什么能动态选动作」 |
| ② LangGraph | State 驱动、节点路由、checkpoint 恢复 | 无法落地「可暂停/恢复的动态图」 |
| ③ LlamaIndex + RAG | 文档→Node→索引→检索 | 无法落地「LlamaIndex 层」与混合检索 |
| ④ 向量与检索工程 | Embedding、BM25+向量+RRF+Reranker | 检索质量差、精确编号匹配失效 |
| ⑤ 存储与数据 | MySQL / ES / Redis / MinIO | 证据无账本、无法恢复、版本混乱 |
| ⑥ 文档解析 | MinerU / Excel / Word | 原文证据无法结构化进索引 |

---

## 0.5 技术组件全景图（系统由哪些部分构成）

> 纠正常见误解：**LangGraph / LlamaIndex / FastAPI / MCP / MinerU 这 5 个只是核心框架/协议/工具，并非系统全部。** 要跑通还需存储四件套（MySQL/ES/Redis/MinIO）和三个模型（LLM/Embedding/Reranker），以及前端与解析器。另外注意区分「基础设施组件」与「Agent 真正调用的 7 个业务工具」。

### 分层全景

| 层 | 组件 | 类别 | 在系统中的作用 | 对应文章位置 |
| --- | --- | --- | --- | --- |
| Agent 编排 | **LangGraph** | 框架 | 状态机、节点路由、checkpoint 恢复、Human-in-the-loop | 目标架构 §4、差距分析 §二.2 |
| 知识检索 | **LlamaIndex** | 框架 | 文档接入、Node 切分、Embedding、Retriever、RAG | 目标架构 §7、差距分析 §二.3 |
| 后端服务 | **FastAPI** | 框架 | 网关、依赖装配、会话主链、SSE、后台任务 | 差距分析 §一.1、§二.4 |
| 工具协议 | **MCP** | 协议 | 把后端能力暴露为标准化工具，Agent 远程调用 | 差距分析 §一.1、§二.4（5.3） |
| 文档解析 | **MinerU**（+ PP-StructureV3） | 工具/服务 | PDF→结构化 Markdown/JSON（OCR/版面/表格） | 目标架构 §11、差距分析 §二.3 |
| 模型 | LLM（本地 Qwen，OpenAI 兼容接口） | 模型 | 推理、规划、生成 | 目标架构 §7.2.4 |
| 模型 | Embedding（BGE-M3） | 模型 | 文本向量化 | 目标架构 §7.2.3、差距分析 §二.3 |
| 模型 | Reranker | 模型 | 召回结果重排 | 差距分析 §一.3、P1-1 |
| 存储 | MySQL（+ SQLAlchemy） | 存储 | 采购业务数据、知识库、会话、报告 | 目标架构 §9、差距分析 §二.4 |
| 存储 | Elasticsearch | 存储 | 文档向量检索 + Schema 语义检索 | 目标架构 §9、差距分析 §二.4 |
| 存储 | Redis | 存储 | checkpoint、会话缓存（需 RedisJSON+RediSearch） | 目标架构 §9、差距分析 §二.4 |
| 存储 | MinIO | 存储 | 原文件、解析产物、证据快照 | 目标架构 §9、§11 |
| 解析 | Excel / Word 解析器 | 工具 | 多 Sheet、合并单元格、字段类型识别 | 差距分析 §一.3 |
| 前端 | React/TS（ChatPage 等） | 前端 | 聊天界面、SSE 事件渲染、任务恢复 | 差距分析 P0-6 |

### 两个关键区分

1. **基础设施组件 ≠ Agent 的工具**。上述组件是「地基」；Agent 真正调用的业务工具是 **7 个函数**（目标架构 §12）：
   `query_purchase_database`、`retrieve_documents`、`read_original_document`、`analyze_purchase_excel`、`analyze_price_reasonableness`、`generate_audit_report`、`retrieve_database_schema`。MCP 只是把这些工具「暴露/派发」出去的协议。
2. **MinerU 不与 LangGraph/LlamaIndex 平级**。它是被 FastAPI 调起的独立解析 Worker，产物再喂给 LlamaIndex，不参与 Agent 决策。

### 一句话记住

> 两大主线（LangGraph + LlamaIndex）+ 后端（FastAPI）+ 工具协议（MCP）+ 解析（MinerU）+ 存储四件套（MySQL/ES/Redis/MinIO）+ 三模型（LLM/Embedding/Reranker）+ 前端，才构成完整系统。

---

## 1. 基础认知：LLM 与 Agent

理解方案的「核心思想」前，先补齐以下概念。

### 1.1 必学概念

- **LLM / 大语言模型**：理解 prompt、上下文窗口、token。
- **Tool Calling / Function Calling**：模型输出结构化 `tool_calls`（名称+参数 JSON），由程序执行。这是全文 `query_purchase_database` 等工具的运行基础。
- **Agent（智能体）**：能感知→决策→调用工具→观察结果→再决策的循环体。本文的 `AgentRunner` 与 LangGraph 图都是它的实现。
- **RAG（检索增强生成）**：先检索相关知识，再让 LLM 基于证据回答，降低幻觉。
- **Agentic RAG**：把 RAG 作为 Agent 的一个工具，由 Agent 决定何时检索、检索什么。

### 1.2 推荐公开资料

- **Anthropic《Building Effective Agents》**（必读，建立 Agent 设计直觉）：https://www.anthropic.com/research/building-effective-agents
- **Hugging Face Agents Course**（免费、含 LangGraph/LlamaIndex/smolagents 实战，有中文版）：
  - 中文：https://hugging-face.cn/learn/agents-course/unit0/introduction
  - 英文：https://huggingface.co/learn/agents-course/unit0/introduction
- **RAG 入门（LlamaIndex 官方）**：https://docs.llamaindex.org.cn/en/stable/understanding/rag/

---

## 2. 核心框架一：LangGraph（State 与流程编排）

目标架构里 LangGraph 负责「流程控制、State 管理、动态规划」，是当前项目最大差距（自研 `AgentRunner` → 显式图）。

### 2.1 必学概念

- **StateGraph / Graph API**：用节点（node）和边（edge）定义 Agent 流程。文中 `Supervisor → Decision → 执行节点 → 更新 State → Decision` 就是一张图。
- **State（状态）**：贯穿全图的共享数据，文中 `AuditState`（question/goal/stage/evidence/missing_information/...）。需理解「状态合并规则（reducer）」避免节点互相覆盖。
- **Checkpointer / Persistence（持久化）**：每一步把状态存为 checkpoint，使任务可暂停、恢复、重放。这是差距分析中「运行过程不能恢复」的解法。
- **Human-in-the-loop**：缺信息需用户补充时暂停（对应 `missing_information` + `needs_clarification`）。
- **终止条件**：用 `finished` + `status` + `stop_reason` 区分「正常完成 / 证据不足 / 等待补充 / 执行失败」，而不是单纯靠轮次预算。

> 关键区分（差距分析反复强调）：**动态规划由 Decision Agent 的 LLM+规则完成，LangGraph 负责承载与执行这一机制。**

### 2.2 推荐公开资料

- **LangGraph 概览（官方，先读）**：https://docs.langchain.com/oss/python/langgraph/overview
- **Quickstart 快速入门（官方，含 Graph API 计算器示例）**：https://docs.langchain.com/oss/python/langgraph/quickstart
- **持久化 Persistence（官方）**：https://docs.langchain.com/oss/python/langgraph/persistence
- **Checkpointers（官方）**：https://docs.langchain.com/oss/python/langgraph/checkpointers
- **中文文档**：https://docs.langchain.org.cn/oss/python/langgraph/overview 、持久化 https://docs.langchain.org.cn/oss/python/langgraph/persistence
- **中文实战：LangGraph 如何通过 Checkpoint 实现持久化**：https://juejin.cn/post/7573597479981121572

---

## 3. 核心框架二：LlamaIndex（RAG 索引与检索）

目标架构里 LlamaIndex 负责文档接入、Node 切分、Embedding、Retriever。关键点：**不要推翻现有解析器，把 MinerU 结构化结果「接入」LlamaIndex 即可**。

### 3.1 必学概念

- **Document / Node**：Document 是整篇文档，Node 是切分后的知识单元（保留页码、章节、坐标等 metadata）。
- **IngestionPipeline（摄取管道）**：组织「转换→Embedding→入库」，并提供转换缓存。
- **VectorStoreIndex / VectorStore**：索引与向量库的解耦；本文用 `ElasticsearchStore`。
- **Retriever / QueryEngine / Reranker**：检索器 + 查询引擎 + 重排。
- **Metadata Filter**：用来源版本、业务实体、有效期做证据过滤（差距分析指出当前 metadata 缺「业务实体/来源版本/有效期」）。

### 3.2 推荐公开资料

- **LlamaIndex 官方文档（英文）**：https://developers.llamaindex.ai/python/framework/module_guides/indexing/vector_store_index/
- **LlamaIndex 官方文档（中文镜像）**：https://developers.llamaindex.org.cn/python/framework/module_guides/indexing/vector_store_index/
- **从零构建 RAG（底层原理）**：https://docs.llamaindex.org.cn/en/stable/optimizing/building_rag_from_scratch/
- **Ingestion Pipeline（官方）**：https://developers.llamaindex.ai/python/framework/module_guides/loading/ingestion_pipeline/
- **ElasticsearchStore（官方）**：https://developers.llamaindex.ai/python/framework-api-reference/storage/vector_store/elasticsearch/
- **IBM LlamaIndex RAG 实战（PDF 解析示例）**：https://www.ibm.com/think/tutorials/llamaindex-rag
- **LlamaIndex × Elasticsearch 集成（Elastic 官方）**：https://www.elastic.co/search-labs/integrations/llama-index

### 3.3 LlamaIndex 在本项目中的具体职责（结合两篇文章）

LlamaIndex 在本系统里是**「知识检索 / 数据框架」层**：处在私有数据与 LLM 之间，负责把采购文档接进来、切好、向量化、建索引，供 Agent 检索。它与 LangGraph 互补——**LangGraph 管流程怎么走，LlamaIndex 管知识从哪来**。

**通用四步流水线（它的本质）：**
1. **数据接入 Loading**：各种格式 → 统一 `Document`（靠 Loader/Connector）。
2. **切分与索引 Indexing**：`Document` 切成 `Node`（知识单元，带页码/章节/坐标等 metadata），Embedding 后建索引。
3. **检索 Retrieval**：`Retriever` 按查询召回相关 Node，可叠 `Reranker` 重排。
4. **查询生成 Query**：`QueryEngine` 把召回内容组织成上下文交给 LLM。

**在本项目的具体用途：**
- 目标架构 §7 明确 LlamaIndex 负责：文档接入、Node 切分、Embedding、Retriever、RAG 查询。
- 接 ES 作向量库（`ElasticsearchStore`）、用 BGE-M3 做 Embedding、用 OpenAI 兼容接口接本地 Qwen（`OpenAILike`）——见 §3.2 安装表。
- `IngestionPipeline` 组织「转换 → Embedding → 入库」并提供转换缓存。
- **关键注意点（差距分析）**：不要重搭 OCR，应把现有 MinerU/PP-Structure 的结构化输出「适配」成 LlamaIndex 的 `Document/Node`；旧 ES 索引不能只靠换连接类迁移，需逐项适配 Node 序列化、metadata、过滤方式（见 §3.2 ElasticsearchStore 链接）。

---

## 4. 检索与向量工程（RAG 质量核心）

差距分析把「检索质量」「向量一致性」「精确编号匹配」列为高风险项，需掌握以下。

### 4.1 必学概念

- **Embedding 模型**：把文本变成向量。本文用 **BGE-M3**（多语言、支持稠密/稀疏/多向量，8192 长文本）。
  - 风险点：Embedding 降级（hashing 向量）会污染语义空间 → 必须「正式索引只写同模型同版本的向量」。
- **混合检索 Hybrid Search**：BM25（关键词/精确编号）+ 向量（语义）双路召回。
- **RRF（Reciprocal Rank Fusion）**：融合两路排名的算法。
- **Reranker（重排）**：Cross-Encoder 对候选重排序，提升 Top-K 精度。
- **ES 向量检索 + RedisJSON/RediSearch**：ES 做向量召回；Redis 做 checkpoint 需要 RedisJSON + RediSearch 模块（差距分析明确提示）。

### 4.2 推荐公开资料

- **BGE-M3 介绍与部署**：
  - BAAI 官方仓库：https://github.com/FlagOpen/FlagEmbedding （搜索 BGE-M3）
  - 中文实战：https://www.cnblogs.com/xiaoqi/p/18143552/bge-m3
  - 部署全流程：https://devpress.csdn.net/v1/article/detail/157483013
- **混合检索 RRF 深度解析（含代码）**：https://www.smallyoung.cn/docs/028-RAG%E6%B7%B7%E5%90%88%E6%A3%A2%E4%B8%8ERRF%E7%AE%97%E6%B3%95%E6%B7%B1%E5%BA%A6%E8%A7%A3%E6%9E%90
- **RAG 混合检索生产实战（BM25+向量+Reranker+Query改写）**：https://walterwang0x01.github.io/portfolio/posts/rag-hybrid-retrieval-production/
- **RAG 完整教程（混合检索与重排序章节）**：https://vivy-yi.github.io/rag-tutorial/02-%E6%A0%B8%E5%BF%83%E4%BC%98%E5%8C%96/09-%E6%B7%B7%E5%90%88%E6%A3%A2%E4%B8%8E%E9%87%8D%E6%8E%92%E5%BA%8F/
- **10 分钟本地 RAG（向量+BM25+RRF）**：https://cloud.tencent.com/developer/article/2654879
- **Elasticsearch 混合检索（LlamaIndex + ES）**：https://elasticstack.blog.csdn.net/article/details/145942780

---

## 5. Agent 工程能力：Tool Calling 与 MCP

当前项目已有 MCP 拆分与 Tool Calling，目标架构只是「按节点授权、统一执行记录、统一契约」。

### 5.1 必学概念

- **Tool Calling**：模型生成 `tool_calls`，程序执行并返回结果。本文 `@tool` 装饰器 + JSON Schema 参数。
- **MCP（Model Context Protocol）**：把工具以标准协议暴露给 LLM 客户端，支持远程工具发现与调用。文中 `MCPClientManager.discover_tools()`、`as_openai_tool()`。
- **工具契约**：统一返回 `status / data / evidence / warnings / error / execution`；工具不调 LLM、不修改全局目标（阶段 4 验收标准）。
- **Supervisor / 多 Agent 编排**：一个主管 Agent 把任务分派给子 Agent。

### 5.2 推荐公开资料

- **MCP 官方文档（中文）**：https://mcpcn.com/docs/
- **MCP 教程（构建客户端 Python/Node、编写有效工具）**：https://mcpcn.com/docs/tutorials/
- **MCP 完全指南（架构+实战，掘金）**：https://juejin.cn/post/7503762078386225162
- **MCP 中文 Wiki**：https://mcp.wiki/introduction

### 5.3 MCP 在本项目中的具体职责（结合两篇文章）

MCP 在本系统里扮演「**工具总线 / 工具服务协议**」：把后端能力以标准化工具形式暴露给 Agent 的 LLM 去发现与调用，使「工具实现」与「Agent 决策循环」解耦。

**当前系统（差距分析）已在用 MCP：**
- 后端把能力拆成 MCP 服务；`MCPClientManager.discover_tools()` 在运行时发现远程工具，将其 Schema 转成模型可识别格式（`MCPToolDefinition.as_openai_tool()`），再由 LLM 决定调用、Agent 执行。
- 目前暴露的 MCP 工具只有 3 个：`search_knowledge`（RAG 检索）、`list_excel_tables`、`query_excel`（Excel 统计）。
- 调用链：`ChatService → AgentRunner → LLM 选工具 → MCP 执行 → 更新本轮数据`。
- `/search` 接口本身也通过 MCP 调 `search_knowledge`，并非直接调容器里的 Retriever——同一工具同时服务于「聊天 Agent」和「独立搜索接口」两套入口。

**它解决的具体问题：**
- **解耦**：检索、Excel 统计等工具可独立部署/演进，Agent 主循环只管调度，不关心内部实现。
- **标准化 Schema**：无论本地函数还是远程服务，统一成 OpenAI Tool Calling 的 `name + description + parameters`，LLM 才能自动填参。
- **复用**：同一工具被多处入口调用。

**目标架构里 MCP 的位置：**
- 目标方案把 7 个工具写成 `@tool` 函数（`query_purchase_database`、`retrieve_documents`、`analyze_purchase_excel` 等）。差距分析指出「当前已具备 MCP Schema + Tool Calling 基础」，升级**阶段 1 明确写「继续调用现有三个 MCP 工具」**。
- 结论：MCP 不会被推翻，而是作为**工具传输层**保留——LangGraph 节点负责「决定调哪个工具、怎么拼参数」，MCP 负责「把调用真正派发到远程服务并返回结构化结果（status/data/evidence/error）」。阶段 4 强调统一工具契约：工具不调 LLM、不修改全局目标。

> 一句话：MCP 是让 LLM Agent「即插即用」调用后端检索/Excel/SQL 等能力的标准协议；Agent（自研 `AgentRunner` 或 LangGraph 节点）负责决策，MCP 负责把决策变成对远程工具的实际执行。

---

## 6. 存储与数据层

### 6.1 必学概念

- **MySQL + SQLAlchemy**：采购业务数据、知识库元数据和会话。需补「采购领域模型」（明细、合同、供应商），目前方案 DDL 不完整。
- **Elasticsearch**：文档向量检索 + 数据库 Schema 语义检索；旧 Mapping 不能直接靠换连接类迁移。
- **Redis**：checkpoint、会话缓存、任务缓存。注意：langgraph-checkpoint-redis 需要 RedisJSON + RediSearch 模块（docker-compose 的 `redis:7-alpine` 不满足）。
- **MinIO**：对象存储，保存原文件、解析产物、证据快照、报告文件，绑定版本与内容哈希。

### 6.2 推荐公开资料

- **Redis checkpoint 安装要求（langgraph-redis）**：https://redis-developer.github.io/langgraph-redis/main/user_guide/installation.html
- **langgraph-checkpoint-redis（GitHub）**：https://github.com/redis-developer/langgraph-redis
- **MinIO 官方文档**：https://min.io/docs/minio/linux/index.html
- **Elasticsearch 官方（向量检索）**：https://www.elastic.co/guide/index.html
- **SQLAlchemy 官方**：https://docs.sqlalchemy.org/

---

## 7. 文档解析（把原文变成证据）

差距分析强调：**PDF 不需要重新搭 OCR，直接复用 MinerU/PP-Structure 输出接入 LlamaIndex**。

### 7.1 必学概念

- **MinerU**：上海 AI Lab 开源 PDF 解析，输出 Markdown/JSON（含 OCR、版面、表格、公式、阅读顺序）。
- **结构化切块（StructuredChunker）**：按块类型/章节/Sheet/页码分组，保留页码、坐标、行号、单元格范围。
- **Excel 解析**：识别多 Sheet、多行表头、合并单元格、字段类型，生成表描述（Schema Document）进 ES。
- **Word / 其他格式解析**。

### 7.2 推荐公开资料

- **MinerU 官方仓库**：https://github.com/opendatalab/MinerU
- **MinerU 本地部署保姆级教程（知乎）**：https://zhuanlan.zhihu.com/p/1908942870666282723
- **MinerU Docker 部署（CSDN）**：https://blog.csdn.net/kymowu/article/details/149189958
- **MinerU 安装部署完全指南（博客园）**：https://www.cnblogs.com/yejinxing/p/19888832

---

## 8. 后端与工程化

### 8.1 必学概念

- **FastAPI**：异步 Web 框架，SSE 流式输出，依赖装配（文中 `create_container()`）。
- **Pydantic / Schema 管理**：工具与 Agent 的输入输出契约。
- **SSE 事件流**：前端聊天逐字输出 + 任务阶段/暂停/恢复事件。
- **任务队列与可观测性**（P2）：持久化解析任务、task/run/tool ID 贯通、耗时与错误记录。
- **版本化数据库迁移**（P2-3）：Alembic 等。

### 8.2 推荐公开资料

- **FastAPI 官方文档（中文）**：https://fastapi.tiangolo.com/zh/
- **Pydantic 官方文档**：https://docs.pydantic.dev/
- **SSE / 流式（FastAPI StreamingResponse）**：https://fastapi.tiangolo.com/zh/advanced/custom-response/#streamingresponse

### 8.3 FastAPI 在本项目中的具体职责（结合两篇文章）

FastAPI 在本系统里是**后端骨架 + 网关 + 编排层**：前端、Agent、存储、解析流水线全都通过它串起来，而非只写几个接口。

**承担的五类职责：**
1. **HTTP API 层（对外所有入口）**：聊天（`api/chat.py`，SSE 流式）、搜索（`api/search.py`，本身也经 MCP 调 `search_knowledge`）、文件上传/预览与知识库管理（`api/files.py`）；升级时还要加「任务查询 / 恢复 / 报告访问」接口（P0-6）。
2. **依赖装配容器（`create_container()`）**：`main.py` 的 `lifespan()` + `dependencies.py` 的 `create_container()` 集中初始化数据库、对象存储、解析 Worker，并注册 API、装配 Agent 与 MCP Client，相当于后端 IoC 容器。
3. **会话编排服务（`chat/service.py`）**：`stream_answer()` / `_prepare_answer()` 从 MySQL 加载历史、必要时滚动摘要、调用 Agent、保存回答，是「用户请求 → Agent 决策 → 返回」主链路。
4. **文档摄入流水线编排（`document/service.py`）**：上传 → MinIO 存原文件 → **FastAPI 后台任务** → 结构化解析（MinerU/PP-Structure）→ 切块 → Embedding → 入库 ES/MySQL（目标架构第 11 节亦明确「FastAPI 后台任务 → MinerU Worker」）。
5. **SSE 流式输出**：前端逐字渲染，事件含 `token`、`references`、`done`；升级后追加 `task_id`、阶段、暂停/恢复、报告结果（P0-6）。

**当前短板（差距分析）**：文件解析依赖 FastAPI `BackgroundTasks`，缺持久化任务队列、重启续跑、任务认领（P2-1），是后续工程要补的点。

> 一句话：FastAPI 在此承载网关（HTTP/SSE）、依赖注入容器、会话主链、文档摄入触发、长任务后台执行五类职责，是连接前端与 Agent/存储/解析的中央枢纽。

---

## 9. 建议的学习与实践顺序（对照差距分析 6 阶段）

把上面知识线按「先框架、后检索、再数据」的顺序落地，正好对应差距分析的升级路线：

1. **先学 ① + ②（LLM/Agent 基础 + LangGraph）**：能跑通一个最小 LangGraph Agent（State + 节点 + checkpoint）。对应阶段 1（基础 LangGraph 改造）。
2. **再学 ③ + ④（LlamaIndex + 检索工程）**：把现有解析结果接入 LlamaIndex，做混合检索对照。对应阶段 2-3（Agent 拆分、LlamaIndex 接入）。
3. **学 ⑤（存储）与 ⑦（解析）**：落实采购业务模型、ES 版本化、MinIO 证据快照。对应阶段 5（数据处理升级）。
4. **学 ⑥（MCP/Tool 契约）+ ⑧（FastAPI/工程化）**：统一工具契约、任务恢复接口、评估测试。对应阶段 4、6。

> 优先级提示：差距分析中 **State 设计、运行可恢复、SQL/采购数据能力、证据一致性** 标为「高」难度，是实践时最容易卡住的地方，建议先把 LangGraph 的 State + Checkpointer 吃透。

---

## 10. 一页速查：知识 → 资源

| 知识 | 首选资源 |
| --- | --- |
| Agent 设计直觉 | Anthropic Building Effective Agents |
| Agent 系统课 | Hugging Face Agents Course |
| LangGraph | docs.langchain.com/oss/python/langgraph（overview / quickstart / persistence / checkpointers） |
| LlamaIndex | developers.llamaindex.ai（VectorStoreIndex / IngestionPipeline / ElasticsearchStore） |
| 混合检索 RRF | smallyoung.cn RAG 混合检索；walterwang0x01 生产实战 |
| BGE-M3 | FlagEmbedding 仓库；cnblogs BGE-M3 介绍 |
| MCP | mcpcn.com/docs |
| Redis checkpoint | redis-developer langgraph-redis 安装要求 |
| MinerU | github.com/opendatalab/MinerU |
| FastAPI | fastapi.tiangolo.com/zh |

---

## 11. 推荐学习路径（由浅入深，9 步）

按「先跑通单个能力 → 再组合成 Agent → 最后接存储与文档」的顺序，每一步都对应上面某条知识线，并可直接映射到差距分析的升级阶段。

| 步 | 目标 | 学什么（对应章节） | 产出 |
| --- | --- | --- | --- |
| 1 | 跑通 LLM 调用 | ① LLM 基础、OpenAI 兼容接口 | 能发 prompt、收回答、理解 token |
| 2 | 第一个 RAG | ③ LlamaIndex、④ 向量 | 本地文件问答的最小 RAG |
| 3 | 第一个 Tool Calling | ① Tool Calling、⑤ MCP 基础 | Agent 能调一个外部工具 |
| 4 | LangGraph 状态机 | ② LangGraph | 计算器 Agent（State+节点+边） |
| 5 | 记忆与恢复 | ② Checkpointer | 重启后能续上对话/任务 |
| 6 | 人工介入 | ② Human-in-the-loop | 关键步骤可暂停等用户确认 |
| 7 | 混合检索 + Reranker | ④ BM25/向量/RRF/Reranker | 检索质量可对照评估 |
| 8 | 多 Agent 编排 | ② Supervisor、⑤ MCP | 主管分派子 Agent |
| 9 | 接存储 + 文档解析 | ⑤⑥⑦⑧ | 最小采购审计闭环（综合案例 K） |

> 路线与差距分析 6 阶段对照：步 1-3 ≈ 阶段 1 基线；步 4-6 ≈ 阶段 1-2（LangGraph + Agent 拆分）；步 7 ≈ 阶段 3（LlamaIndex 接入）；步 8-9 ≈ 阶段 4-5（Tool 体系 + 数据处理）。

---

## 12. 可动手的最小案例清单

每个案例给出「目标 / 用到的知识 / 关键代码骨架 / 参考」。代码为示意，实践以官方最新 API 为准。

### 案例 A：第一个 LLM 调用（步 1）
- **目标**：理解 prompt 与消息结构。
- **知识点**：① LLM 基础。
- **骨架**：
```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8080/v1", api_key="none")
r = client.chat.completions.create(
    model="Qwen3-8B", messages=[{"role":"user","content":"15万买激光器合理吗？"}])
print(r.choices[0].message.content)
```

### 案例 B：最小 RAG（步 2）
- **目标**：把一个本地 PDF/Markdown 变成可问答知识库。
- **知识点**：③ LlamaIndex、④ Embedding。
- **骨架**：
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
docs = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(docs)
print(index.as_query_engine().query("采购制度对单价有什么要求？"))
```
- **参考**：LlamaIndex VectorStoreIndex 官方文档（第 3 节链接）。

### 案例 C：第一个 Tool Calling Agent（步 3）
- **目标**：让模型自动决定调用一个工具并填参数。
- **知识点**：① Tool Calling、⑤ MCP 基础。
- **骨架**（LangChain 风格 `@tool`）：
```python
from langchain_core.tools import tool
@tool
def get_price(item: str) -> float:
    """查询某设备历史采购单价。"""
    return {"激光器": 14.0}.get(item, 0.0)
# 把 tools 传给模型，让它返回 tool_calls，再用 ToolExecutor 执行
```
- **参考**：MCP 中文文档（第 5 节）；LangChain Tool Calling 文档。

### 案例 D：LangGraph 计算器（步 4）
- **目标**：理解 State + 节点 + 边。
- **知识点**：② LangGraph 核心。
- **骨架**：
```python
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    nums: Annotated[list[float], operator.add]
    result: float

def add(state):  return {"result": sum(state["nums"])}
def decide(state): return "add" if state["result"] is None else END

g = StateGraph(State)
g.add_node("add", add); g.add_edge(START, "add"); g.add_edge("add", END)
app = g.compile()
print(app.invoke({"nums":[3,5]}))
```
- **参考**：LangGraph Quickstart（第 2 节）。

### 案例 E：带记忆/恢复的对话（步 5）
- **目标**：进程重启后任务能续上。
- **知识点**：② Checkpointer/Persistence。
- **骨架**：
```python
from langgraph.checkpoint.memory import MemorySaver
app = g.compile(checkpointer=MemorySaver())
app.invoke({"nums":[3]}, config={"configurable":{"thread_id":"t1"}})
# 之后用同一 thread_id 续跑，状态从 checkpoint 恢复
```
- **参考**：LangGraph Persistence / Checkpointers（第 2 节）。

### 案例 F：Human-in-the-loop 审批（步 6）
- **目标**：关键动作前暂停，等用户确认再继续。
- **知识点**：② interrupt。
- **骨架**：
```python
from langgraph.types import interrupt
def risky_step(state):
    decision = interrupt({"ask":"确认执行 SQL？"})  # 暂停，等外部 resume
    return {"approved": decision}
app = g.compile(checkpointer=MemorySaver())
# app.invoke(..., config); app.invoke(None, config)  # 用户确认后 resume
```
- **参考**：LangGraph Persistence 文档中 human-in-the-loop 章节。

### 案例 G：混合检索（BM25 + 向量 + RRF）（步 7）
- **目标**：对比纯向量检索，体会精确编号匹配为何更准。
- **知识点**：④ 混合检索、RRF、Reranker。
- **做法**：用 LlamaIndex 的 `BM25Retriever` + `VectorIndexRetriever` 各取 Top-K，再用 `rrf` 融合；最后接一个 Cross-Encoder Reranker。
- **参考**：第 4 节 smallyoung.cn / walterwang0x01 实战。

### 案例 H：BGE-M3 + ElasticsearchStore（步 7 进阶）
- **目标**：把案例 B 的索引迁到 ES，统一模型版本。
- **知识点**：③ LlamaIndex ES、④ BGE-M3。
- **骨架**：
```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.elasticsearch import ElasticsearchStore
from llama_index.core import VectorStoreIndex, Settings
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
vs = ElasticsearchStore(index_name="docs", es_url="http://localhost:9200")
index = VectorStoreIndex.from_documents(docs, vector_store=vs)
```
- **参考**：第 3、4 节 ElasticsearchStore / BGE-M3 链接。

### 案例 I：SQL Agent（受控执行）（步 8）
- **目标**：自然语言 → SQL，但**不**直接执行模型字符串。
- **知识点**：⑤ 只读账号、白名单、语句校验。
- **做法**：Agent 生成 SQL → 工具层做「只读校验 + 表字段白名单 + 行数上限」→ 用 SQLAlchemy 执行。
- **参考**：SQLAlchemy 官方（第 6 节）；差距分析 P0-2 / 阶段 4 工具契约。

### 案例 J：价格合理性分析（纯 Python，不调 LLM）（步 8）
- **目标**：理解「分析节点不调 LLM、只做确定性计算」。
- **知识点**：⑧ 确定性工具、口径校验。
- **骨架**：
```python
def analyze_price(current: float, history: list[float]):
    avg = sum(history)/len(history)
    dev = (current-avg)/avg
    return {"avg":avg, "deviation":dev, "risk":"高" if abs(dev)>0.3 else "低"}
```
- **注意**：必须传入币种、含税口径、单位、时间，否则偏差不可比（差距分析 P0-4 强调）。

### 案例 K：最小采购审计 Agent（综合，步 9）
- **目标**：把以上拼成闭环——验证「15 万买激光器是否合理」。
- **做法**：
  1. `Supervisor` 初始化 `AuditState`（goal=采购合理性审计）。
  2. `Decision` 看 `missing_information`，先调 `query_purchase_database`（案例 I）取历史价。
  3. 再调 `retrieve_documents`（案例 B/H）取制度与合同。
  4. `Analysis` 跑 `analyze_price`（案例 J）。
  5. `Audit Reasoning` 综合证据给结论；`Report` 渲染报告（绑定 evidence ID）。
  6. 全程用 `MemorySaver`/`Redis` checkpoint 记录每步状态，可恢复。
- **对应**：目标架构总体需求第 4-6 节 + 差距分析阶段 1-6。

---

### 案例难度与前置关系

```
A(LLM) → B(RAG) → C(Tool)
                    ↓
              D(LangGraph) → E(记忆) → F(审批)
                                ↓
                    G(混合检索) → H(ES索引)
                                ↓
              I(SQL) + J(价格) → K(综合审计)
```

建议：先逐个跑通 A~F（每个半天~1 天），再挑战 G~J，最后用 K 串成完整系统。每完成一个案例就对照差距分析对应阶段写一段小结，便于回看。

---

*整理日期：2026-09-08。以上链接均为公开可访问资料，版本可能随官方更新变化；实践时以官方最新文档为准。*
