# AISI 项目知识库索引

> ⚠️ 本文件由 kb.py 自动生成（save/rebuild 时同步刷新），请勿手工编辑。
> 最后更新：2026-08-24 ｜ 总条目 8 ｜ active 8

## 使用说明

- 检索：`kb.py search "关键词"`（中文友好，关键词 >= 3 字符）
- 写入：先 `kb.py scan <文本>` 识别候选 → Agent 规范化 → `kb.py save <文件>`
- 重建：`kb.py rebuild`（INDEX.md 同时刷新）

## business/ — 业务知识

业务知识。业务规则、产品口径、指标定义、业务流程等领域事实

| ID | 标题 | 标签 | 状态 | 更新 | 文件 |
| -- | ---- | ---- | ---- | ---- | ---- |
| （暂无） | | | | | |

## workflow/ — 工作知识

工作知识。操作流程、工具用法、命令、配置、SOP 等工作方法

| ID | 标题 | 标签 | 状态 | 更新 | 文件 |
| -- | ---- | ---- | ---- | ---- | ---- |
| （暂无） | | | | | |

## decisions/ — 决策记录

决策记录。技术/方案选型决策（ADR 风格），含理由与取舍

| ID | 标题 | 标签 | 状态 | 更新 | 文件 |
| -- | ---- | ---- | ---- | ---- | ---- |
| KB-2026-0001 | 知识库采用文件式存储（Markdown + SQLite FTS5）而非向量库/图数据库 | knowledge-base,architecture,sqlite | active | 2026-08-23 | knowledge/decisions/KB-2026-0001-file-based-knowledge-store.md |
| KB-2026-0002 | Agent 知识库 v2：六类本体 + links 关系表 + 索引自动生成 + 文本知识识别 | knowledge-base,ontology,sqlite,agent | active | 2026-08-23 | knowledge/decisions/KB-2026-0002-agent-kb-v2.md |

## lessons/ — 经验教训

经验教训。踩坑、调试结论、验证过的解决方案

| ID | 标题 | 标签 | 状态 | 更新 | 文件 |
| -- | ---- | ---- | ---- | ---- | ---- |
| KB-2026-0004 | 需求拆解的三轮迭代经验：粗粒度→层级化→类型分组（附待澄清机制） | requirements,sysml,gjb438c,workflow | active | 2026-08-23 | knowledge/lessons/KB-2026-0004-requirement-decomposition-iteration.md |

## entities/ — 实体卡片

实体卡片。项目、工具、人物、组织等实体结构化卡片

| ID | 标题 | 标签 | 状态 | 更新 | 文件 |
| -- | ---- | ---- | ---- | ---- | ---- |
| KB-2026-0003 | AISI 项目进展快照（2026-08-23） | progress,milestone,aisi | active | 2026-08-23 | knowledge/entities/KB-2026-0003-aisi-progress-2026-08-23.md |

## domains/ — 领域知识

领域知识。暂未细分的一般领域知识

| ID | 标题 | 标签 | 状态 | 更新 | 文件 |
| -- | ---- | ---- | ---- | ---- | ---- |
| KB-2026-0005 | 调研：报告未展开职称管理细节，是否与职位管理同构？ | research,hr-management-system | active | 2026-08-24 | knowledge/domains/KB-2026-0005-research.md |
| KB-2026-0006 | 调研：调研行业典型值或与用户确认 REQ-002 的量化指标（数值+单位+条件） | research,hr-management-system | active | 2026-08-24 | knowledge/domains/KB-2026-0006-research.md |
| KB-2026-0007 | 调研：报告未给出量化响应指标（如页面响应时间上限），是否需要补充？ | research,hr-management-system | active | 2026-08-24 | knowledge/domains/KB-2026-0007-research.md |
| KB-2026-0008 | 调研：调研行业典型值或与用户确认 REQ-002.1 的量化指标（数值+单位+条件） | research,hr-management-system | active | 2026-08-24 | knowledge/domains/KB-2026-0008-research.md |
