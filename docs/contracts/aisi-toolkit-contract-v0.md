# AISI 系统知识拆解工具套件 · 契约层设计 v0.1

> 状态：**已通过**（G0 approved，2026-08-23；用户变更：GJB 438B → GJB 438C）。
> 本文件冻结为 v0.1 实施基线。实施中小扩展：`aisi gate` 增加 `review`/`reset` 动作（见 §5/§6）。
> 设计原则：12-Factor Agents（https://github.com/humanlayer/12-factor-agents）

## 1. 定位与命名

| 项 | 值 |
|---|---|
| 包名 | `aisi-toolkit`（Python 包 `aisi`） |
| CLI 命令 | `aisi` |
| 一句话定位 | 基于大模型的系统知识拆解工具套件：资料 + 用户系统描述 → 需求/组成/架构/流程四视图 → 系统规格说明 |
| 标准轮廓 | GJB 2786A / GJB 438C（文档结构与研制要求）+ ISO/IEC/IEEE 29148（需求属性）+ SysML v2（结构化描述） |
| 适用领域 | 机载/航天装备、信息系统、软件系统（架构层数自适应，四层仅为参考） |

## 2. 总体架构（四层）

```
┌──────────────────────────────────────────────────────────────┐
│ 宿主适配层  opencode Skill / Codex AGENTS.md / 自研 Harness     │ ← 薄封装，只写"怎么指挥工具"
├──────────────────────────────────────────────────────────────┤
│ 门禁编排层  gates.json 状态机 draft→validated→reviewed→approved │ ← 断点续作、人类介入
├──────────────────────────────────────────────────────────────┤
│ 核心工具层  aisi CLI：init/ingest/coverage/research/validate/  │ ← 确定性代码，模型无关
│            decomp辅助/render/export/trace/status/gate          │
├──────────────────────────────────────────────────────────────┤
│ 契约层      JSON Schema（版本化）+ 工件目录规范 + 退出码规范     │ ← 一切输入输出的形式约束
└──────────────────────────────────────────────────────────────┘
  依赖复用：knowledge-base skill（业务知识沉淀与检索）
            extract-sysml-requirements skill（SysML 需求映射经验）
```

**12-Factor 分工**：LLM（宿主 Agent 提供）负责**理解与生成**——产出符合 Schema 的 JSON 草稿；`aisi` CLI 负责**确定性处理**——编号、校验、查重、追踪、落盘、渲染、导出。二者通过 JSON 契约解耦，任何 Harness 只要能执行 shell 命令即可接入（Factor 1/3/4/8/11）。

## 3. 工件目录规范（每系统一个工作区，全 Git 可追踪）

```
systems/<system-id>/
├── manifest.json          # 系统清单（schema: aisi.system.manifest/1）
├── gates.json             # 阶段门禁状态（schema: aisi.gates/1）
├── sources/               # 输入资料登记与抽取文本
│   └── SRC-001.md         #   每来源一文件（原文块 + 定位锚点）
├── research/              # 调研工件（证据不足时启用）
│   ├── gaps.json          #   覆盖率检查产出的证据缺口
│   ├── questions.json     #   调研问题清单（宿主执行搜索）
│   └── findings.json      #   调研结论 + 来源（可沉淀入 knowledge/）
├── views/                 # 四视图结构化数据（核心产物）
│   ├── requirements.json  #   需求视图
│   ├── composition.json   #   组成视图
│   ├── architecture.json  #   架构视图
│   └── processes.json     #   流程视图
├── trace.json             # 四视图追踪矩阵
├── sysml/                 # SysML v2 导出（.sysml，按视图分包）
├── render/                # 图文产物（report.md / diagrams/*.mmd / viewer.html）
└── reports/               # 最终规格说明报告（Markdown，可再导 docx）
```

## 4. 核心数据模型（JSON Schema，均带 `$schema` 版本号）

### 4.1 需求视图 `aisi.requirements/1`（对齐 29148 + GJB 438C）

```jsonc
{
  "schema": "aisi.requirements/1",
  "requirements": [
    {
      "id": "REQ-001",
      "name": "员工资料管理",
      "text": "系统应支持员工基本资料的增删改查……",
      "type": "functional",
      "priority": "必须",
      "verification": "测试",
      "rationale": "来自机关单位人事保密要求",
      "fit_criterion": "演示100条档案增删改查全部成功",
      "source_refs": ["SRC-001#3.1"],
      "parent": "",
      "allocations": [ {"module_id": "MOD-01", "role": "implements"} ],
      "interfaces": ["IF-001"],
      "measures": [ {"metric": "响应时间", "value": "<2", "unit": "s", "condition": "并发100用户"} ],
      "status": "proposed",
      "confidence": "high",
      "clarifications": [ {"question": "档案字段范围？", "answer": ""} ]
    }
  ]
}
```

