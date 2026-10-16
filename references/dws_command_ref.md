# dws AI表格命令参考（v1.0.61–1.0.62 实测口径 · 2026-10-15 更新）

> 原则：命令与参数以 `dws aitable --help` / `dws aitable <资源> <动作> --help` / `dws schema` **实测为准**；本表只是常用速查。

## ★ dws 版本与权威命令面（2026-09-10 核实，SKILL 前置必读）
- **权威命令面 ＝ `dws schema --all -f json`**（本机 **v1.0.61：全部 1298 个 leaf，其中 `aitable` 228 个**；对比 v1.0.55 的 840/145，一次升级净增 **83 个 aitable 能力**）；单条参数用 `dws schema --cli-path "aitable <leaf>" --compact -f json`。**不要靠父级 `--help` 推断能力有无**（help 会漏列已注册命令）。
- **本机 v1.0.61（2026-09-10 升级后实测）具备**（在 v1.0.55 基础上净增 83 项）：base(search/get/create/update/delete/copy/**bootstrap**/get-primary-doc-id/schema-snapshot)、table(get/list/create/update/delete/**copy/bootstrap**)、field(list/get/create/update/delete/search-options)、record(query/list/get/create/update/delete/batch-update/**upsert**/**upsert-by-key**/**bulk-patch**/query-empty/history-list/share-url/primary-doc-get/create、**`record stats`（不分组聚合）**、**`record group-stats`（分组/去重聚合）**)、view(list/get/create/**update**/delete/duplicate/lock/**preset-apply**/set-frozen-cols/set-row-height/set-fill-color-rule + filter·sort·group·aggregate·card·timebar·visible-fields·field-widths·name)、form(list/get/create/update/delete + field list/update/hide + questions + share)、dashboard(get/create/update/delete/**arrange**/config-example/share get/update)、chart(get/create/update/delete/widgets-example/share get/update)、**workflow(create/update/get/list/enable/disable/run/history/edit-example ＋ `+workflow-deploy/enable/disable/get/list` 快捷命令) = 自动化可 CLI 建**、**datasource(审批同步：create/update/get-config/get-fields/list-sources/sync/sync-status)**、**advperm role-create/update/get/delete/list + enable/disable**、section(create/delete/rename/reorder/move-node)、export data、import upload/data、attachment upload/put/remove、role(*)、url-resolve、template search、info/list/search
- **本机 v1.0.61 仍不具备**（GitHub main 已有、尚未进发布版）：**`psql`（只读 SQL+JOIN）**、`app`（应用模式/Widget）、`+shortcut` 全集中的少部分。→ 判断能力有无**永远以本机 `schema --all` 为准**，不以 GitHub main 为准（main 领先于 npm 发布版）。
- **服务端独立校验通道（v1.0.61 新增，必须用于交付前验数）**：图表数值不再"自己算自己验"，改由服务端聚合复算——
  - `record stats`：整表/过滤后**不分组**聚合。**`statsType` 必须大写**（`SUM`/`COUNT`/`AVG`…），最多 20 项、fieldId 不得重复——**同一 fieldId 的多种 statsType 须拆成多次调用**（同调用内重复报 RC=3，2026-09-23 实证）。
  - 🆕 `record stats` **返回结构（必记，2026-10-01 采纳 EV-202609-46）**：数值路径＝**`data.results[0].results[0].value`**——同名 `results` **两层嵌套**（外层＝聚合结果集，带 `calcVersion` / `dataVersion` / `deltaVersion` 版本水位；内层＝stats 数组）；**解析失败禁 `or 0` 静默兜底**（会把「解析失败」伪装成「行数 0」——最危险方向）；首次使用的子命令先落盘一次原始响应再写解析代码。
  - `record group-stats`：按字段分组或**去重**统计。**`statsType` 自 v1.0.62 起统一为必须大写**（`SUM`/`COUNT`/`DISTINCT`…）——v1.0.61 时曾要求小写（两命令相反），**v1.0.62 实测变更**：小写直接报 RC=3「必须使用大写枚举值」（2026-10-15 实测）——**旧口径已作废**，勿再按「相反」记忆。
  - ⚠️ `group-stats` 的 `groupKeys[].value` 回读常为 `{"dataType":"OBJECT","value":{}}`（**不回选项名**）→ 需靠 `recordCount` 与已知选项分布对照，或按分组顺序对应；需要名字时改用 `record query --filters` 逐组确认。**日期分组同样不回值**（`{"dataType":"DATE"}`）——分组值回读不可靠为跨类型通例（选项 / 日期均不回，2026-10-15 实测）。
  - 实测样例（2026-09-10，快照表）：`record stats --stats '[{"fieldId":"<编码>","statsType":"COUNT"}]'` → **99**（在售SKU数）；`record group-stats --group '[{"fieldId":"<4C颜色>"}]' --stats '[{"fieldId":"<TC近30销量>","statsType":"SUM"}]'` → 三色系数值与图表口径逐项吻合 ✅（具体数值脱敏；2026-10-15 v1.0.62 复测：同口径大写）
- **升级实录（2026-09-10，v1.0.55 → v1.0.61 实操）**：
  - `dws upgrade -y` ＝ 备份旧二进制（`vendor/dws.exe.old` 保留可回滚）→ 下载新二进制 → 原子替换 → **安装/更新官方技能包**；**耗时可达 20 分钟以上（网络慢），中途无输出属正常**（用 `| tail` 更看不到进度）；**判定是否已成功的可靠信号＝`vendor/dws.exe` 的 mtime 变化 + `dws version`**。
  - ⚠️ 升级后会提示「**检测到旧升级器留下的嵌套 Skill；请运行 `dws skill setup --mode multi`**」——**必须补跑这一步**（`dws skill setup --mode multi --yes`，可先 `--dry-run` 看计划）：把 14 个官方 skill（dingtalk-aitable / chat / doc / drive / calendar / todo / wiki / mail / minutes / contact / event / misc / shared / aisearch）平铺到 `~/.agents/skills` 并自动适配本机已检测到的 Agent（codebuddy / qoder / qoderwork / workbuddy…）；同时把对面模式（mono）残留备份到 `~/.dws/skill-backups/<时间戳>/` 再移除。**我们的项目自有 skill（如 `dingtalk-aitable-assistant`）不在受管范围内，不会被清理。**
  - **后续每次 `dws upgrade` 都会按新版官方清单全量覆盖预制 skill**（本地删掉的官方 skill 会被恢复）——这正是 SKILL 保持与官方同步的机制。
  - `dws skill setup` **只认长参数** `--yes`（`-y` 会报 unknown shorthand flag）。
