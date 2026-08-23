---
id: KB-2026-0001
type: decision
title: 知识库采用文件式存储（Markdown + SQLite FTS5）而非向量库/图数据库
tags: [knowledge-base, architecture, sqlite]
source: 与用户讨论，2026-08-23
created: 2026-08-23
status: active
supersedes: ""
---

## 内容

本项目（AISI，单机 Trae/opencode + uv + Git 环境）的知识库技术路径选型：

- **L1 索引层**：`knowledge/INDEX.md`，启动时轻量加载做路由（渐进式披露，参考 Anthropic Agent Skills）。
- **L2 知识层**：每条知识一个 Markdown 文件（YAML frontmatter + 原文正文），按 domains/decisions/lessons/entities 四分类，原文保存不做摘要（参考 MemPalace 的 verbatim 原则，避免摘要丢失信息）。
- **L3 检索层**：`knowledge/index.db`，SQLite FTS5 且 tokenizer 必须用 `trigram`（默认 unicode61 不切中文，中文检索不可用），由 `.opencode/skills/knowledge-base/kb.py` 维护。

**否决方案**：
- Mem0 / Letta / Supermemory（向量库路线）：需要 Postgres + 向量服务，部署成本超过单机项目收益。
- Zep/Graphiti、Cognee（知识图谱路线）：需要图数据库（Neo4j 等），多跳推理能力在本场景用不上。
- 纯 Markdown + Grep：中文语义检索弱，已由 SQLite FTS5 补齐。

**保留的机制借鉴**：
- Mem0 的"写前查重"；Zep 的 supersession 时效链（status + supersedes，过时不删而是标记被取代）；Letta Context Repos 的"记忆进 Git、可 diff 可回滚"。

## 适用场景

- 为本项目扩展知识库功能、修改 kb.py 或调整知识分类时。
- 评估是否引入向量检索/嵌入模型时（当前结论：数据量小，FTS5 够用；若未来知识超过数千条且需要语义近义召回，再考虑本地嵌入）。