字段枚举：`type` ∈ functional|performance|interface|data|deployment|safety|security|reliability|usability|environment|operability|constraint（**修订 R1**：2026-08-23 按用户要求增加 deployment 部署需求类型；顶层按类型分组：功能/性能/数据/部署/安全/接口，对齐 GJB 438C 需求规格说明章节结构）；`priority` ∈ 必须|应当|可以；`verification` ∈ 审查|分析|演示|测试；`status` ∈ proposed|confirmed|deferred|rejected；`confidence` ∈ high|medium|low。

### 4.2 组成视图 `aisi.composition/1`

```jsonc
{
  "schema": "aisi.composition/1",
  "modules": [
    {
      "id": "MOD-01", "name": "员工资料管理",
      "kind": "module",
      "parent": "MOD-00",
      "responsibilities": ["员工档案CRUD", "Excel导入导出"],
      "requirements": ["REQ-001"],
      "layer": "LAY-01",
      "provided_interfaces": ["IF-01"],
      "used_interfaces": [],
      "notes": "同一员工可有多条奖惩记录（1:N）"
    }
  ]
}
```

`kind` ∈ subsystem|module|service|component|database|external；`MOD-00` 为系统根，parent 形成包含层级。

### 4.3 架构视图 `aisi.architecture/1`（多层自适应）

**修订 R3**（2026-08-23）：data_assets 与 deploy_nodes 增加 `notes` 字段（承载实体关系、部署注记等信息，与 layers.description/services.notes 对齐）。

```jsonc
{
  "schema": "aisi.architecture/1",
  "layers": [
    {"id": "LAY-01", "name": "应用层", "order": 1, "description": "Vue.js SPA + Element UI",
     "technologies": ["Vue", "ElementUI"], "modules": ["MOD-01"]}
  ],
  "services": [
    {"id": "SVC-01", "name": "RBAC权限服务", "kind": "business",
     "module": "MOD-06", "api": "Spring Security Filter", "scalability": "", "notes": ""}
  ],
  "data_assets": [
    {"id": "DA-01", "name": "员工档案库", "entities": ["Employee", "Reward"],
     "store": "MySQL 8.0", "owner_module": "MOD-01", "sensitivity": "机密",
     "retention": "", "backup": ""}
  ],
  "deploy_nodes": [
    {"id": "N-01", "name": "应用服务器", "hosts": ["SVC-01"], "spec": "2C2G ESC", "protocol": "HTTPS"}
  ]
}
```

层数不固定：数据层/逻辑层/模型算法服务层/应用层仅为参考模板，按系统自适应增减（`order` 排序）。

### 4.4 流程视图 `aisi.processes/1`（工作流 + 数据流 + 接口）

```jsonc
{
  "schema": "aisi.processes/1",
  "processes": [
    {"id": "PRC-001", "name": "员工入职建档", "trigger": "新员工入职", "actors": ["HR", "系统"],
     "steps": [
       {"id": "S1", "actor": "HR", "action": "录入基本资料", "module": "MOD-01",
        "inputs": ["纸质档案"], "outputs": ["DA-01"], "next": ["S2"],
        "exceptions": ["必填缺失→表单校验拦截"]}
     ]}
  ],
  "dataflows": [
    {"id": "DF-01", "from": "MOD-01", "to": "MOD-05", "payload": "员工工资数据",
     "frequency": "月度", "protocol": "内部调用", "interface": "IF-03"}
  ],
  "interfaces": [
    {"id": "IF-01", "name": "登录认证接口", "provider": "SVC-01", "consumers": ["MOD-01"],
     "style": "REST", "protocol": "HTTPS", "contract_ref": "", "messages": [
       {"name": "login", "direction": "request", "fields": ["username", "password"]},
       {"name": "token", "direction": "response", "fields": ["jwt"]}
     ]}
  ]
}
```

### 4.5 追踪矩阵 `aisi.trace/1`（v1 静态生成；v2 升级动态影响库）

边类型：`REQ→MOD`（satisfy 需求由模块实现）、`MOD→LAY`（allocate 模块位于架构层）、`STEP→MOD`（流程步骤由模块执行）、`REQ→STEP`（refine 需求在流程中体现）、`DF/IF→MOD`（数据流/接口连接模块）。

`aisi validate --trace` 完整性 lint（警告不阻断）：孤儿需求（无模块承载）、空模块（无需求）、断链流程步骤（模块不存在）、无来源需求（source_refs 空且非用户新增）、接口无消费方。

