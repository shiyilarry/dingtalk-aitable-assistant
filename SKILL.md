---
name: dingtalk-aitable-assistant
description: 钉钉AI表格三场景助手（搭建/同步/审计）。This skill should be used when 用户想在钉钉AI表格（多维表格/Base）上「建一个管理表并搭好字段结构、把本地 Excel/CSV 计算结果同步进已有表（含增量/覆盖/补列）、或对已有表格做只读审计优化」，或明确提到 @dingtalk-aitable-assistant、dws、aitable、多维表格、AI表格、建表、同步数据、审计表格、看板数据同步。
agent_created: true
version: 1.0.0
dws_cli_version: ">=1.0.61"
requires_upgrade_gate: true
---

# 钉钉AI表格助手（dingtalk-aitable-assistant）

面向 **非 IT 同事**（Windows + WorkBuddy）的三场景助手，用大白话完成钉钉 AI 表格的搭建、同步与审计。所有命令通过官方 `dws`（dingtalk-workspace-cli）执行。

**权威信息链（从高到低，冲突时以上层为准）**：
1. **运行时真值**：`dws schema --all` / `dws schema --cli-path "<leaf>"` / `dws <命令> --help`（永远最新，且每次升级后自动跟随版本变化）；
2. **官方文档源（本机自带、随 dws 升级自动更新）**：`~/.agents/skills/dingtalk-aitable/`（SKILL.md + 42 个 references）——**遇到任何"这个能不能做 / 参数怎么写"，先读这里**，不要凭记忆或猜测；
3. 本 SKILL 的 `references/dws_command_ref.md` 与场景文档（沉淀了实测口径、平台坑与踩坑记录）；
4. 官方仓库 `github.com/DingTalk-Real-AI/dingtalk-workspace-cli`（源码，用于理解行为，**不以它判断能力有无**——main 领先发布版）。

> **自给自足原则（最高优先级）**：SKILL 必须独立解决 90%+ 场景问题。**不得把"需要用户懂技术来配合"设计进流程**——用户不需要知道 dws、不需要知道 GitHub、不需要手工建样例。凡是需要"请用户帮忙验证/手工操作"的，先自问能否用上面第 1、2 层的权威信息自己解决；确实必须用户目视确认的（如平台渲染类缺陷），一次性做成 SKILL 规则，后续同类场景不再打扰用户。

## 0 · 使用边界与安全（每次先读）

- **零破坏铁律**：未经用户点选/批准，不修改现有 Base/Table/字段/记录；不做删除、清空、改名。写操作只发生在用户明确批准的目标表上。
- **敏感与脱敏**：输出与日志中不出现真实项目名/ID/财务明细/品牌名等（示例一律用"示例××"）；Excel 单号类列以字符串写入（防科学计数法）。
- **CLI 能力边界（做不到就明说）**：**唯一权威＝运行时实测**（`dws schema --all` / `dws schema --cli-path "<leaf>"` / `dws <命令> --help`）。父级 `--help` 会漏列子命令，**不可作为能力清单**。已知（2026-09-10 实测 v1.0.61；本机 2026-10-15 已升 v1.0.62）：建表/字段/记录/关联/filterUp 查找引用/视图全属性（filter·sort·group·aggregate 含 DISTINCT·frozen-cols·row-height·fill-color-rule）/仪表盘/图表/section/表单基础/`workflow`（自动化 DSL 可 CLI 建）；**仍 UI 专属**：公式字段创建、按钮字段、OCR、单选「同步其他表选项」。**升级后必须重新落 schema 快照**，能力清单以新版为准。
- **触发说明（保守原则）**：本 Skill 只对「与钉钉 AI 表格强相关」的表达自动唤醒；同事也可直接输入 `@dingtalk-aitable-assistant` + 需求来显式调用，避免歧义词（如"台账"）被其它场景抢答。

## 1 · 执行主流程（六段式 P0–P5）

每次任务按下述原子能力流水线执行，不许跳段：

