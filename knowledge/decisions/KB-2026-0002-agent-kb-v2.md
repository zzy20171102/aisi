---
id: KB-2026-0002
type: decision
title: Agent 知识库 v2：六类本体 + links 关系表 + 索引自动生成 + 文本知识识别
tags: [knowledge-base, ontology, sqlite, agent]
source: 与用户讨论并调研 2026 主流方案，2026-08-23
created: 2026-08-23
status: active
supersedes: ""
confidence: high
---

## 内容

基于 2026 年高星开源方案调研（Mem0 约 4 万+ star、Letta、Zep/Graphiti、Cognee、MemOS、LightRAG，以及社区回归 Markdown+SQLite 的 memweave / sqlite-memory 趋势），确定本仓库知识库 v2 设计：

**维持"本体 Markdown + SQLite"路线**（否决向量库/图数据库：需额外基础设施，超出单机 Agent 项目收益），借鉴各家机制而非其基础设施：

- **Mem0** → 写前查重：`save` 自动 bm25 相似度提醒（阈值 score < -1.5）。
- **Zep/Graphiti** → 时效管理：`status + supersedes` 不删旧知识，新增 `links` 关系表（supersedes/supports/contradicts/related）。
- **Letta** → Agent 自管理：识别-复核-写入流程由 skill 驱动，规则引擎（`scan`）只做召回，LLM 复核定案。
- **memweave/sqlite-memory** → md 为本体、SQLite 只做检索层的双记忆架构。
- **Anthropic Skills** → L1 轻量索引渐进式披露。

**本体定义**：6 类型（business 业务知识 / workflow 工作知识 / decision 决策 / lesson 教训 / entity 实体 / domain 领域）+ 4 关系 + 自由标签。

**v1 教训修复**：
1. `connect()` 补 `conn.row_factory = sqlite3.Row`（v1 缺失导致 list/search 必崩）。
2. INDEX.md 改为 kb.py 自动生成（v1 手工维护导致索引与实际条目漂移）。
3. schema 加 `PRAGMA user_version`，旧脏库自动丢弃重建（v1 遗留 FTS 行 id=NULL 导致检索永 miss）。

## 适用场景

- 修改 kb.py、调整知识分类或关系模型时先读本条。
- 评估是否引入向量检索/嵌入：当前结论仍是数据量小、FTS5 够用；数千条以上且需语义近义召回再评估本地嵌入。