> v2 规划（仅记录，本期不实现）：`design.db` 动态库，四视图任何修改自动产生影响提醒（如 REQ-001 变更 → 影响 MOD-01 / PRC-001-S1 / IF-02）。

### 4.6 调研工件 `aisi.research/1`（资料不足时的搜索补足）

**修订 R4**（2026-08-24，M2 实施）：新增两个契约——`aisi.sources/1`（sources/index.json 来源索引：id/title/origin/format/chunks/sha256）与 `aisi.gaps/1`（coverage 产出的证据缺口：kind ∈ NO_SOURCES_INGESTED|NO_SOURCE|UNRESOLVED_SOURCE|OPEN_CLARIFICATION|MISSING_MEASURE，severity ∈ high|medium|low）。ingest 支持 md/txt/html/docx/pdf 抽取与 URL 占位登记（CLI 不联网，正文由宿主抓取回填）；分块锚点格式：文本 `SRC-NNN#L<起>-L<止>`，PDF `SRC-NNN#P<页>`。

```jsonc
{
  "schema": "aisi.research/1",
  "topic": "人事系统数据保密要求",
  "questions": [
    {"id": "Q1", "question": "机关事业单位人事数据的定密与访问控制惯例？",
     "reason": "覆盖缺口：安全类需求无资料支撑",
     "status": "answered",
     "findings": [{"summary": "……", "source_refs": ["WEB-001"], "confidence": "medium"}]}
  ],
  "sources": [
    {"id": "WEB-001", "url": "https://…", "title": "…", "accessed": "2026-08-23", "reliability": "medium"}
  ]
}
```

CLI 本身**不直接联网**（保持可迁移、环境无关，Factor 11）。搜索由宿主 Agent 的搜索工具执行，结果按此 Schema 归档，可选沉淀入 `knowledge/`（`--to-kb`）。

## 5. 工具清单与 I/O 契约

统一约定：输入 = 文件路径或 stdin JSON；输出 = stdout JSON（`{"ok":true,…}` 或 `{"ok":false,"errors":[…]}`）；退出码 `0` 成功 / `2` 契约校验失败 / `3` 门禁拒绝 / `4` 未找到。所有命令幂等、状态全在工件文件（Factor 5/12）。

