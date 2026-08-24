# AISI · 系统知识拆解工具套件

基于大模型的 AI + 系统工程（MBSE）工具链：**业务资料 + 系统描述 → 四视图（需求/组成/架构/流程）→ 系统规格说明 + SysML v2 + 追踪矩阵**。

设计遵循 [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)：LLM 只负责理解与生成（Schema JSON 草稿），CLI 负责一切确定性处理（校验/编号/追踪/渲染/导出）；二者通过 JSON 契约解耦，**任何能执行 shell 的智能体宿主均可接入**。

## 架构

```
宿主适配层  opencode Skill / Codex AGENTS.md / 自研 Harness（docs/harness-integration-guide.md）
门禁编排层  gates.json 状态机：draft→validated→reviewed→approved（人类在环、断点续作）
核心工具层  aisi CLI：init/ingest/coverage/research/validate/gate/clarify/trace/export/render/status
契约层      10 个版本化 JSON Schema（GJB438C + ISO 29148 + SysML v2 对齐）
```

## 快速开始

```powershell
uv sync                                                        # 或 pip install -e .
uv run python -m aisi init --id my-system --name 我的系统 --domain software
uv run python -m aisi ingest --file 设计报告.docx              # 资料分块锚点入库
uv run python -m aisi coverage                                 # 证据缺口分析
# …LLM 生成 views/requirements.json（按 aisi/schemas 契约）…
uv run python -m aisi validate --view requirements             # 校验→validated
uv run python -m aisi gate review requirements                 # 人工审阅
uv run python -m aisi gate approve requirements --comment 通过  # 批准（解锁下一视图）
# 四视图全部 approved 后：
uv run python -m aisi trace && uv run python -m aisi export && uv run python -m aisi render --format all
```

## 交付物（以黄金样例 HR 管理系统为例）

| 产物 | 位置 | 规模 |
---|---|---|
| 四视图结构化数据 | `systems/*/views/*.json` | 67 需求 / 32 模块 / 4 层架构 / 8 流程 |
| 追踪矩阵 | `trace.json` + `render/trace.md` | 170 边，0 孤儿需求 |
| SysML v2 | `sysml/*.sysml` ×4 | requirement 树 / part def / 分层 / action def |
| 图集 | `render/viewer.html` + 12 张 mermaid | 需求树/模块树/架构/流程/数据流 |
| 规格说明报告 | `reports/system-specification.md` | GJB 438C 风格 9 章（GitHub 直接渲染） |

## 测试

```powershell
uv run python -m unittest discover -s tests -v   # 25 项（M1 契约 / M2 资料通道 / M4 交付物 / 知识库）
```

## 宿主接入

| 宿主 | 入口 |
---|---|
| opencode | `.opencode/skills/system-decomposition/SKILL.md` |
| Codex | `AGENTS.md` |
| 自研 Harness | `docs/harness-integration-guide.md` |

## 更多

- 契约基线与修订记录：`docs/contracts/aisi-toolkit-contract-v0.md`
- Agent 知识库（md+SQLite FTS5）：`.opencode/skills/knowledge-base/`
- 黄金样例全过程（三轮门禁打回留痕）：`systems/hr-management-system/gates.json`
