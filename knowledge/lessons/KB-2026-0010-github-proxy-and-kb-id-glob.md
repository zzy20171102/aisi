---
id: KB-2026-0010
type: lesson
title: 两个实战坑：GitHub 推送代理切换策略 + KB 编号 glob 不匹配带后缀文件名
tags: [git, proxy, knowledge-base, glob, workflow]
source: 2026-08-24 实战调试记录
created: 2026-08-24
status: active
supersedes: ""
confidence: high
---

## 内容

### 坑 1：GitHub 推送时通时断

现象：直连 github.com:443 间歇性超时/SSL reset；本地 Clash 代理（127.0.0.1:7890）时开时关。

**可复用处理流程**：
1. 推送失败先 `netstat -ano | findstr LISTENING | findstr ":7890 :7897 :10809 :1080"` 检测代理端口
2. 有代理：`git config --global http.https://github.com.proxy http://127.0.0.1:7890`（仅对 github.com 生效，不污染其他 git 操作）后 push
3. 无代理且直连失败：本地 commit 无风险，等网络恢复；重试 2-3 次仍失败即停止，勿死循环
4. 代理关闭后记得 `git config --global --unset http.https://github.com.proxy` 切回直连，否则 connection refused

### 坑 2：glob `KB-????-????.md` 匹配不到带后缀文件名

现象：知识库文件命名 `KB-2026-0001-file-based-knowledge-store.md`，glob 模式 `KB-????-????.md`（要求问号后紧跟 .md 结尾）匹配不到 → 编号扫描返回 0 → 自动生成 ID 与现有条目冲突（KB-2026-0001 重复，kb.py save 时会静默覆盖旧条目）。

**教训**：
1. glob 问号是精确的单字符通配，`????.md` 隐含"以 .md 紧跟结尾"的语义——**生成带后缀文件名时不要用定长 glob 扫号**
2. 正确做法：`rglob("KB-*.md")` + 正则 `^KB-\d{4}-(\d{4})` 提取编号（research.py 与 kb.py 已修复）
3. 自动分配 ID 的代码必须有"已占用检测"，冲突宁可报错也不要静默覆盖

## 适用场景

本机推送 GitHub 失败时；任何涉及文件名模式扫描与自动编号的代码（知识库/工作区/SRC 编号）。