| 命令 | 输入 | 输出 | 说明 |
|---|---|---|---|
| `aisi init` | `--id --name --domain --profile` | manifest.json | 建工作区 |
| `aisi ingest` | `--file <路径>` | sources/SRC-xxx.md | 资料登记+文本抽取（pdf/docx/md/txt/html），保留章节/页/行锚点 |
| `aisi coverage` | `--view requirements` | research/gaps.json | 证据缺口分析：哪些需求类型/字段无资料支撑 |
| `aisi research plan` | gaps.json | research/questions.json | 生成调研问题清单（供宿主搜索） |
| `aisi research ingest` | findings JSON（stdin） | research/findings.json | 归档调研结论，`--to-kb` 沉淀知识库 |
| `aisi clarify` | `<REQ-ID> --answer <文本>` | requirements.json 更新 | **修订 R2**：回填待澄清项答案；`status` 自动提示未回答项，并提示可启用 research 搜索调研补充（用户要求：资料细节未展开时系统主动询问是否调研） |
| `aisi validate` | 任意视图 json | 校验报告 JSON | Schema 校验 + 追踪 lint + 编号查重；LLM 草稿必须先过此关 |
| `aisi gate` | `review\|approve\|reject\|reset <view> [--comment]` | gates.json 更新 | **人类确认动作**：review=validated→reviewed，approve=reviewed→approved（解锁下一视图），reject=打回 draft（需 comment），reset=强制回 draft（Factor 7） |
| `aisi render` | `--view <v> --format md\|html\|mmd` | render/ 产物 | 报告 Markdown、Mermaid 源码、自包含 HTML 查看器 |
| `aisi export sysml` | views/*.json | sysml/*.sysml | 四视图→SysML v2 包 |
| `aisi trace` | views/*.json | trace.json + 矩阵 md | 追踪关系生成与可视化 |
| `aisi status` | 工作区 | 状态摘要 JSON | 当前门禁、下一步建议、断点信息（Factor 6） |

**LLM 草稿落盘流程**（写入宿主适配层）：生成草稿 JSON → `aisi validate` → 修正循环 → 人工 review 渲染产物 → `aisi gate approve` → 下一视图。

## 6. 阶段门禁状态机

```
ingest ──→ requirements ──→ composition ──→ architecture ──→ processes ──→ report/sysml
              │                │                │               │
          draft→validated→reviewed→approved（每视图四态）
              │  reject 打回 draft（comment 记入 gates.json）
+ research 循环：coverage 缺口 → 调研 → 补充草稿（任意阶段可触发）
```

- 每视图四态：`draft`（LLM 生成）→ `validated`（过 schema+lint）→ `reviewed`（人类看渲染产物）→ `approved`（gate 确认）。
- 门禁动作：`aisi validate` 完成 draft→validated；`aisi gate review` 完成 validated→reviewed；`aisi gate approve` 完成 reviewed→approved；`aisi gate reject --comment` 打回 draft。
- 前一视图 `approved` 才能开始下一视图（validate 拒绝，退出码 3）；`--force` 可越级但记录原因。
- 断点续作：状态全在 gates.json，`aisi status` 输出恢复指令。

## 7. SysML v2 映射规则（导出器规格）

| 视图数据 | SysML v2 构件 | 规则 |
|---|---|---|
| requirement | `requirement <'REQ-001'> name { doc /* text */ }` | 嵌套表达 parent；measures → attribute 注释；allocations → satisfy 注释 |
| module | `part def` + 嵌套 part | parent→嵌套；kind→构造型注释 |
| layer/service | 分层 `package` + `item def`（数据资产） | package 嵌套，层数自适应 |
| process step | `action def` / `activity` | next 多目标→分支；数据流→flow |
| interface | `interface def` + port | messages→item 字段 |

标识符英文 camelCase，中文进 `doc /* */`（沿用现有 skill 成熟规则）。

## 8. 黄金样例映射（HR 管理系统，用户提供的设计报告）

| 样例内容 | 视图落点 |
|---|---|
| 六大模块：通讯/资料/考评/奖惩/培训/薪资/统计/系统管理 | composition：MOD-00 根 + 各子系统 → 子模块 |
| RBAC 访问控制、角色菜单权限、操作日志 | requirements（安全类）+ processes（访问控制流程含鉴权异常分支）+ architecture（SVC 权限服务） |
| MVVM 前后端分离、Spring Boot/Vue/MySQL、B/S | architecture：layers + technologies + deploy_nodes |
| 业务流：建档→调动→辞职→工资管理 | processes：多端到端流程，steps 带 module/inputs/outputs |
| 员工 1:N 奖惩、1:1 在训 | composition.notes + data_assets.entities 关系 |
| 38MB 部署、2C2G、多浏览器兼容 | requirements（性能/环境类，measures 数值+单位） |

## 9. 12-Factor 合规映射

| Factor | 落地方式 |
|---|---|
| 1 自然语言→工具调用 | LLM 只产出 Schema JSON；CLI 确定性执行 |
| 2 Own your prompts | 提示词全在 Skills/适配层文件，Git 版本化 |
| 3 Own your context window | ingest 分块带锚点；按需加载，不整篇塞上下文 |
| 4 工具即结构化输出 | 全命令 JSON in/out + 版本化 Schema |
| 5 执行态=业务态 | gates.json / views/*.json 即全部状态 |
| 6 Launch/Pause/Resume | aisi status 输出精确恢复点 |
| 7 用工具调用联系人类 | aisi gate 即人类确认点 |
| 8 Own your control flow | 阶段顺序 CLI 强制，Agent 不可跳过 |
| 9 错误压缩进上下文 | validate 错误结构化：字段+路径+修复建议 |
| 10 小而专注 | 每命令单一职责，四视图独立生成校验 |
| 11 Trigger from anywhere | shell 可调即可用，三宿主统一接入 |
| 12 无状态 reducer | 所有命令幂等，状态即文件 |

## 10. 实施计划（G0 通过后）

| 里程碑 | 内容 | 验收 |
|---|---|---|
| M1 | 6 个 JSON Schema + validate + init + status + gate | Schema 自校验 + 单测 |
| M2 | ingest + coverage + research 三命令 | HR 样例资料导入出缺口清单 |
| M3 | HR 样例四视图草稿过 validate | trace 完整性 lint 全绿 |
| M4 | render（md/mermaid/自包含HTML）+ export sysml | HR 样例四图 + .sysml 可读 |
| M5 | 规格说明报告骨架 + opencode/Codex 适配层 | 端到端演示 |

## 11. 待确认小项（不阻塞，默认值已给出）

1. 包名/命令名：默认 `aisi` / `aisi-toolkit`；
2. GJB 标准子集：**已确认按 GJB 2786A + GJB 438C** 组织文档骨架，做成可替换 profile（`--profile gjb438c|gb8567|custom`）；
3. 输出语言：默认中文交付（SysML 标识符英文、doc 注释中文）；
4. Mermaid 转图片：默认零依赖自包含 HTML（浏览器打开即渲染、可导出 PNG）；若本机有 `mmdc` 则额外直接输出 PNG/SVG。