- **每日首次自动升级（SKILL 内置，用户无感）**：`scripts/daily_upgrade_gate.ps1` —— 当天已检查则秒退（戳记 `~/.workbuddy/.dws_daily_upgrade`）；否则 `upgrade --check` → 有新版则 `upgrade -y` → 落 `~/.workbuddy/dws_schema_all.json` 快照；日志 `~/.workbuddy/dws_upgrade.log`。退出码 `10`＝已升级、`0`＝已最新、`3/4`＝失败或离线（不阻断）。**升级后必须重落 schema 快照并与上一份 diff**，把新增/变更 leaf 纳入本次任务可用能力。`install_dws.ps1` 安装成功后会自动接一次该 gate。
- ⚠️ **修正旧结论**：自动化**并非**"CLI 不支持"——`workflow create/update`（DSL `workflow-dsl/v1`）在本版即可用；"无 automation 命令"的说法作废。


## 通用
- **ID 复核铁律（2026-09-23 采纳 EV-202609-22）**：任何 `baseId`/`tableId` **使用前现查复核**（`base list` / `base get` / `table list`）——笔记/记忆里的值可能残缺且肉眼难辨（实测：记录 20 位 vs 真实 26 位、中段缺 6 位，报 `INVALID_BASE_ID`）。遇 `INVALID_BASE_ID` **优先怀疑 ID 残缺**而非权限或网络。现查成本＝一次只读调用，无豁免场景；同名多 Base 时以用户指认 + 结构特征（`field list`）双确认。
- 所有命令加 `--format json` 便于解析。
- 危险写操作用 `--dry-run` 预览；确认后加 `--yes`。
- 超长 JSON（记录/字段）用 `--records-file <文件>` / 建议先写文件再传，避免 Windows 引号与长度问题。

## Base
| 操作 | 示例 |
|---|---|
| 列表 | `dws aitable base list --format json` |
| 创建 | `dws aitable base create --name "客户管理" --format json` |
> 🆕 `base get` 返回含 **`dashboards[]`**（dashboardId / dashboardName / chartCount）——**多盘场景用它列盘**（无 `dashboard list` 子命令；2026-10-15 采纳 EV-202610-05）。

## Table
| 操作 | 示例 |
|---|---|
| 列表 | `dws aitable table list --base-id <BASE_ID> --format json` |
| 创建（≤15 字段） | `dws aitable table create --base-id <ID> --name "订单表" --fields '[{"fieldName":"订单编号","type":"text"},...]' --format json` |
| 结构 | `dws aitable table get --base-id <ID> --table-id <TID> --format json` |

## Field
| 操作 | 示例 |
|---|---|
| 列表 | `dws aitable field list --base-id <ID> --table-id <TID> --format json` |
| 新增（≤15/次） | `dws aitable field create --base-id <ID> --table-id <TID> --fields '[{"fieldName":"8月直播","type":"number","config":{"formatter":"THOUSAND"}}]' --format json` |
| 更新（改名 / 配置；**不可变更字段类型**） | `dws aitable field update --base-id <ID> --table-id <TID> --field-id <FID> [--name "新名"] [--config '{...}'] --format json` |

> ⚠️ `field update` 更新选项（options）为**全量覆盖**（须回传完整列表、已有选项带原 `id`，否则丢数据）→ 校验按「选项名 + 原 id 保留集合 + 数量变化」做；返回 `verified` **仅代表服务端受理**——选项生效在**读侧可见可能滞后分钟级**（EV-202609-41 实测约 1 分钟，复核纪律见 verification-protocol.md §4-I「读后写延迟」条）；**勿以写通道回显 id 比对**（写 / 读通道 id 可能不一致）。

## Record
| 操作 | 示例 |
|---|---|
| 查询（分页 nextCursor） | `dws aitable record list --base-id <ID> --table-id <TID> --limit 100 [--cursor <C>] --format json` |
| 新增（≤100/批） | `dws aitable record create --base-id <ID> --table-id <TID> --records-file ./recs.json --format json` |
| 新增·幂等键 | `--client-token <uuid-v4>`：**只接受合法 UUID v4**（禁派生 / 拼接串）；**多批写入＝逐批各持一个 token 并落盘复用**（超时重跑取同批同 token ⇒ 仍幂等）；**token 与「同一组内容」绑定**——同 token 提交不同内容报 `DUPLICATE_CLIENT_TOKEN`（跨批 / 跨月须换新 token；按内容命名 token 文件）（2026-10-01 采纳 EV-202609-45 ＋ 2026-10-16 采纳 EV-202610-02） |
| 更新（≤100/批，只传要改的字段） | `dws aitable record update --base-id <ID> --table-id <TID> --records-file ./upd.json --format json` |
| 删除（不可逆） | `dws aitable record delete --base-id <ID> --table-id <TID> --record-ids ... --yes`（先快照） |

> CLI `--filters` **不读视图配置**——视图 filter 仅作用于 UI 展示与图表引用层；「CLI 查不到」与「UI 视图不可见」是两条互不相交的链路（复核疑似未落库时先按**非选项列**交叉验证；2026-09-24 采纳 EV-202609-37）。
>
> 🆕 `record query --filters` 过滤 **singleSelect：选项名 / 选项 id 两形态实测均可**（2026-09-28 四组对照实证；勿据 view filter「单选值=id」段落推断「名称无效」）。**「基线 0 行」不得直接进入 create**——先跑「已知有数据的选项值」**对照查询**：对照组命中 ⇒ 0 行可信；对照组也 0 行 ⇒ 过滤器 / 字段 id 有问题，禁止写入（2026-10-01 采纳 EV-202609-47）。

## 写记录 cells 格式
- key = fieldId（不是字段名）；value 见 aitable_field_types.md。
- text→"文本"；number→123 或 "123"；singleSelect→"选项名"（须已存在）；date→"2026-08-01"；user→[{"userId":"xxx","corpId":"xxx"}]。
- 🆕 **置空限制（2026-10-15 采纳 EV-202610-08）**：`record update` **无法用 `null` / 空值清空字段**（报 `INVALID_RECORDS`：must contain at least one writable record）；空值策略＝**不传该字段**（保留原值）或整行跳过；确需「清空」语义时与消费方确认替代方案。