1. **P0 环境与登录**（分两小步，**都不需要用户参与**）：
   - **P0.0 版本前置（每日首次必做）**：跑 `scripts/daily_upgrade_gate.ps1`（当天已检查过会秒退，exit 0）。解读退出码——`10`＝已升级到新版本：随即 `dws schema --all -f json` 落盘、与上一份快照 diff，把**新增/变更的 leaf 命令与参数**纳入本次任务可用能力，并在首条回复里用一句话告知用户"dws 已更新 x.y.z，新增 N 项能力"；`0`＝已是最新（继续）；`3/4`＝升级未成功或离线（**不阻断**，按当前版本继续，仅提示一次）。升级日志在 `%USERPROFILE%\.workbuddy\dws_upgrade.log`。
     > 为什么必须做：钉钉随时可能发布新版 dws（新增命令/参数/枚举）。不主动升级，SKILL 就会用旧命令硬凑——这是"能力缺口"的头号来源。**用户不会知道有新版本，也不需要知道。**
   - **P0.1 环境与登录**：PowerShell 执行 `scripts/env_check.ps1`（或按 references/dws_command_ref.md 手动分步）；**一切执行环境约定遵守 `references/exec_env_windows.md`（铁律）**。dws 未装→`scripts/install_dws.ps1`（安装成功后会自动接一次升级）；未登录→引导授权（`dws auth login` 或 `--device`）。
   - **P0.2 看板无头会话（摆脱人工依赖的关键，2026-09-10 实证）**：`scripts/dashboard_session.py`
     - 姿势：`playwright.chromium.launch(channel="chrome", headless=True, args=["--disable-blink-features=AutomationControlled"])` + `new_context(storage_state=~/.workbuddy/dingtalk_state.json)`。**必须 channel="chrome" + 反检测参数**（否则钉钉跳登录页）；**禁用 agent-browser**（本机启动卡死）。
     - 能力：① **自动打开盘页 = 建立 UI 会话窗口**（无需用户打开/停留）；② **`reload()` 续窗**——实测刷新后单窗可连写 **5/5**，`write()` 已内置"每 4 笔自动 reload"；③ **截图回传**供 AI 读图自检（`shot()`）。
     - 用途：建盘/改盘/交付前自检全流程无人值守；**用户不再需要"刷新停留/截图/描述现象"**。
     - 首次准备：`scripts/login_dingtalk.py` 登录一次（弹窗扫码），登录态归档 `~/.workbuddy/dingtalk_state.json`，长期复用（同 dws 采集项目的 `login_state.json` 模式）。
     - **适用范围**：**看板的所有写操作**（`chart create/update/delete`、`dashboard` 改）**都要在会话窗口内**；无窗口时表现为"首笔可写、随后 `DASHBOARD_STORAGE_NOT_READY`"。
     - ⚠️ **就地改布局的坑与绕开（2026-09-10 实证）**：既有盘上调布局若报 `Dashboard layout item changed concurrently`（该行超载时服务端视为"重排中"），**重试无效**；改用 **「`chart get` 存配置 → `chart delete` → `chart create --layout` 按目标位置重建」**（盘 ID 不变、配置无损，实测删 9/9、重建 6/6 成功）。详见 `references/dws_command_ref.md`。
     - **决策规则**：盘已被自动化/开放平台 API/分享引用 → **就地改**；全新盘或确认无外部引用 → **整盘重建**。
2. **P1 意图路由**：按描述/触发词归类到 场景一（搭建）/场景二（同步）/场景三（审计）；难以判断时先追问，不臆测。
3. **P2 场景执行**：进入对应 `scenarios/scenario_0X_*.md` 按其子阶段执行，逐段推进，每段结束做 🔴 检查点。
4. **P3 交付物**：方案类（场景一）产出**单一项目设计方案 HTML 档案**（演进式：设计→评审→实施→验收全生命周期在同一文件内推进，状态徽章 评审中→已确认→实施中→已交付，结构见 report_style_guide §2）、同步报告 HTML（场景二，简洁任务性小报告）、审计报告 HTML（场景三，评级总览置顶，结构见 guide §3）；**不再拆分**"评审稿/交付验收"独立 HTML。渲染一律遵守 references/report_style_guide.md（锁定版 v2.0，含 Tailwind v4 构建链与常规中文措辞）。报告存放于用户工作目录，文件名 `YYYYMMDD_<主题>_设计方案.html` / `_审计报告.html` 固定演进。
5. **P4 自检**（**必须由 SKILL 自己完成，不得把校验责任推给用户**）：
   - **结构校验**：字段类型/键集（chart config 对照 `chart widgets-example` 真实键集）/字段归属/布局 `i` 映射/幂等；
   - **数据校验（服务端独立复算）**：用 `record stats`（不分组）或 `record group-stats`（分组/去重）**独立算出"每个图表应有的数值清单"**，与图表口径逐项对照——**绝不用自己的脚本口径验证自己**；
   - **可编辑性校验**：新盘图表类型须按 UI 生成形态写全键集（见 references/dws_command_ref.md 的 HISTOGRAM 规则）；
   - **布局收尾**：建盘/改盘后必调 `dws aitable dashboard arrange` 归一化（服务端 layout 合规 ≠ UI 呈现无留白）；
   - 未过不交付。**用户目视仅作最终抽检**（非必经环节）。
6. **P5 复盘进化**：任务收尾按 `evolution/rules.md` 判定 T1/T2/T3 触发；产生候选经验卡→展示给用户→经确认才落地（备份→写入→CHANGELOG→版本+1）。

## 2 · 关键语法速记（2026-09 实测，dws v1.0.61+）

- 字段对象固定为 `{"fieldName":"...","type":"...","config":{...}}`；**不是** `name/property`。
- 建表/加字段单次 ≤15 个；records 单批 ≤100（超长用 `--records-file`）。
- 写记录 cells 的 key 是 **fieldId**（`dws aitable field list` 获取）；singleSelect 按选项名写；number 收数字或数字字符串；date 写 `"YYYY-MM-DD"`。
- 只读字段（filterUp/lookup/公式/系统字段）不可通过 record create/update 写入。
- 删除类命令（record delete 等）不可逆：需 `--yes`、单批≤100、先快照备份。
- 更多见 references/dws_command_ref.md、references/aitable_field_types.md。

## 3 · 场景路由表

| 用户表达 | 场景 |
|---|---|
| 建/搭一个 XX 表（含一句话模糊需求） | 场景一 |
| 把本地 Excel/计算结果同步/导入/刷新到某表 | 场景二 |
| 看看/分析/审计/优化这个表，或对照需求文档评估 | 场景三 |
| 同步后再把子表/看板一起更新 | 场景二（含派生子场景，见 scenario_02） |

## 4 · 常见分支（详见 references/error_handling.md）

- 未指认目标表 → 不写；列出可选表请用户确认。
- 字段缺失/类型不符 → 场景内按「确认→补列/降级 text→提示」流程。
- API 限流/超时 → 等待后重试（≤3 次），不无限重试。
- 认证失败 → 停止业务命令，走授权诊断，不反复重试。
