---
name: system-decomposition
description: 基于大模型的系统知识拆解工具（AI+MBSE）：从业务资料与用户系统描述生成四视图（需求/组成/架构/流程）并产出系统规格说明、SysML v2 与追踪矩阵。Use when the user asks for 系统拆解、系统设计、需求分析、系统需求清单、架构设计、功能组成、业务流程设计、系统规格说明、SysML 生成、GJB438C 文档, or English equivalents like decompose system, generate system specification, requirements/architecture/process design.
---

# 系统知识拆解工具套件 · opencode 宿主适配

本 skill 是 `aisi` CLI 的**薄封装**（12-Factor：逻辑在工具，提示词在适配层）。核心原则：
**LLM 负责理解与生成（产出符合 Schema 的 JSON 草稿），CLI 负责确定性处理（校验/编号/追踪/渲染/导出）**。

## 命令速查

```powershell
# 一律 uv run；uv 不可用时用 .venv\Scripts\python.exe -m aisi
uv run python -m aisi init --id <系统id> --name <中文名> --domain <airborne|aerospace|information-system|software|other> [--profile gjb438c|gb8567|custom]
uv run python -m aisi ingest --file <资料路径或URL> [--title 标题]        # 资料分块锚点入库（md/txt/html/docx/pdf）
uv run python -m aisi coverage                                            # 证据缺口分析 → research/gaps.json
uv run python -m aisi research plan                                       # 缺口 → 调研问题清单
uv run python -m aisi research ingest --file <findings.json> [--to-kb]    # 调研结果归档（可沉淀知识库）
uv run python -m aisi validate --view <requirements|composition|architecture|processes>   # Schema+lint → validated
uv run python -m aisi gate review <view>                                  # 人工审阅确认
uv run python -m aisi gate approve <view> --comment <意见>                 # 人类批准（解锁下一视图）
uv run python -m aisi gate reject <view> --comment <原因>                  # 打回 draft
uv run python -m aisi clarify <REQ-ID> --answer <答案>                     # 待澄清回填
uv run python -m aisi status                                              # 断点续作：当前阶段+下一步
uv run python -m aisi trace                                               # 追踪矩阵（四视图 approved 后）
uv run python -m aisi export                                              # SysML v2 导出 ×4
uv run python -m aisi render --format all                                 # mermaid×N + HTML 查看器 + GJB438C 报告
```

退出码：`0` 成功 / `2` 契约校验失败（看 errors[].path+message 修正草稿）/ `3` 门禁拒绝（先看 status）/ `4` 未找到。

## 标准工作流

### 阶段 0 · 资料通道（任意时刻可触发）
1. `ingest` 用户提供的资料（多份逐个入库，SRC-001/002… 自动编号）。
2. `coverage` 检查缺口：来源断链 / 无来源 / 待澄清 / 性能缺量化。
3. 有缺口时**询问用户**是否启用搜索调研；同意后：逐题 web 搜索 → 按 `aisi.research/1` 契约填写 findings+sources → `research ingest --to-kb` → 执行输出中提示的 `kb.py save` 命令沉淀知识库 → `clarify` 回填需求。

### 阶段 1-4 · 四视图（严格顺序：requirements → composition → architecture → processes）
每视图循环：
1. **生成草稿**：读契约（`aisi/schemas/<view>.schema.json`）+ 资料分块（按 source_refs 锚点**按需读取**，不整篇塞上下文）→ 产出符合 Schema 的 JSON 写入 `views/<view>.json`。
   - 需求视图：按类型分组（功能/性能/数据/部署/安全/接口），细粒度叶子，全量 source_refs 溯源，资料未展开处写 `clarifications`（question 留空 answer）——**不杜撰**。
   - 组成视图：MOD-00 根 + 子系统/模块层级，`requirements` 数组承载需求（目标 100% 覆盖）。
   - 架构视图：layers 自适应层数 + services + data_assets + deploy_nodes，模块 layer 引用需与组成视图一致。
   - 流程视图：processes（steps 带 module/inputs/outputs/next/exceptions）+ dataflows + interfaces。
2. **校验**：`validate --view <v>`；exit 2 → 按 errors 修正草稿重跑，直到通过（state → validated）。
3. **人类审阅**：向用户展示渲染摘要（树状结构/统计/关键内容），请求确认。
4. **门禁**：用户明确说"通过" → `gate review` + `gate approve --comment <用户意见摘要>`；用户给修改意见 → `gate reject --comment <意见>` → 回到 1。

### 阶段 5 · 交付物（四视图全部 approved 后）
`trace` → `export` → `render --format all`，向用户报告产物路径：
- `trace.json` + `render/trace.md`（追踪矩阵）
- `sysml/*.sysml` ×4（SysML v2，可在 SysON 打开）
- `render/viewer.html`（图集）+ `reports/system-specification.md`（GJB 438C 报告，GitHub 直接渲染 mermaid）

## 铁律（不可违反）

1. **人类门禁**：`gate approve` 只能在用户明确表示"通过"后执行；**绝不自行批准**。reject 必须带用户原话摘要。
2. **不跳阶段**：前一视图未 approved 不得开始下一视图（CLI 会拒绝，也不要 --force，除非用户明确要求并给原因）。
3. **改已批准内容**：先 `gate reset <view>`，改完重新 validate→review→approve。
4. **原文保真**：需求 text 保留资料原始表述与数值；量化指标进 measures（数值+单位+条件）。
5. **不杜撰**：资料没有的内容 → clarifications 待澄清 + coverage 调研建议；调研结论必须带来源。
6. **上下文纪律**：先 `status` 再决定读什么；资料只读锚点命中的分块；长文档不整篇加载。
7. **状态即文件**：一切状态在 gates.json/views/*.json，断点续作用 `status`，不依赖记忆。

## 契约与参考

- 契约基线：`docs/contracts/aisi-toolkit-contract-v0.md`（修订 R1-R4 已登记）
- Schema：`aisi/schemas/*.schema.json` ×10
- 黄金样例：`systems/hr-management-system/`（四视图+追踪+SysML+报告全套）
