---
name: knowledge-base
description: AI Agent 知识库（本体 Markdown + SQLite FTS5）。识别文本中的业务知识与工作知识并存储、查重、检索、建立关系、管理时效。Use when the user asks for 知识入库、沉淀知识、保存经验/决策/业务规则/工作流程、识别文本里的知识、查知识库、检索知识、更新或取代某条知识, or English equivalents like save knowledge, extract knowledge from text, search knowledge base, record this decision/lesson/business rule.
---

# AI Agent 知识库（识别 / 写入 / 检索 / 关系 / 时效）

本 skill 是一个**零部署、零第三方依赖**的项目级 Agent 知识库。设计借鉴 2026 年主流开源方案（Mem0、Zep/Graphiti、Letta、Cognee、memweave/sqlite-memory）的机制，但用"本体 Markdown + SQLite"落地，适合单机 Agent 项目：可 Git diff、可回滚、中文检索友好。

## 架构（三层 + 轻量本体）

```
L1 索引层  knowledge/INDEX.md     自动生成（勿手改），Agent 启动时轻量加载做路由
L2 本体层  knowledge/<分类>/*.md  每条知识一个文件：frontmatter 元数据 + 原文正文
L3 检索层  knowledge/index.db     SQLite FTS5(trigram) 全文索引 + links 关系表
```

**轻量本体** = 6 种知识类型 + 4 种关系 + 自由标签：

| 类型 | 目录 | 存什么 | 识别线索示例 |
| ---- | ---- | ------ | ------------ |
| `business` 业务知识 | `knowledge/business/` | 业务规则、产品口径、指标定义、计费/审批/合规政策 | 必须、不得、规则、指标、口径、客户、需求 |
| `workflow` 工作知识 | `knowledge/workflow/` | 操作流程、工具用法、命令、配置、SOP | 步骤、首先/然后、命令、部署、安装、配置 |
| `decision` 决策记录 | `knowledge/decisions/` | 选型与方案取舍及理由（ADR） | 决定、选型、采用、否决、权衡、对比 |
| `lesson` 经验教训 | `knowledge/lessons/` | 踩坑、调试结论、验证过的解法 | 问题、报错、失败、原因、解决、注意 |
| `entity` 实体卡片 | `knowledge/entities/` | 项目、工具、人物、组织的结构化信息 | 是一个、负责人、地址、属于 |
| `domain` 领域知识 | `knowledge/domains/` | 暂未细分的一般领域知识 | （默认兜底） |

关系（`kb.py link A B <relation>`）：`supersedes`（取代，自动从 frontmatter 生成）、`supports`（支撑）、`contradicts`（矛盾）、`related`（相关）。

**运行方式**：项目规范为 `uv run python ...`；若 uv 不可用，用 `.venv\Scripts\python.exe .opencode\skills\knowledge-base\kb.py ...` 兜底。

## 工作流程

### 流程 1：从文本识别知识（用户给文本/文档，要求"识别/提取/入库"）

1. **规则预筛**（脚本完成）：
   ```powershell
   .venv\Scripts\python.exe .opencode\skills\knowledge-base\kb.py scan "<文本文件>"
   ```
   输出 JSON：候选块 + 类型猜测 + 命中线索 + 行号定位 + 置信度。
2. **Agent 复核**（LLM 完成，规则引擎只做召回不做定案）：
   - 丢弃背景叙述、客套话、与知识无关的块；
   - 修正类型（如"部署步骤"误判为 business → workflow）；
   - 拆分复合块（一段含规则+流程 → 拆两条）；
   - 凝练标题（一句话说清这条知识）、补 `## 适用场景`；
   - 补充 tags（英文小写、逗号分隔）。
3. **写入**：每条知识写一个 md 文件（模板见下）到对应目录，然后：
   ```powershell
   .venv\Scripts\python.exe .opencode\skills\knowledge-base\kb.py save "knowledge\<分类>\<文件>.md"
   ```
   `save` 会：校验 frontmatter、自动分配缺失 ID、**自动查重提醒**、自动刷新 INDEX.md。
4. **快速模式**（用户明确说"直接存/不用确认"）：`scan --save` 一键入库，事后复核。

### 流程 2：检索（用户问"之前怎么定的/有没有相关经验"或新任务需要背景）

```powershell
kb.py search "<关键词>" -n 10        # 全文检索（>= 3 字符），返回命中摘要
kb.py get KB-2026-0001               # 读全文 + 关系
kb.py list [business|workflow|...]   # 浏览
kb.py stats                          # 分类/标签统计
```

规则：**先检索再回答**；命中后必须读文件全文再引用；`status != active` 的条目引用时须说明并追踪其取代者。

### 流程 3：时效管理（旧结论被推翻，Zep 式 supersession）

不删除旧文件：新建新知识 → 旧文件 frontmatter 改 `status: superseded`，正文末尾追加"## 已被取代"（新 ID + 原因）→ 新文件 `supersedes: <旧ID>` → 两个文件重新 `save`（links 表自动建立 supersedes 关系）。

## 知识文件模板

```markdown
---
id: KB-2026-0002
type: business
title: <一句话标题>
tags: [billing, rule]
source: <文档名 章节行号 / 对话日期 / URL>
created: 2026-08-23
status: active
supersedes: ""
confidence: high
---

## 内容
<原文保真：保留数值、单位、命令、代码，不做摘要式改写>

## 适用场景
<什么情况下应检索并使用本条知识>
```

说明：`id` 缺失时 `save` 自动分配并回写；`type` ∈ {business, workflow, decision, lesson, entity, domain}；`status` ∈ {active, superseded, outdated}；`confidence` ∈ {high, medium, low}。文件名规范：`<ID>-<英文短名>.md`。

## 命令速查

| 命令 | 作用 |
| ---- | ---- |
| `kb.py init` | 初始化目录 + INDEX.md |
| `kb.py scan <文件或-> [--save]` | 识别知识候选（JSON 预览 / 直接入库） |
| `kb.py save <md> [add 别名]` | 索引文件：校验 + 自动ID + 查重 + 刷 INDEX |
| `kb.py search "<词>" [-n N] [--all]` | FTS5 trigram 全文检索，带命中摘要 |
| `kb.py get <KB-ID>` | 全文 + 关系链 |
| `kb.py list [type] [--all]` | 条目列表 |
| `kb.py stats` | 类型/状态/标签统计 |
| `kb.py link <A> <B> <关系> [--note]` | 建立关系 |
| `kb.py similar <ID或标题>` | 查重 |
| `kb.py rebuild` | 全量重建索引 + 刷 INDEX.md |

## 注意事项

- **仅手动写入**：未经用户明确要求，不写、不改、不删知识条目。
- **原文保真**：正文保留原始数值/单位/命令/代码；宁可长，不做有损摘要。
- **写前必查重**：重复是知识库腐烂的主因；`save` 已内置提醒，语义相同时更新原文件而非新建。
- **一条知识一个文件**：复合内容拆条，各自独立可检索。
- **来源可追溯**：source 尽量精确到章节号/行号/URL。
- **INDEX.md 是生成物**：由 kb.py 维护，永不手改（v1 手工维护导致索引漂移是历史教训）。
- `index.db` 不进 Git；知识 `.md` 与 INDEX.md 进 Git，可 diff 可回滚。