## CLI 能力边界（2026-09-10 v1.0.61 实测更新）
**CLI 已支持（不再走 UI）：**
- 视图：`dws aitable view create/update/delete/duplicate/lock/list`（建网格/看板类视图；筛选排序条件可 CLI 传入）
- 仪表盘：`dws aitable dashboard create/update/delete/arrange/config-example`
  - **写入前置（2026-09-23 口径更新）**：写操作需「UI 会话窗口」；**由 `scripts/dashboard_session.py` 自动打开/续窗，无需用户参与**（详见下方「看板无人值守会话」）；无窗口时仅首笔可写、随后版本链锁死（DASHBOARD_STORAGE_NOT_READY）
  - **窗口耗尽时**：表现为尾部连续失败 → 幂等重跑补建（脚本 `write()` 已内置每 4 笔 auto-reload 续窗）
  - **写入纪律**：create-only、一次定稿、大改整盘重建；chart config 键集须与 `chart widgets-example` 逐键 diff
  - **模板解析（2026-09-10 踩坑更正）**：`widgets-example` 返回 **JSONC 字符串**（含 `//` 注释），且**官方文档缺顶层逗号**（`\n  }` 后直接接注释行与下一个 `"TYPE": {`）——须三步解析：字符串感知去注释 → 补顶层 `}` 后逗号 → 去尾逗号，得 47 种图型真实键集。**用缩进正则提取会得到错误键集**（曾据此误判 `gridShow` 为多余键，误导一轮修复）
  - **验收纪律（质量事故教训）**：组件「建成」≠「可用」。交付看板前必须过三项独立校验：结构（键集／字段归属／布局 `i` 映射；**校验器须先用已知可用样本自测**）、数据（独立算「逐图应有数值」清单对照）、**UI 目视（用户现场确认为唯一验收依据）**；先建 2-3 个代表图经用户确认「可见可编辑」，再批量建其余
  - **★ 布局最小宽度规则（2026-09-10 实证 · "留白/错位"的真因）**：
    - 网格是 **48 列**；**表格类组件（GRID_VIEW）有最小宽度 ≈ 16**——layout 给 `w=12` 时**UI 会把它自动撑到 16**，于是该行超宽/顺推 → 表现为"某行留白 + 组件换行错位"。
    - **排布规则**：每行按 **3 × w=16**（推荐）或 2 × w=24 / 6 × w=8；**混排时表格一律 ≥16**；同行 h 必须一致。
    - **定位方法**：`dashboard get` 读回 `layout`，与设计值**逐项 diff**（本次实测揪出：`细类×色矩阵` 由 w=12 被撑成 16、`4C分析结论` 由 (x36,w12) 变 (x32,w16) 并换到下一行）。
    - **修复**：用 `chart update --layout` 按新方案重写（21 组件 4 次自动续窗、OK 21/0）→ 读图确认 6 行全部铺满、零留白。
  - **看板无人值守会话（2026-09-10 突破 · 取消三处人工依赖）**：
    - **姿势**：`playwright.chromium.launch(channel="chrome", headless=True, args=["--disable-blink-features=AutomationControlled"])` + `new_context(storage_state="~/.workbuddy/dingtalk_state.json")`。工具：`scripts/dashboard_session.py`（`shot` / `write`）。
    - **三项实证**：① 自动打开盘页＝**建立 UI 会话窗口**（自开页面首笔可写 1/1）；② **`page.reload()` ＝ 续窗**，实测刷新后单窗连写 **5/5**、再刷新 **4/5** → `write()` 内置「每 4 笔 auto-reload」即可无限续写；③ 截图回传供读图自检。
    - **必要参数（缺一即失败）**：`channel="chrome"`（用系统 Chrome）；`--disable-blink-features=AutomationControlled`（不加则钉钉判定自动化 → **跳登录页**）；登录态必须走 **storage_state**（持久化 `.dt_profile` 在钉钉侧无效）。
    - **禁用**：`agent-browser`（本机 `open` 连 about:blank 都卡死 9 分钟，非沙箱/`--no-sandbox` 均无效）；**改用 playwright(channel=chrome)**，26 秒即可完成打开+滚动+整页截图。
    - **首次准备**：`scripts/login_dingtalk.py` 弹窗扫码一次 → 导出 `dingtalk_state.json`（判据必须严格：**页面 URL 回到 alidocs 且非 login/oauth** + 出现登录 cookie，否则会被"页面中间态"误判为成功）。
  - **GRID_VIEW 表格必须用官方 13 键模板（2026-09-10 实证修复）**：`chartType / name / sheet / view / filter / viewSort / viewGroup / cellHeight / hiddenFields / widthMap / columnSort / frozenColCount / toolbarConfig`。**症状**：表格组件只显示行号、**无列**（读图确认）。**根因**：config 混入非官方键（`fieldConfigVersion` / `showNewFields`）、缺 `viewSort` / `widthMap` / `name`、`hiddenFields` 带旧值。**修复**：按上述 13 键重写（`hiddenFields={}` 表示不隐藏任何列），实测列与数据立即恢复。
  - **★★ HISTOGRAM「编辑图表」报错的唯一真因＝键集不全（2026-09-10 定案）**：可编辑样本（UI 生成的同型图）**35 键**；不全的图只有 **23–24 键**，**固定缺这 11 个**：`kanbanCustom`、`view`、`xAbbr`、`yAbbr`、`yRightAbbr`、`xSortCustom`、`ySortCustom`、`yAxisRange`、`axisLabelShow`、`categoryAxisMaxRatio`、`xAxisLabelRotate`（旧盘那批还缺 `chartName`），且 `group=[]`、`nullValue="ignore"`（应为 `[{"value":"none"}]` / `"zero"`）。
    → **修复法（实测有效、无需新建）**：取**同盘已可编辑的同型图** config 作模板 → 只替换 `sheet`/`dimension`/`measure`/`measureType`/`filter`/`name`（其余键原样保留，`view` 置 `""`）→ `chart update --config`（**不要带 `--layout`**）。
    → 回读校验门槛：**键数须与模板一致（本例 35）**。
  - **★ 看板图表「能否编辑」可自动验证（2026-09-10 实证 · 无人值守自证）**：卡片**悬停后**头部右侧会出现 30×30 的 `BUTTON`（图标是竖排三点 `path 3x12`；同排还有 `ai-analyze-container`、`分享到聊天`）→ 点击展开菜单（`编辑图表 / 重命名 / 导出为图片 / 删除`）→ 点「编辑图表」→ 判定：**出现配置面板关键词（图表类型/数值/分类/聚合）= OK；出现「文档错误，数据已保存，请刷新重试」= BROKEN**。
    - 注意：**表格类（GRID_VIEW）的菜单里本来就没有「编辑图表」**（只有重命名/导出为图片/删除）——这不是故障。
    - 实现：卡片、菜单都在 `iframe/notable` frame[1]；用元素级 `element.click()` 绕开 Playwright 可操作性检查（常有遮罩拦截）。
  - **★ 两条 UI XPath（用户提供 · 实测可点，用于出"干净整屏"截图）**：
    - **钉钉文档左栏折叠**（宿主页 frame[0]，28×28）：`/html/body/div[1]/div/div/div/div/div[1]/div/div[1]/div[4]/div/div/div[1]/div[1]/div[3]/div/div`
    - **AI 表格隐藏边栏**（`iframe/notable` frame[1]，24×24）：`/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div[1]/div[2]/div[1]/div[1]/div[1]/div/div/div[2]/div/div/button[2]`
    - 用法：截图前依次点这两处 → 收掉左栏与表格边栏，仪表盘占满整屏；**禁止再靠目测坐标点击**（坐标跨 frame 有偏移，曾误触"新建"）。
  - **弹窗清理（截图前必做）**：① 文本按钮 `跳过`（注意真实文案是「跳过(1/4)」，用包含匹配，多点几轮直至无）；② **新公告弹窗**「全新组件上线：拖拽即刻构建应用」需点**右上角 × **（`class/aria-label` 含 close 且尺寸 ≤44、位置在顶部）；③ 兜底 `Escape` ×2；④ 移除大面积 mask/overlay 层。
  - **★ 旧盘改布局被平台拒绝时的绕开法（2026-09-10 实证 · 就地改路径的关键坑）**：
    - **现象**：在既有盘上对图表调布局 `chart update --config --layout`，报 `UPDATE_CHART_OPERATION_ERROR / IllegalStateException: Dashboard layout item changed concurrently: <chartId>`（`retryable=true` 但重试无效；CLI 自身已重试 3 次，故一次调用耗时约 30s，**不要再叠加自定义重试**，否则极慢）。
    - **成因（实测规律）**：当某行**超载**时（如两列表格被前端最小宽 16 撑大后本行 12+12+16+16=56>48），服务端把该行及其下一行视为"重排中" → 这些布局项一直处于"正在被并发修改"状态，任何针对它们的 layout 写入必冲突。
    - **可用的绕开路径（实测 6/6 成功、盘 ID 不变、配置无损）**：**「取配置 → 删除 → 按目标位置 `chart create --layout` 重建」**——`chart delete` 与 `chart create` 都不受该并发检查约束（同盘实测：删 9/9 成、重建 6/6 成），重建后布局项为新建、位置即目标值。
    - **执行顺序**：① 先 `chart get` 逐个保存配置（含 `name`）；② 批量 `chart delete`；③ 批量 `chart create --layout`；④ `dashboard get` 回读逐行核对 w 合计=48。
    - **同时确认**：**看板的写操作（含 chart create/update/delete、dashboard 改）统一需要 UI 会话窗口**；无窗口时表现为"首笔可写、随后 `DASHBOARD_STORAGE_NOT_READY`"——用 `scripts/dashboard_session.py` 的 `DashSession`（自开页面 + 每 4 笔 reload 续窗）即可，无需用户参与。
    - 工具：`tmp_excel_dump/old_rebuild_rows.py`（本次落地脚本，幂等可复跑）。
  - **图表命名（2026-09-10 实证 · 极易踩）**：图表显示名由 **config 内的 `name` 字段**决定——`chart create` 与 `chart update` **都必须传 `config.name`**；`chartName` 只是**回读字段**，传入无效（实测：create 时传 `chartName` → 实体名变成默认的 `STATISTICS Chart` / `GRID_VIEW Chart 6`，且 `chart update` 只传 `chartName` 也改不回来）。**改名正确姿势**：`chart get` 取 config → 写入 `config["name"]`（可同时写 chartName）→ `chart update --config`。有 `name` 的图，`dashboard get` 回读即显示正确名称。
  - **就地改布局 vs 整盘重建（2026-09-10 双路径实测 · 真实场景选择）**：
    - **就地改（`chart update --layout`，config 原样回传）**：本次 32 图 → `OK 23 / SKIP 9 / FAIL 0`，回读每行 w 合计=48、宽度分布健康（8/16/12/24）。**优点**：**盘 ID 不变**、分享设置 / 主题 / filters / 已挂载的自动化与开放平台 API 引用**全部不受影响**、可分批续做。**成本**：每图需 `chart get` + `chart update` 两次调用（N 图 ≈ 2N 次），窗口占用更多。
    - **整盘重建（新建盘 + 批量 create + 删旧盘）**：本次 21 图 → `OK 21 / FAIL 0`（2 分 09 秒）。**优点**：一次写全、干净、组件少时更快。**代价**：**旧盘 ID 失效** → 挂在旧盘上的自动化/API/分享链接全部要改；适合"盘上无外部依赖"的场景。
    - **决策规则**：盘已被自动化/API/分享引用 → **就地改**；全新或确认无外部引用 → 重建。
  - **布局的正解（2026-09-10 两次实证 · 含一次自我更正）**：
    - ⚠️ **不要用 `dashboard arrange` 作为建盘收尾**：它是**贪心填充**，会把多个图表硬塞进一行、宽度压到极小（实测出现 **w=5**，12 列制仅 1.25 格）——**钉钉前端有最小卡片宽度，过窄卡片渲染不下就会被挤到各自一行**，UI 表现为「错位 / 每行填不满」，而服务端 `layout` 看似完全合规（每行 w 合计=48）。这就是"错位反复出现"的真因。
    - ✅ **正解 = `chart update --layout` 写确定性布局**：`chart get` 单图即返回 `layout`（`{i,x,y,w,h}`，`i`=chartId）；`chart update` 支持 `--layout`（与 `--config` 同传，**config 必填**）。建盘时按「每行 2–4 个、宽取 **12 / 16 / 24**、同行 h 必须一致」人工排布并一次写定。
    - 官方 `aitable-dashboard-chart.md` 原文即写「布局空白/不对齐用 **chart update** 修」——`arrange` 只适合救急对齐历史盘，**不建盘收尾**。
  - **`chart update` 入参**：`--config` **必填**（即使只改布局也要带完整 config，服务端拒绝空对象 `{}`，至少含 `chartName`）；`--layout` 可选。故"改布局"优先用 `dashboard arrange`（一次修全盘）
  - **官方仓库实况（2026-09-10 全量核对 github.com/DingTalk-Real-AI/dingtalk-workspace-cli）**：仓库为 Go 编写的**客户端**，**不含** `HISTOGRAM`/`listConfig`/`timeGroup` 等图表 widget schema 字面量——图表 leaf schema 在**服务端 MCP**，权威来源只能是 `+chart-widgets-example` / `dashboard config-example`。仓库价值：`skills/multi/dingtalk-aitable/references/aitable/aitable-dashboard-chart.md`（命令矩阵+流程）、`internal/helpers/sheet_chart.go`、以及 `dashboard arrange` 这一布局解法
  - **HISTOGRAM 配置形态（2026-09-10 与用户 UI 手建图逐键比对）**：可编辑的 UI 生成形态为 **35 键**（`axisLabelShow/categoryAxisMaxRatio/chartType/colors/dimension/fillType/filter/gridShow/group/kanbanCustom/label/labelHideOverlap/legend/listConfig/listCustom/measure/measureType/nullValue/sheet/sortRule/view/xAbbr/xAxisLabel/xAxisLabelRotate/xAxisLine/xAxisShow/xSortBy/xSortCustom/yAbbr/yAxisLabel/yAxisLine/yAxisRange/yAxisShow/yRightAbbr/ySortCustom`），**无 `name`**；与我出错版本的差异共 7 处：`group`（`[{"value":"none"}]` vs `[]`）、有无 `listConfig`、有无 `timeGroup`、`kanbanCustom.groupBase.baseFieldId`（应=维度字段）、`listCustom`（`{"listSetting":{}}` vs `{}`）、`nullValue`（`zero` vs `ignore`）、`xAbbr.abbr`（`""` vs `"default"`）。模板已存本地 `histogram_manual_template.json`
  - **图表配置红线（2026-09-10 实证，含两次自我更正）**：
    ① **HISTOGRAM（普通柱状图）必须照 UI 生成形态写全 35 键**（见上条键集清单）——只写"最小集"会导致该图在 UI 编辑器报「文档错误，数据已保存，请刷新重试」；其余图型容错，**仅 HISTOGRAM 崩**（本盘 21 图里仅有的 3 个 HISTOGRAM 全部报错，其余图型均可编辑）
    ② **`view` 的作用域（2026-09-10 更正 · 曾因此砸掉 6 张表）**：
       - **指标类图表（STATISTICS/HISTOGRAM/LINE/…）**：`view` 必须为空 `""`（引用"带日期筛选"的视图会报错且匹配 0 行）。
       - **表格类（GRID_VIEW）**：`view` **就是它的数据源视图，必须给出具体 viewId**（如 `DD0OMDW`）——**把它当图表一样清空会导致表格渲染成"只有行号、没有列"的空表**。本次 C 版整盘新建时我误清空 → 6 张表全空；从已验证盘复制 config 后 6/6 恢复。
       - 另：`GRID_VIEW` 的 `hiddenFields` 建议显式置 `{}`（空对象=不隐藏任何列），避免从别处复制时带入 `"False"` 字符串这类类型残留。——引用「带日期筛选」的视图（如「最新采集日（xx-xx）」）**只会导致「暂无可用数据」，不会导致编辑报错**（2026-09-10 隔离实验 P10 证实：带日期视图的图**可以正常编辑**，但显示空）。原因：此类视图的日期条件被规范化为 **UTC 零点**（09-09 → 1788883200000），与日期字段实存的**本地零点**值（2026-09-09T00:00:00+08:00 → 1788854400000）**差 8 小时 → 视图匹配 0 行**。「最新采集日」等时间口径一律在数据层用**结果表**承载。
    ③ `dashboard create` 需带 `theme:{key:"DEFAULT",background:null,image:""}`（官方示例：主题禁止自编，否则无法解析渲染）；布局空白/不对齐用 **`dashboard arrange`** 修（`dashboard update` 改不了布局）
