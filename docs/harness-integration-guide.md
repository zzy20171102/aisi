# 自研 Harness 接入指南

> 目标：任何能执行 shell 命令、解析 JSON 的智能体编排系统，无需改动核心即可接入 aisi 工具套件。

## 1. 接入三原则（12-Factor 映射）

| 原则 | 实践 |
---|---|
| **工具即契约** | 只通过 `aisi` CLI 交互（JSON stdout + 退出码），不 import 内部模块、不读内部状态文件做业务判断（gates.json 例外：断点展示用） |
| **状态即文件** | Harness 不缓存阶段状态；每次决策前调 `aisi status` 重新获取 |
| **人类在环** | `gate review/approve/reject` 是人类专属动作；Harness 只在用户确认后调用，并把用户意见写入 `--comment` |

## 2. CLI 契约

- 调用：`<python> -m aisi <command> [--path <workspace>]`（workspace 缺省自动发现 `systems/` 下唯一系统）
- 输出：stdout 一律 JSON（UTF-8，`ensure_ascii=False`）：成功 `{"ok": true, ...}`；失败 `{"ok": false, "errors": [{code, message, path?, suggestion?}]}`
- 退出码：`0` 成功｜`2` 契约失败（修正后重试）｜`3` 门禁拒绝（勿绕过，转人类）｜`4` 未找到（先 init/ingest）
- 完整命令表见 `docs/contracts/aisi-toolkit-contract-v0.md` §5 或 `--help`

## 3. 编排状态机（Harness 侧实现）

```
IDLE ──init/ingest──→ READY
READY ──coverage──→ {无缺口→GEN_VIEW; 有缺口→ASK_RESEARCH}
ASK_RESEARCH ──用户同意──→ RESEARCH_LOOP(plan→宿主搜索→ingest→clarify) ──→ READY
GEN_VIEW: LLM按Schema生成草稿JSON → aisi validate
   ├─ exit 2 → 修正循环（最多 N 轮，错误喂回 LLM）
   └─ exit 0 → HUMAN_REVIEW（渲染摘要给用户）
HUMAN_REVIEW: 用户"通过"→ gate review+approve → 下一视图 or DELIVER
              用户意见 → gate reject --comment → GEN_VIEW
DELIVER: trace → export → render → 报告产物路径给用户
```

断点恢复：任意时刻崩溃/重启后，调 `aisi status`，按 `next_view` + `next_action` + `open_clarifications` 恢复。

## 4. 人机介入点（必须暂停等人类）

1. **视图批准**：validated 之后（gate review/approve 前）
2. **调研授权**：coverage 出现缺口后（是否启用 web 搜索）
3. **越级授权**：任何 `--force` 使用前

## 5. 上下文策略（Factor 3）

- LLM 生成视图草稿时，**只加载**：对应 schema + 上一视图 JSON + coverage 报告 + source_refs 锚点命中的资料分块（`sources/SRC-xxx.md` 中 `<!-- chunk N | anchor: ... -->` 定界）
- 单次上下文超过预算 → 让 LLM 先输出视图的骨架（分组节点），再逐组填充

## 6. 最小集成示例（Python）

```python
import json, subprocess

def aisi(*args, path="systems/my-system"):
    r = subprocess.run([".venv/Scripts/python.exe", "-m", "aisi", *args, "--path", path],
                       capture_output=True, text=True, encoding="utf-8")
    out = json.loads(r.stdout or "{}")
    if r.returncode == 3:   # 门禁拒绝 → 转人类
        ask_human(out["errors"])
    elif r.returncode == 2: # 契约失败 → 喂回 LLM 修正
        return {"retry": out["errors"]}
    return out

st = aisi("status")                      # 断点
while st["next_view"]:
    draft = llm_generate(schema_for(st["next_view"]), context(st))
    save(f"views/{st['next_view']}.json", draft)
    v = aisi("validate", "--view", st["next_view"])
    if v["ok"] and human_approves(render_summary(v)):
        aisi("gate", "review", st["next_view"])
        aisi("gate", "approve", st["next_view"], "--comment", human_comment())
    st = aisi("status")
aisi("trace"); aisi("export"); aisi("render", "--format", "all")
```

## 7. 接入检查清单

- [ ] 能执行 shell 并捕获 stdout/exit code
- [ ] JSON 解析与 UTF-8 处理
- [ ] 实现三处人机暂停点（§4）
- [ ] exit 2 自动修正循环 + exit 3 转人工
- [ ] 断点恢复（启动时调 status）
- [ ] web 搜索工具（供 research 循环调用，结论按 `aisi.research/1` 回填）
