---
name: extract-sysml-requirements
description: 从系统设计文档或系统需求设计文档（docx/pdf/md/txt/html）中抽取详细需求，规范化为需求清单表格（Markdown + Excel），并生成 SysML v2 文本表示法的需求图代码（.sysml）。Use when the user asks for 需求抽取、需求提取、需求规格、需求点表格、需求清单、SysML需求图、需求图代码, or English equivalents like extract requirements, requirements table, SysML requirement diagram.
---

# 需求抽取并生成 SysML 需求图（SysML v2）

本 skill 的输入是一份系统设计文档或系统需求设计文档；输出三件套：

1. `requirements.md` — 需求清单 Markdown 表格 + 统计摘要
2. `requirements.xlsx` — 需求清单 Excel（带格式、筛选、统计页）
3. `requirements.sysml` — SysML v2 文本表示法需求图代码（可在 SysML v2 工具中渲染为需求图）

## 工作流程

### 第 1 步：定位并读取输入文档

先确认用户给出的输入文件路径。按扩展名选择读取方式：

| 扩展名 | 读取方式 |
| ------ | -------- |
| `.md` `.txt` `.text` | 直接用 Read 工具读取全文 |
| `.docx` | 用 pandoc 转 Markdown：`pandoc <input.docx> -t gfm -o <tmp>.md`，或 Python：`uv run python -c "import docx; print('\\n'.join(p.text for p in docx.Document(r'<path>').paragraphs))"`（表格用 `docx.Document` 的 `tables`） |
| `.pdf` | Python pypdf：`uv run python -c "from pypdf import PdfReader; print('\\n'.join((p.extract_text() or '') for p in PdfReader(r'<path>').pages))"` |
| `.html` `.htm` | pandoc 转 Markdown 后读取 |
| `.xlsx` | Python openpyxl 逐行读出单元格 |

> **项目规范**：本项目的所有 Python 命令与脚本一律通过 `uv run python ...` 在项目虚拟环境（`.venv`，由 `pyproject.toml` / `uv.lock` 管理）中执行，不直接使用系统 `python` / `pip`。

若文档很长（>2000 行文本），分块读取，不要遗漏任何章节。**保留来源定位信息**（章节号 / 页码 / 段落号 / 表格行号），后续每个需求都要记录来源。

### 第 2 步：识别需求候选句

从文本中找出"约束性陈述"。优先关注：

- **情态动词/关键词**：中文「必须 / 应 / 应当 / 须 / 需要 / 不得 / 不允许 / 要求 / 指标 / 约束 / 接口」；英文「shall / must / should / will / required / shall not / must not」。
- **章节标题**：如「需求分析」「功能需求」「性能需求」「接口要求」「约束条件」「非功能需求」等小标题下的内容。
- **编号列表**：`1) 2)`、`a) b)`、`(1) (2)`、`1.1.1` 等。
- **表格**：带「需求 / 要求 / 指标 / 描述」列的表格，逐行抽取。

区分"需求"与"背景描述"：叙述性背景、目的、范围说明、设计理由等**不算需求**，不要抽取。只有可验证的约束性陈述才算需求。

### 第 3 步：规范化每条需求

对每条候选需求做以下整理：

1. **补充主语**：如果句子省略主语（如「应支持并发」），根据上下文补全系统/模块名（如「系统应支持并发」），并记录在案。
2. **拆分复合句**：一个句子含多个独立约束时拆成多条需求。
3. **量化指标单列**：含阈值/单位/条件的（如「≥ 10 km/L」「响应时间 < 100 ms」）尽量保留原始数值与单位。
4. **分配字段**，每一条需求一个对象：

```
{
  "id": "REQ-001",
  "name": "短名称（凝练短语）",
  "type": "功能需求|性能需求|接口需求|约束|物理需求|运行/环境需求|安全需求|其他",
  "priority": "必须|应当|可以",
  "source": "章节号/页码/段落号",
  "text": "完整需求正文（保留原文语义，可微调补充主语）",
  "verification": "审查|分析|演示|测试",
  "parent": "父需求编号（无则留空）"
}
```

- **ID 规则**：顺序编号 `REQ-001`、`REQ-002`…；有父子分解时用层级编号 `REQ-001`、`REQ-001.1`、`REQ-001.2`。
- **类型**：从下列取值中选最贴切的一个，拿不准归「其他」。
- **优先级**：原文出现「必须/shall/must」→ `必须`；「应当/should」→ `应当`；「可以/could/may」→ `可以`；无明确情态词时按上下文判断，拿不准标 `应当`。
- **验证方法**：根据需求性质推断——可测试的量化指标→`测试`；静态结构/可追溯性→`审查`；需仿真或计算→`分析`；需操作演示→`演示`。

**整理为一个 JSON 数组**（保留原始顺序），示例：

```json
{
  "title": "某系统需求",
  "source": "系统设计文档.docx",
  "requirements": [
    {
      "id": "REQ-001",
      "name": "并发支持",
      "type": "功能需求",
      "priority": "必须",
      "source": "3.1.1",
      "text": "系统应支持并发处理至少 100 个用户会话。",
      "verification": "测试",
      "parent": ""
    },
    {
      "id": "REQ-002",
      "name": "响应时间",
      "type": "性能需求",
      "priority": "必须",
      "source": "4.2",
      "text": "系统对查询请求的响应时间应小于 100 ms。",
      "verification": "测试",
      "parent": "REQ-001"
    }
  ]
}
```

> 提示：将上述 JSON 写入临时文件（如 `C:\Users\ZHENYU~1\AppData\Local\Temp\opencode\requirements_data.json`），后续 Excel 生成与 .sysml 生成都基于它，避免手动转录出错。