- **【2026-09-10 官方仓库全量通读后的能力补充】**（来源：github.com/DingTalk-Real-AI/dingtalk-workspace-cli，clone 3085 文件，通读 skills/multi/dingtalk-aitable 全部文档 + Go 实现 + docs/parameter-hallucination）
  - **权威参数源＝运行时 Schema**：`dws schema --cli-path "aitable <leaf>" --compact -f json`（返回 parameters/constraints/confirmation/data_schema/outcomes/pagination）。官方文档明载**事实优先级：Help/Cobra > 运行时 Schema > 产品 Skill > 别名表**。另有 `dws shortcut list --service aitable`（100 条 shortcut）
  - **服务端聚合（本地不拉全量）**：`record stats`（COUNT/SUM/AVG/MAX/MIN/MEDIAN/DISTINCT…，statsType 大写）与 `record group-stats`（分组；**不传 --group + statsType=distinct ＝条件去重计数**，statsType 大写（v1.0.62 起统一、与 record stats 一致）；分组上限 1000 行）
  - **psql 只读 SQL**：`dws aitable psql -d <baseId> -l`（列表）→ `-t <tableId>`（列类型）→ `-c '<SELECT…>'`；**同 Base 最多 8 表 JOIN**、聚合/分组/窗口函数；中文标识符必须双引号、末尾不加分号、默认补 LIMIT 200；**输出为 psql 文本、不加 --format json**。→ 跨表校验与独立取数的正确通道
  - **视图能力（此前遗漏）**：`view update <attr>` 子命令族——filter/sort/group（`--json '[{"operator":"eq","operands":[fld,val]}]'`，外层必须数组）、visible-fields（**只支持重排，不支持真隐藏**）、field-widths、**aggregate（Grid，action 含 SUM/AVG/DISTINCT/…）**、frozen-cols、row-height（**仅 32/56/88/128**）、fill-color-rule（color 只能 `firstLine1~11`、filter 用 `{fieldId,symbol,value}` 大写枚举）、lock、duplicate
  - **dashboard/chart**：`chart create` 需 `--config` + `--layout`；`chart update` 的 `--config` 必填且**至少要含 `chartName`**（官方示例 config 用 `chartName`，模板用 `name`——两者并存，实测 create 用 `name` 可成）；`chart create` 帮助写"12 列网格"属 **V1 旧文案**，本 Base schemaVersion=2 → **48 列**（`dashboard arrange` 回读 totalColumns 与 x+w 最大值均 =48 证实）；布局收尾一律 `dashboard arrange`
  - **字段**：`filterUp` 无需关联字段（`targetSheet` + `filters[{fieldId,operator:equal|contain,value|currentSheetFieldId,link}]` + `valuesField` + `aggregator: SUM|AVERAGE|COUNT|MAX|MIN|CONCATENATE|VALUES`）；`lookup` 需先有 link 字段（`associateField`=**本表关联字段**的 fieldId）；AI 字段 prompt 必须含 fieldRef；options 更新为**全量覆盖**（不回传旧 id 会丢数据）
  - **记录**：`record create` 返回 **`data.newRecordIds`**、`record update` 返回 **`data.recordIds`**、`record upsert` 返回 created/updatedRecordIds；`record batch-update`（同一 cells 批量）、`+record-upsert-by-key`（业务键，0 建 1 改多冲突停）、`+record-bulk-patch`（须给选择条件 + --max-matches）；`record query --all --page-limit 0` 自动翻页（禁手写循环）——🆕 **`--limit` 最大 100：配合 `--all` 超限（101+）时静默返回 0 条**（`fetchedCount=0 / records=null / complete=true`，**不报错**）⇒ 全量取数一律 `--all --page-limit 0` 且**不传超限 `--limit`**；「0 条」与预期不符先核参数再下结论（2026-10-15 采纳 EV-202610-01，双项目复现）；**零命中时 `records` 返回 `null`（非 `[]`）→ 代码一律 `(d.get("data") or {}).get("records") or []` 兜底**（2026-09-23 实证：直接迭代 None 会 TypeError 中断同步）；`record query-empty` 找空行
  - **日期字段坑（官方确证）**：`record query --filters` 对 date 只能用 `date_eq/before/after/not_before/not_after`——通用 `eq/gt/…` **静默返回 0 条**；无 `date_between`、无 `from_now`，区间用 not_before+not_after
  - **文件级导入导出**：`import upload`（拿 uploadUrl/importId）→ `curl -X PUT -H "Content-Type:"`（**Content-Type 必须置空**，否则 403）→ `import data --import-id [--table-id 追加] [--field-mapping]`；`export data` 异步两阶段（**该命令的 --format 是导出格式，禁止再加 --format json**）
  - **其余**：`attachment upload`（禁直传 URL，须 fileToken）；`workflow edit-example/create/update/run/history`（DSL `workflow-dsl/v1`，须 `data.valid=true` 且 `issues=[]`；删除未开放）；`advperm` 角色 CRUD（角色↔成员绑定仍需 UI）；`section` 节点/文件夹；应用模式 `app`（pageId=dashboardId；widget create 需含 chartType 的 config + x/y/w/h layout）；`table update --record-name-key <英文枚举>`（如 task/project）；`+url-resolve/+resolve-base/+resolve-table/+base-search`；Base 链接 `https://alidocs.dingtalk.com/i/nodes/{baseId}`、表+视图 `?iframeQuery=sheetId%3D{tableId}%26viewId%3D{viewId}`
  - **官方自述的"参数幻觉"治理**：仓库含 docs/parameter-hallucination/…/aitable 分析——官方把"模型臆造参数/枚举"当治理对象，规则是"只做值不变、角色明确的别名，其余 block/ambiguous 停止；不通过别名表做名称查 ID、URL 拼装、枚举翻译"。→ **我方纪律同源：枚举/字段一律取运行时与模板，禁猜**
  - **文件级导入导出（2026-09-10 依据 CLI Help 更正——此前抄了 multi 文档的过时口径）**：
    - **导出**：`dws aitable export data --base-id B --scope all|table|view [--table-id][--view-id] --export-format excel|attachment|excel_and_attachment|excel_with_inline_images --format json` —— **`--export-format` 是业务格式、`--format json` 是输出格式，两者可并用**（旧写法 `--format excel` 仅兼容历史脚本）。**`--timeout-ms` 上限 30000**；`--output` **不会**保存导出的 xlsx（实测只写 JSON/0 字节）→ 必须取 `downloadUrl` 再 `curl -L` 下载
    - **导入**：`import upload --file-name x.xlsx --file-size <字节>`（**无 `--file` flag**）→ `curl -X PUT "<uploadUrl>" -H "Content-Type:"`（**此处 Content-Type 必须留空**，留空/默认 form-urlencoded 会被 OSS 403）→ `import data --import-id <ID> [--table-id 追加] [--field-mapping '{"目标字段名":"源列名"}']`（`--timeout` 秒，推荐 30）
    - ⚠️ **注意与附件上传的区别**：`attachment upload` 的 PUT 要求 **Content-Type = 具体 MIME**（.txt→text/plain、.png→image/png、.xlsx→…spreadsheetml.sheet）；**导入上传要求留空**——两个通道要求相反，勿混
    - 两条链路选路：无目标表的 Excel 导入→文件导入任务（新建表）；追加到既有表→`import data --table-id`（列名需精确匹配，否则 `Failed to build import sheet infos from preview data`）；字段不匹配→`--field-mapping`；也可用脚本 `scripts/aitable_import_via_task.py` / `scripts/import_records.py`
  - **【mono/multi 文档差异与裁决（2026-09-10 通读后）】** 官方仓库里 aitable 文档有两套：`skills/mono/references/products/**`（含**大量实测踩坑口径**）与 `skills/multi/dingtalk-aitable/references/**`（精简后的 agent 版）。逐篇 md5 比对：14 篇完全相同、**15 篇不同**（其余 89 个 mono-only 文件属 doc/sheet/drive 等其他产品）。**凡两版矛盾处一律以运行时 Help/Schema 裁决**（官方事实优先级），已裁决：
    - **一律用 `--export-format`**（见上，mono 对 / multi 错）
    - `record query` 全文搜索 flag 是 **`--query`**（multi 对 / mono 的 `--keyword` 已过时）
    - `view update visible-fields`（Help 只声明"列顺序/整组替换"）——mono 称**短列表可真正隐藏**字段（证据：`view list` 的 `custom.hiddenFields` 变 true，传回全量解除）；multi 称"只支持 reorder 不支持隐藏"。**Help 未正面表态 → 列为待实测项，默认按 mono（短列表=隐藏），隐藏状态以 `view list` 的 `custom.hiddenFields` 为准**
    - `view update aggregate` 清除语义：Help 明确"**传 null 清除单个字段聚合**"且有 `--clear-field-id`（与 multi 一致）；mono 称**实测清除静默无效**（改聚合方式可行、无法回到"无聚合"）→ **列为待实测项，默认按 Help**
    - `primary-doc-get` 未创建主键文档时的返回：mono 称返回 `status=error` + `code:-1 "no record"`（**不是** `nodeId:null`）；multi 称 `nodeId` 为 null → 待实测
    - `form get` 返回结构：mono 称 `data` **就是该表单对象**（服务端 viewIds 过滤不生效、CLI 客户端过滤，不存在报 `form view <id> not found`）；multi 称 `data.formViews[]` → 待实测
    - `record history-list` 实测字段名：mono 称 `type:"row"`、`action:"appendRow"|"updateRecords"`、`newValue/oldValue` 解析后为 `{fieldId:{dataType,value}}`、**无 `typeChangedFields`**、**记录删除后历史不可查（返回空）**；multi 称 `field_change` / `create|update|delete` + `typeChangedFields` → **mono 为实测口径，采信 mono，实测前不按 multi 写死**
    - `view get frozen-cols`/`row-height` 未设置时的返回：mono 称**整个键缺失**；multi 称**为 null** → 待实测（判空逻辑两种都兼容即可）
    - multi 独有的补充（值得保留）：`form` 的 canonical shortcut 闭环 `+form-share-update` → 取 `data.shareFormUuid` → 分享地址 `https://alidocs.dingtalk.com/i/form/{uuid}`；`view-config` 的全套 typed-flag 与列顺序最短闭环；`field create` 两种输入模式严格互斥；货币字段须用 `currency` + `currencyType`
    - mono 独有的补充（值得保留）：`dashboard share get/update`、`chart share get/update` 命令族（`--share-type ORG`；**ORG 分享时 `shareType` 回显 `"[1]"` 是服务端已知问题**；`dashboard share get` 可能 404 属可重试）；`form list` 新建表单**无 title 且 createdAt=0**；`record query` 的 `--records` 常见错误清单（`--data`/`fields` 误用）
