# AISI 项目 · Codex 宿主适配指令

## 项目概述

AI + 系统工程（MBSE）工具套件：从业务资料与系统描述生成四视图（需求/组成/架构/流程）→ 系统规格说明 + SysML v2 + 追踪矩阵。设计遵循 12-Factor Agents（契约见 `docs/contracts/aisi-toolkit-contract-v0.md`）。

## 常用命令

```powershell
uv run python -m aisi --help                    # 系统拆解 CLI（uv 不可用：.venv\Scripts\python.exe -m aisi）
uv run python -m aisi status                     # 任何工作前先看断点状态
uv run python -m unittest discover -s tests -v   # 全量测试（25 项）
uv run python .opencode/skills/knowledge-base/kb.py search "关键词"   # 知识库检索
```

## 系统拆解工作流约束

- **阶段门禁**：requirements → composition → architecture → processes 严格顺序；每视图 draft→validated→reviewed→approved。
- **人类门禁**：`gate approve` 仅在用户明确说"通过"后执行，绝不自行批准；reject 带用户意见。
- **契约优先**：LLM 产出 JSON 草稿必须过 `aisi validate`（exit 2 时按 errors[].path/message 修正）；退出码 0/2/3/4。
- **证据闭环**：资料 `ingest` 入库 → `coverage` 查缺口 → 调研需用户同意 → 结论带来源回填。
- **不杜撰**：资料未展开的细节写 clarifications 待澄清，不编造。
- **断点续作**：状态全在 systems/*/gates.json 与 views/*.json；恢复工作先 `aisi status`。

## 代码规范

- `aisi` 包零第三方运行时依赖（pdf/docx 抽取仅用项目 venv 已装库）；所有命令 JSON in/out、幂等、状态即文件。
- 新增输出结构必须先加 `aisi/schemas/*.schema.json` 契约并在 docs/contracts 登记修订号。
- 中文输出（SysML 标识符英文 camelCase）。