### 第 4 步：输出 1 — Markdown 需求表格（requirements.md）

生成 `requirements.md`，结构：

1. 文档标题与元信息（来源文档、抽取日期、需求总数）。
2. 汇总统计：按类型计数、按优先级计数（简短）。
3. 需求清单表格，列为：

```
| 需求编号 | 需求名称 | 需求类型 | 优先级 | 来源 | 需求内容 | 验证方法 | 父需求 |
```

- 若需求量很大，先按「需求类型」或文档章节分小节，每节一个子表。
- 需求内容列保留完整原文。

### 第 5 步：输出 2 — Excel 需求清单（requirements.xlsx）

用随本 skill 附带的脚本生成，样式统一（表头蓝色、冻结首行、筛选、斑马纹、统计页）：

```powershell
uv run python ".opencode\skills\extract-sysml-requirements\generate_excel.py" "<data.json>" -o "requirements.xlsx"
```

- 脚本输入为第 3 步的 JSON（含 `title` / `source` / `requirements`）。
- 脚本输出两个工作表：`需求清单`（主表）与 `需求统计`（按类型/优先级/验证方法计数）。
- 若 `openpyxl` 未安装：`uv add openpyxl`。

### 第 6 步：输出 3 — SysML v2 需求图代码（requirements.sysml）

生成标准 SysML v2 文本表示法文件。核心语法依据 OMG SysML v2 正式规范（7.21 Requirements 与官方示例 `SysML-v2-example.sysml`，见项目根目录，也可参考 `SysML-2.0-Language.pdf`）：

**语法要点：**

- 需求用 `requirement` 关键字声明；需求 ID 用短名 `<'1.1'>` 写在名字前；需求正文写在 `doc /* ... */` 注释里（这是官方要求的"非正式文本"写法）。
- 需求按类别/章节用**嵌套 requirement** 形成包含（containment）结构，父需求自动包含子需求。
- 量化需求可在 body 中加 `attribute` 绑定，如 `attribute redefines massRequired = 2000 [kg];`（非必需）。
- 派生关系用 `#derivation connection`，需 `public import RequirementDerivation::*;`。

**模板：**

```sysml
package <PkgName>Requirements {
    // 基础库导入（保持与官方示例一致的风格）
    public import Definitions::*;
    public import ISQ::*;
    public import RequirementDerivation::*;   // 仅当用到 #derivation connection 时需要

    requirement <'0'> <PkgName>Requirements {
        doc /* <文档名> 需求集合 */

        requirement <'1'> functionalRequirements {
            doc /* 功能需求 */
            requirement <'1.1'> <camelName> {
                doc /* <需求正文> */
            }
            requirement <'1.2'> <camelName> {
                doc /* <需求正文> */
            }
            // ...
        }

        requirement <'2'> performanceRequirements {
            doc /* 性能需求 */
            requirement <'2.1'> <camelName> {
                doc /* <需求正文> */
                // 可量化的性能需求可加：
                // attribute redefines <param> = <值> [<单位>];
            }
            // ...
        }

        requirement <'3'> interfaceRequirements {
            doc /* 接口需求 */
            // ...
        }

        // 其余类别：约束 / 物理 / 运行环境 / 安全 ...
    }

    // 派生关系示例：高层需求 -> 其细化/分解出的子需求
    // #derivation connection {
    //     end #original ::> <PkgName>Requirements.<父需求>;
    //     end #derive ::> <PkgName>Requirements.<子需求>;
    // }
}
```

**命名与编码规则：**

- `<PkgName>`：由文档标题派生，PascalCase（如 `AviationWarningSystem`）。
- 需求标识符（`<camelName>`）：用英文 camelCase 概括需求含义（如 `concurrencySupport`、`responseTimeLimit`），**不要把中文直接当作标识符**；中文内容全部放进 `doc /* */` 注释。
- 短名 `<'0'>`、`<'1'>`、`<'1.1'>` 即需求 ID，与 Excel/Markdown 的编号对应（`REQ-001` 可用 `<'1'>` 简化表达；若表格用层级编号，保持层级一致）。
- 每个需求 body 至少包含一个 `doc /* ... */` 注释，内容为需求正文。
- 派生关系按文档中的"分解 / 细化"关系补充；若文档没有明确的父子分解，可省略。

**生成步骤：**

1. 按类型分组：功能、性能、接口、约束、物理、运行/环境、安全、其他 → 每个组一个嵌套 requirement。
2. 遍历第 3 步 JSON，把每条需求映射为 `requirement <'编号'> <camelName> { doc /* ... */; }`。
3. 有 parent 关系的需求之间，在组内形成嵌套（子需求直接写在父 requirement 的 body 内）。
4. 需要时添加 `#derivation connection` 块。
5. 写入 `requirements.sysml`（UTF-8 编码）。

### 第 7 步：验证与交付

1. 检查 JSON、Markdown、Excel、.sysml 中需求**数量一致**（编号不重不漏）。
2. 简单校验 .sysml：括号/分号配对，`requirement <'..'> name { ... }` 结构完整。
3. 告知用户三件套输出路径；建议用 SysML v2 工具（如 SysON https://sysml2.systems 、openCAESAR 等）打开 `requirements.sysml` 渲染需求图。
4. 若需求抽取量大，提醒用户复核 `type / priority / verification` 字段的自动判断结果。

## 注意事项

- 不要杜撰需求：文档没有的内容不要添加；语义含糊的句子可标注 `[待澄清]` 并保留原文。
- 保留数值与单位原文，不要在需求正文中改写数值。
- 来源定位尽量精确（章节号 / 页码 / 表格行号），便于追溯。
- 中文文档用中文写需求正文，Markdown/Excel 内容为中文；.sysml 标识符用英文。