- 图表：`dws aitable chart create/update/delete/get/widgets-example`（建图前先读 `widgets-example` 模板；`chart update` 的 config 必含 chartName）
- 表单：`dws aitable form list/update/share`、`form field list/update/hide`
**仍为 UI 专属（明示并给 UI 步骤）：**
- 公式字段创建（服务端 not supported，UI 配置后可读）；
- 按钮字段（字段类型表无 button）、自动化（无 automation 命令）、OCR、单选「同步其他表选项」。
- 关联类字段（单向/双向）**CLI 实测可创建**（勿默认降级 text）；确失败时排查原因（如主键约束）并报告用户，在方案中说明降级。

## 视图 / 仪表盘 / 图表实操纪要（2026-09-05 实测通过）
- **视图**：`dws aitable view create --base-id B --table-id T --view-type Grid|Kanban|Gantt|Calendar|Gallery|FormDesigner --name "名称" [--config '{"visibleFieldIds":[...]}']`；Kanban 无分组字段配置也能创建（视图类型本身不依赖分组字段）。**分组/筛选均已实操闭环**（2026-09-05：UI「按审批状态分组」视图为协议反查权威样例 + CLI `--config group/filter` 复刻成功，见下条）。view get 返回协议：`{views:[{filter:{operator:"and",operands:[]}, group:[], sort:[], columns:[fieldId...], viewId, viewName, viewType}]}`。
- **view filter/group 协议（2026-09-05 已解，CLI 实测可用）**：视图持久化协议 = `filter:{operator:"and",operands:[叶子]}`；**叶子 = `{"operands":[fieldId, 选项key], "operator":"eq"}`**（单选值=选项 id/key 非显示名；eq=等于）。CLI 创建时 `--config` 直接传 `{"filter":[{"operands":[fieldId,optKey],"operator":"eq"}]}` 与 `{"group":[{"fieldId":..,"direction":"ASC"}]}` 均成功。UI 建样例视图后用 `view get` 反查是可靠反查路径（勿臆造 operator/结构）。
- **仪表盘**：`dws aitable dashboard create --base-id B --name "名称"` → 返回 dashboardId；URL 规则 `https://alidocs.dingtalk.com/i/nodes/{baseId}?entrance=data&applicationId={dashboardId}`（对用户输出实体名+可点链接，隐藏 id）。
- **图表**：`chart create --base-id B --dashboard-id D --config '<widget json>' --layout '{"x":0,"y":0,"w":6,"h":5}'`。先 `chart widgets-example` 取模板：chartType 必须用示例类型名（PIE/BAR/AREA/LINE/PIVOT/AGGREGATE_LIST_VIEW/COUNTDOWN…）；`colors` 只能用 `COLOR_PALETTE_1` 等默认值；`sheet/view/filter 内 fieldId` 必须真实存在；filter 空传 `[]`；AGGREGATE_LIST_VIEW 的 `fieldAggregateMap:{fieldId:"sum"}` 可行。layout 以本段下方「网格布局」的 **V2·48 列网格**为准（chart help/widgets-example 中的 12 制示例不可沿用）。
- **网格布局（重要）**：dashboard 根容器为 **V2 · 48 列网格**（config-example 权威），x∈0..47、同行 w 之和=48、同行 h 一致、行连续堆叠（chart create --layout 按 48 制传入生效）。
- **chart 级 filter**（指标卡等按状态统计）：`config.filter = [{fieldId, link:null, version:1, symbol:"ANY_OF"|"NONE_OF", value:[选项id数组]}]`（选项类）或 symbol EQ/GT…（数字）、DATE_EQ（日期）；选项 id 从 field get 的 options.id 取。实测 STATISTICS 指标卡带此 filter 成功。
- **常用模板要点**：STATISTICS（指标卡：measure sum + titleColor/descColor 可每卡个性化配色 + numberFormat 千分位；**desc 易挤占数值区→用短描述或留空，数字完整优先**）；折线多系列——**LINE 与 STACKED_LINE 都支持**（dimension=X + group=[{value:分类字段}] 即按类型多系列；勿臆断基础折线不能多系列）；STACKED_HISTOGRAM 同构（dimension+group 堆叠）；HISTOGRAM 柱/BAR 条（dimension+measure sum）；GRID_VIEW 表格组件（sheet+view=复用现成视图（含其筛选），cellHeight/frozenColCount/toolbarConfig）。
- **折线图权威 config（2026-09-05 UI 端手动调整后反查，含「平滑」两层结构）**：多系列=LINE/STACKED_LINE + `group:[{"value":分类字段Id}]`；空值置零=`nullValue:"zero"`；数据点常显=`symbolType:"always"`；**平滑= `smooth:true` + 嵌套 `seriesSettingsBySheet:{<sheetId>:{"ALL_SERIES_VALUE":{"shape":{"lineSmoothType":"smooth"}}}}`**（后者是 UI「线条样式=平滑」的真实落点，二者同写才可靠生效）；其余键 xSortBy:"x"/sortRule:"asc"/legend/filter 与其它图一致。**UI 端反查（chart get 读用户手动调好的图）是学习权威结构的首选路径。**
- 🆕 **UI 组件 config 可读（2026-10-15 更新）**：v1.0.62 实测 UI 手动创建的组件 `chart get` 可读回**完整 config**（34/34 全可读）——「UI 端反查」路径**无版本顾虑**（EV-202609-07 补测②的旧顾虑解除）。
- 🆕 **图表动态时间窗与聚合（2026-10-15 采纳 EV-202610-04 · 用户手动版反查 + 渲染实测）**：① **相对日期 filter**——`{symbol:"FROM_NOW", value:{type:"relative", offset:-30, period:"day"}}`＝滚动近 30 天；`{symbol:"DATE_EQ", value:{type:"relative", offset:-1, period:"month"}}`＝上一自然月——**图自动跟随时间**，无需人工改期（与 CLI `record query` 的日期限制是**两条链路**，勿混用推论）；② **周聚合**——`timeGroup:"week"`（分桶标签＝周始日；多日趋势防拥挤，如 41 根日柱 → 5 根周柱）；③ **图型与选型速查**：`BAR`＝横向条形（**排行**场景，名称横排可读、条长直观）；`COMPOSITION`＝组合图（双轴；次序列挂 `composition:{chartType:"LINE", yAxisPosition:"right"}`——**量＋额**同图）。**排行→BAR／量额构成→COMPOSITION／趋势→LINE＋相对时间窗／结构占比→STACKED_HISTOGRAM／多日防挤→周聚合。**
- **平台缺陷红线（dashboard）**：同一仪表盘上**禁止反复 chart update/delete**——① chart update 返回成功但 chartType 实际不变（假象）；② 多次写操作后 charts 实体随机丢失、仅剩 layout 幽灵（dashboard get 的 charts 索引抖动）；③ dashboard arrange 无法清除幽灵。大改一律**整盘重建**：dashboard create → 一次批量 chart create（create-only，类型/关键配置一次定稿）→ get 校验实体=布局零幽灵 → 旧盘 dashboard delete（NOT_FOUND 确认）。
- **dashboard CLI 写入依赖「UI 会话同步」（2026-09-09 实测，老/新 Base 同规律）**：`DASHBOARD_STORAGE_NOT_READY / DELTA_CHAIN_INVALID / cpVersion<latestVersion` 会锁死所有 dashboard 写操作——**该锁在「用户界面打开该 Base 仪表盘页」的会话期间被解除**（服务端按 UI 访问补齐 delta 链），一旦 UI 关闭则回到锁定（dashboard create 偶可成功——storage 恰好最新；成功后 latest+1 再次锁死，chart/update/delete/arrange 全失败；等待/重试/轻量写均无法自行追平）。规律实证：新 Base（KK）与活跃老 Base（预算）在无 UI 会话时，均只允许第一笔写成功。**操作规则（2026-09-23 口径更新）**：建盘/删除/大改一律在 `scripts/dashboard_session.py` 打开的会话窗口内执行（自开页面 + 每 4 笔 auto-reload），**无需用户参与**；无脚本环境才回退为"请用户在 UI 打开仪表盘页停留"。新 Base 首次更需先建立会话窗口。
- **filterUp「取原值」**：`aggregator:"VALUES"`（2026-09-09 实测 CLI 可创建；界面建的原值查找引用回读 config 同构：aggregator VALUES + filters[含 link:"AND"] + targetSheet + valuesField）。此前试 NONE/FIND_FIRST/FIRST/ANY 全被拒（not supported for external configuration）——VALUES 为正确枚举。详见 aitable_field_types.md。
- **图表删除**：`chart delete --base-id --dashboard-id --chart-id --yes`（--yes 必带，否则静默不删）。
- **图型补测（2026-09-07）**：`RADAR`（雷达图）CLI **可创建**——config 与其它图同族（measureType/measure sum + dimension + colors/legend/label/filter/nullValue/smooth），虽 `widgets-example` 模板段未收录 RADAR，实测 create 被服务端接受、dashboard get 正常落盘（参考键集勿臆造新键）。→ 默认仪表盘模板第 3 行「雷达图」可行。
- **能力边界补测（2026-09-07）**：① UI 手动创建在仪表盘上的组件（chartId 形如 `widget-xxx`）**CLI `chart get` 读不到 config**（空返回）——UI 组件的精细配置无法经 CLI 反查，仅 dashboard get 可列名称/类型/布局；② CLI `field create` 显式传 option id（想对齐源表选项池模拟"选项同步"）会被服务端**忽略并重新生成** id → 选项同步确认仅 UI 可建（见 aitable_field_types.md）。
- **验证**：`dashboard get --dashboard-id` 看 chartCount/charts/layout（每行 x+w 校 48）；发现实体丢失/幽灵/错位时**不要**用 arrange 或 chart update 修补（实测均无效），直接整盘重建（见上方平台缺陷红线）；完成后向用户输出仪表盘 URL：`https://alidocs.dingtalk.com/i/nodes/{baseId}?entrance=data&applicationId={dashboardId}`（隐藏技术 id，给实体名+链接）。
- 实测样例：预算 Base 已建「预算执行总览（示例）」仪表盘 v3（盘 id 略；10 组件 4 行：5 指标卡/3 结构图/LINE 多系列平滑折线/GRID_VIEW 待办表）；CRM Base 已建「回访台账（示例）」Grid 与「客户状态看板（示例）」Kanban 视图；「待办审批」「按审批状态分组」视图为 UI 样例（协议反查权威来源）。
