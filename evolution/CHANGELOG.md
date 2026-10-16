# CHANGELOG · dingtalk-aitable-assistant

> 每次采纳一条经验卡后在此记录；格式：日期 / 经验卡 ID / 触发 / 改动文件位置 / 回滚点。

## v0.1.0 · 2026-09-05 · 首版建立
- 基于 v0.2 方案报告落地 SKILL 骨架（SKILL.md / references×5 / scenarios×3 / templates / evolution / scripts）。
- 吸收开发期实战经验（fieldName+config 语法、formula 不支持、单批100、records-file、差异列创建、三模式同步）作为 v0.1 内置规则。

---
_以下为后续采纳记录区（EV 经验卡）_
## v1.0.0 · 2026-10-16 · 🎉 正式版首次发布（首个公开开源版本）
- 本版本为 **dingtalk-aitable-assistant 首个正式版（v1.0.0）**，正式发布为公开开源项目（GitHub）。
- 内容基线：开发线 v0.4.9（三场景能力 / 看板支持 / 交付验证协议 / 执行环境铁律 / 经验卡机制）；已通过完整开源化审查（敏感信息零残留）。
- 后续版本约定：新的正式版在交付目录中以独立版本发布；改进先经开发线经验卡机制采纳、再进入正式版。
## v0.4.9 · 2026-10-16 · v1.0 准备批（README/License/名称/档案脱敏/执行环境铁律）
- **README 全面重写**（开源级）：新增「源头与致谢」（cangjie-skill / darwin-skill / dingtalk-workspace-cli / WorkBuddy 四组来源）＋「三场景 × 真实项目验证迭代」能力说明 ＋ 安装 / 快速上手 / 技能结构 / 安全边界 / FAQ / 贡献 / License。
- **README 二次增强**（同批）：新增「**工作原理**」章节（六段式流程概览 ＋ 三场景完整工作过程——场景一按「需求 → 方案 → 确认 → 开工 → 验收交付」生命周期展开、明确「先方案后开工」铁律；场景二/三各六段/五段流程）＋「**快速上手**」改版为三场景各一个完整示例（对话 → 技能过程 → 产出物）。
- **LICENSE**：署名改个人 —— `Copyright (c) 2026 shiyilarry (https://github.com/shiyilarry)`。
- **名称**：「钉钉AI表格全能助手」→「**钉钉AI表格助手**」（SKILL.md 标题 ＋ README）。
- **经验卡档案脱敏**（cards/2026-09 ＋ 2026-10，开机源档留备份）：专名代号化（项目 A~I / 渠道A / 品牌甲 / 库标识A / 库表 A~C / 仓库A / 店码 1~5 / 同店码 A·B）＋ 业务数值量级化（技术白名单保留：批上限 / 秒数 / schema 计数 / 算法名）；**净度验收 CLEAN（敏感词 0 残留）**。
- **新增 `references/exec_env_windows.md`**（R1 执行环境铁律：文件读写 / 命令执行 / 落盘再读 / 修改安全 / 状态时间）；SKILL.md P0.1 已引用。
- 备份：backups/20261016-1304c_v0410-*.md（5 份：LICENSE / README / SKILL / cards×2）。
- 遗留：**v1.0 打包**（技能本体分发包 + 版本号 1.0.0 + 出厂检查）——交付路径与用户确认后执行。

## v0.4.8 · 2026-10-16 · 全面复核治理批（开源化前置审查 · 用户批准方向）
- **背景**：用户计划将技能上传 GitHub 仓库开源 ＋ 分享同事，要求全面复核（敏感信息 / 真实数据 / 冗余 / 场景边界 / 反复坑治本）；复核按「开源公开」标准执行。
- **安全修复**：① `scripts/dingtalk_state.json`（320KB 登录态）清出技能目录；② `scripts/.dt_profile`（67MB 登录态残留）清出；③ `scripts/shots/*` 看板截图清出；④ `login_dingtalk.py` 导出路径改至 `~/.workbuddy/`（治本，不再落进技能目录）。
- **脱敏（执行层）**：`verification-protocol.md`（项目名×2 ＋ 4C 数值 → 示意化）；`dws_command_ref.md`（数值样例 ＋ 盘 id → 脱敏）；`aitable_platform_rules.md`（内部痕迹泛化）；人名类称谓 ×2 → 「用户」。
- **开源化改造**：`scripts/dashboard_session.py`——node / dws **动态发现**（禁硬编码本机路径）＋ `BASE_ID` 改环境变量 `DWS_BASE_ID`（未设置时 fail-fast 明确提示）；`login_dingtalk.py` URL 去硬编码；**冒烟测试通过**（真实截图链路，动态 node 组合实测可用）。
- **过期更正**：`aitable_platform_rules.md`「自动化无命令」过期结论 ＋ v1.0.55 标记；`SKILL.md` 版本标记（v1.0.55 → v1.0.61+）；`dws_command_ref.md` 标题口径（v1.0.61–1.0.62）。
- **流程自披露**：安全修复批未预先单独备份（已补 `v047b` 基线备份）；后续恢复「先备份后改」纪律。
- **遗留（待用户拍板）**：① LICENSE 署名（公司/个人）；② evolution（经验卡档案）是否进开源仓库；③ v1.0 建议清单（exec_env 文档 / README 开源化 / 打包分离）见复核报告。
- 回滚点：backups/20261016-1029_v047-*.md（5 份）＋ 20261016-1034b_v047b-*.md（6 份）。

## v0.4.7 · 2026-10-16 · EV-202610-02 补充采纳（client-token「批」边界）
- EV-202610-02 client-token 单批幂等键边界：**token 与「同一组内容」绑定**——跨批 / 跨月复用旧 token 提交新内容 → `DUPLICATE_CLIENT_TOKEN` 拒绝（实测 0 落差）；token 落盘文件按批 / 按内容命名（实践做法：内容 sha256 前 12 位，内容变则自动换新）→ `scenarios/scenario_02_sync.md` S5「新增幂等键」条扩展（EV-202609-45 落地边界补强）＋ `references/dws_command_ref.md` Record·幂等键行。
- 说明：本条为「先解释后采纳」流程产物（2026-10-15 解释已交、2026-10-16 用户确认采纳）。
- 回滚点：evolution/backups/20261016-1029_v047-*.md（5 份快照：SKILL / CHANGELOG / cards-2026-10 / dws_command_ref / scenario_02_sync）。

## v0.4.6 · 2026-10-15 · 批采纳 EV-202610-01/03 ＋ 实战沉淀 04~08（7 张 · 用户批准）
- **他项目反馈卡（2 张）**：
  - EV-202610-01 `record query --all` + `--limit>100` 静默返 0（伪装空表、无报错）→ `references/dws_command_ref.md` CLI 能力边界·记录条（全量取数一律 `--all --page-limit 0`；技能侧跨表独立复核复现）。
  - EV-202610-03 验收两层（写入命中 ＋ 口径独立判定）→ `scenarios/scenario_02_sync.md` 交付前自检清单 ＋ 写入取值规则节。
- **实战沉淀卡（5 张 · 真实项目同步 + 看板对比）**：
  - EV-202610-04 图表动态时间窗与聚合（relative filter / timeGroup:week / BAR·COMPOSITION / 选型速查）→ `dws_command_ref.md` 图表区。
  - EV-202610-05 v1.0.62 观测更新（UI 组件 config 可读＝旧顾虑解除；`base get` 含 dashboards 清单）→ `dws_command_ref.md`。
  - EV-202610-06 联动对象三查（结果表刷新 / 字典缺口 / 消失行逻辑删除优先）→ `scenarios/scenario_02_sync.md` 派生子场景段。
  - EV-202610-07 高视口截图方案 → **新增 `scripts/shot_full.py`**（1680×2400 一屏全量；替代滚动分段）。
  - EV-202610-08 `record update` 置空限制（null 被拒）→ `dws_command_ref.md` 写记录 cells 段。
- **暂缓（本轮未处置）**：EV-202610-02（client-token 单批边界）——用户要求补充场景解释，解释已交、待再裁定；卡片保留「待采纳」+ 裁定过程备注。
- 回滚点：evolution/backups/20261015-2158_v046-*.md（5 份快照：SKILL / CHANGELOG / cards-2026-10 / dws_command_ref / scenario_02_sync）。

## v0.4.5 · 2026-10-15 · 勘误：group-stats statsType 大小写（v1.0.62 行为变更 · 实测更正）
- **背景**：真实项目数据同步实战（2026-10-15）实测发现——`dws` v1.0.62（Build 2026-09-16）下 `record group-stats` 的 `statsType` 由「必须小写」变更为**必须大写**：小写报 RC=3「必须使用大写枚举值，got "count"」，大写正常返回。v1.0.61 时代记载的「两命令大小写相反」**已作废**。
- **落点**：`references/dws_command_ref.md`（group-stats 权威说明 + 能力面描述 + 实测样例统一大写）；`references/verification-protocol.md`（§4-D 示例注释与样例值）。
- **附带补记**：`group-stats` 的 `groupKeys[].value` **日期分组同样不回值**（`{"dataType":"DATE"}`）——分组值回读不可靠为跨类型通例（选项 / 日期均不回），需靠 `recordCount` / 顺序对照。
- 回滚点：evolution/backups/20261015-1657_v045-*.md（4 份快照：SKILL / CHANGELOG / dws_command_ref / verification-protocol）。

## v0.4.4 · 2026-10-01 · 批采纳 EV-42/45/46/47 ＋ EV-43/44 通用化并入（用户批准）
- **直接采纳（4 条）**：
  - EV-202609-42 单选 `SELECT_OPTION_NOT_FOUND` 排查次序（先逐字符核 id → 再核归属 → 最后谈形态；「形态不支持」须零污染实验证伪）→ `scenarios/scenario_02_sync.md` 新增「单选传值排查次序」节 ＋ `references/aitable_field_types.md` 约束第 13 条。
  - EV-202609-45 `record create --client-token` 必须合法 UUID v4、禁派生拼接；多批「一批一 token」落盘复用 → `references/dws_command_ref.md` Record 段（新增幂等键行）＋ `scenarios/scenario_02_sync.md` S5。
  - EV-202609-46 `record stats` 返回两层嵌套 `results`（取值路径 `data.results[0].results[0].value`）；解析失败禁 `or 0` 静默兜底 → `references/dws_command_ref.md`（stats 返回结构）＋ `references/verification-protocol.md` §1（L1 数值取值路径注）。
  - EV-202609-47 `record query --filters` 过滤 singleSelect 选项名 / id 两形态均可；「基线 0 行」须对照查询证伪 → `references/dws_command_ref.md`（filters 注）＋ `scenarios/scenario_02_sync.md` S4（写前预览）。
- **通用化并入（2 条 · 用户批示「提炼通用性经验后补强到 EV-29」）**：EV-202609-43 / 44 含项目特化（字段名 / 平台名）→ 提炼为「**键粒度纪律**」（定键两步：先测行粒度再测唯一性；多行可能 → 键须含节点维度；共用表域过滤与键节点列同维度、读写验三通道一致；单域建议保留）；项目特化名不入档 → 并入 `scenarios/scenario_02_sync.md` S4（EV-202609-29 落点）。
- 回滚点：evolution/backups/20261001-1427_v044-*.md（7 份快照：SKILL / CHANGELOG / cards / scenario_02_sync / dws_command_ref / aitable_field_types / verification-protocol）。

## v0.4.3 · 2026-09-24 · 批采纳 EV-27/30/35/37 ＋ 7 卡丢弃 ＋ EV-41 参数底线修订（用户批准）
- **采纳（4 条）**：
  - EV-202609-27 批量写入失败韧性与重试分档 → `references/error_handling.md`（重试表按**幂等性**分档：幂等可重试 / create 类禁自动重试「超时 ≠ 未执行」；批量失败粒度＝批 → 参数类二分定位、网络类不二分）＋ `scenarios/scenario_02_sync.md` S5 同源落地。
  - EV-202609-30 number 读回为字符串 → `references/aitable_field_types.md` 约束第 12 条 ＋ `references/verification-protocol.md` §4-K（逐格比对：先类型归一、禁裸 `!=`、左右同一归一函数）。
  - EV-202609-35 执行凭证对账纪律 → `references/verification-protocol.md` §4-L（写工具反馈＝客户端视角；判据只认目标侧回读；差额先归因再收口；未归因不得触发重写）。
  - EV-202609-37（并入 · 不留独立卡）→ `references/dws_command_ref.md` 补「CLI `--filters` 不读视图配置」；`references/verification-protocol.md` §4-I 补「排查次序」；定标与新建选项维度已于 v0.4.2 并入「读后写延迟」条。
- **丢弃（7 条 · 用户定性「非本技能域」）**：EV-202609-31（BI 属使用项目越权考虑范围）；EV-202609-32 / 33 / 34 / 38（采集 / 入库侧——他项目 playwright ＋ 自建 MySQL MCP 域）；EV-202609-39 / 40（与三场景及派生场景无关——自动化运行卫生 / 采集自愈）。
- **EV-202609-41 参数底线修订**：§4-I 复核参数改为「先等 ≥60s（**硬底线**）再回读」，移除「小表可先按 15s 试」例外——依据用户明确需求（跨项目两次实证：选项追加后回读无新值；立即拉数不完整）。
- 遗留：**无**——EV-202609-36 已于 2026-09-24 当日裁定**丢弃**（用户定性：缺口形态聚合属采集 / 对账链路，与 EV-202609-32 为姊妹形态；本技能侧零实证）；TR-02「未处置卡」清零。
- 回滚点：evolution/backups/20260924-1358_*.md（8 份快照：SKILL / CHANGELOG / cards / verification-protocol / dws_command_ref / error_handling / aitable_field_types / scenario_02_sync）。

## v0.4.2 · 2026-09-24 · EV-202609-41 采纳（读后写延迟触发面扩展）
- **来源**：EV-202609-41 · 用户 2026-09-24 批准「并入 28/37 的『读后写延迟』条」。触发面由 `record upsert` 扩写为「`record upsert` 与 `field update` 均含」，并补两条铁律（服务端受理 ≠ 读侧可见；禁止以写 / 读通道回显 id 判落地）。按「只增不退 + 同落点合并」原则执行，**未新增独立规则条**。
- **落点 1**：`references/verification-protocol.md` §4-I —— 触发面（渠道）、复核参数（≥60s 起 · 等间隔轮询）、两条铁律。
- **落点 2**：`references/dws_command_ref.md` `## Field` —— 补 `field update` 速查行（改名 / 配置；不可变更字段类型）＋告警（options 全量覆盖 / `verified` 仅代表受理 / 复核按「选项名 + 原 id 保留集合 + 数量变化」）。
- **附带**：`evolution/cards/2026-09.md` —— EV-202609-41 状态置「已采纳」；TR-02 未处置卡清单更新为 EV-202609-30 ~ 40。
- 回滚点：evolution/backups/20260924-1310_*.md（5 份快照：verification-protocol / dws_command_ref / SKILL / CHANGELOG / cards）。

## v0.4.1 · 2026-09-23 · A 组收尾 + B/C 组批量采纳（用户批准）
- **A 组收尾（v0.4.0 批次补落）**：① 禁止静默降级（设计交付一致性纪律）→ scenarios/scenario_01_build.md 流程铁律⑥；② 主数据字典须有消费方 → scenario_01_build.md S4 建表通用规则；③ `record stats` 同字段多 statsType 须拆多次调用 → dws_command_ref.md；④ 看板写入口径统一为 `dashboard_session.py` 无人值守（清理旧「需用户前台打开 / 窗口容量数字」表述）→ dws_command_ref.md。
- **B 组（采纳 6 条）**：EV-202609-19 formula 复算对账法 → verification-protocol.md §4-G；EV-202609-22 ID 复核铁律 → dws_command_ref.md 通用；EV-202609-23 职责边界＋报告输出禁令 → scenario_02_sync.md 新节；EV-202609-26 时间保真三层证据链 → verification-protocol.md §4-H；EV-202609-28 空结果 null 兜底＋读后写延迟 → dws_command_ref.md / verification-protocol.md §4-I；EV-202609-29 身份键选择纪律 → scenario_02_sync.md S4。
- **C 组（合并采纳 2 组）**：EV-202609-20 + 25 → 「写入取值口径与空值纪律」（scenario_02_sync.md 新节；20 为过渡原则、25 为最终态）；EV-202609-21 + 24 → 「缺口/差异集：现算＋口径分层」（verification-protocol.md §4-J + scenario_02_sync.md S4）。
- **D 组（丢弃）**：EV-202609-14 项目特例不入档；EV-202609-15 窗口容量细节、EV-202609-16「用户目视＝唯一验收」旧表述不再采纳（现行为「用户仅抽检」）；EV-202609-16「手建图对照」转为跨月跟踪待办（见 cards/2026-09.md 跨月跟踪项）。
- **EV-202609-27（重试按幂等分档）**：差异点已向用户解释，**待决定**（未落地），相关文字暂保持现状。
- 说明：本批为批量采纳（B 6 条 + C 2 组合并），经用户明确批准，与 rules.md「一次只采纳 1 条」的偏差受理；规则修订提案留置评估（见 cards）。
- **机制落盘（本批收尾）**：① `evolution/rules.md` 新增「二之补·能力基线三原则」（只增不退 / 三场景核心能力覆盖 / 频次优先：低频个例不直接采纳）；② `cards/2026-09.md` 新增「跨月跟踪项」（TR-01 看板手建图对照学习；TR-02 低频卡留待观察与频次复查）＋「决策留置记录」（规则修订建议「同落点小批合并 ≤4 条」留置待议）；③ 本轮采纳项已按三原则逐条复核：8 条全部属「每次 / 隔几次任务必遇」档，无个例特化项。
- 回滚点：evolution/backups/20260923-1153_*.md（7 份快照）＋ 20260923-1157_rules.md。

## v0.4.0 · 2026-09-10（2026-09-23 补记结账）· 看板质量整改 + 验证协议建立 + 每日升级门禁
- 覆盖经验卡 EV-202609-13 ~ 18（当时未走 CHANGELOG 结账，状态在此一并闭环）。
- 主要内容：① SKILL.md P0.0 每日自动升级门禁 + P0.1/P0.2 环境与看板无头会话（scripts/daily_upgrade_gate.ps1 / dashboard_session.py / login_dingtalk.py / shot_dashboard.py）；② references/verification-protocol.md 建立（三项独立校验、HISTOGRAM 35 键、禁止自证）；③ dws_command_ref.md 看板实测区（键集校验、48 列布局、视图日期时区坑、filterUp VALUES、statsType 大小写、服务端聚合通道）。
- 回滚点：原批次快照见 backups/ 内 20260909-1740_* 等历史文件（本补记条目不新增回滚点）。

## v0.3.0 · 2026-09-07 · 报告单文件化定稿 + SKILL 全量复核清理（EV-202609-12 采纳）
- 报告交付收敛为两类单文件：方案类=演进式项目档案（设计→评审→实施→验收同文件推进，状态徽章，评审摘要留痕），审计类=独立只读报告（评级总览置顶）；不再拆分评审稿/交付验收独立 HTML。
- report_style_guide.md 升 v2.0：方案 0-13 章 / 审计 1-8 章结构总纲；审计黑话改常规中文（阻断级/重要/一般 + 通过/部分通过/未通过）；Tailwind v4 构建期编译·离线内联路线；合规自查阈值；SKILL 仅两类报告产出声明。
- 实测结论残留全链路清除：看板/仪表盘=CLI 支持（4 处旧说法修正）；dws_command_ref 关联降级/12 列/arrange 修补 3 残留；error_handling 关联默认降级（违 EV-03）。
- scenario_01/02/03 编排更新：单文件演进铁律、仪表盘三分支、审计多源需求与符合度矩阵、可选项目优化建议。
- 回滚点：evolution/backups/20260907-1830_*.md（7 份）+ 20260907-1840_*（3 份）。

## v0.2.1 · 2026-09-05 · 批量采纳 EV-202609-09 ~ 11（用户确认，仪表盘阶段收尾）
- EV-09 chart delete 同盘高频写操作引发索引脏数据（layout 幽灵/实体复现）→ 整盘重建优先、delete 后 get 验证 → dws_command_ref.md 平台缺陷红线。
- EV-10 chart update 无法变更 chartType、多次写操作致实体随机丢失、arrange 不清幽灵 → dashboard「create-only、一次定稿、大改整盘重建」红线 → dws_command_ref.md + EV-09 合并落点。
- EV-11 折线多系列与平滑权威结构（LINE 亦支持 group 多系列；平滑= smooth:true + seriesSettingsBySheet.<sheet>.ALL_SERIES_VALUE.shape.lineSmoothType:"smooth" 两层；空值置零 nullValue:zero、数据点常显 symbolType:always）→ dws_command_ref.md 折线权威 config 段。
- 回滚点：evolution/backups/20260905-1100_*.md（4 份快照）。

## v0.2.0 · 2026-09-05 · 批量采纳 EV-202609-02 ~ 08（用户确认）
- EV-02 场景一「先方案评审稿、确认后再开工」流程铁律 → scenarios/scenario_01_build.md（S2→S3→S4 闸门）。
- EV-03 单向/双向关联 CLI 实测可建，禁止默认降级文本 → references/aitable_field_types.md。
- EV-04 交付 HTML 严格执行 assets 风格规范 → P4 自检「风格规范核对」。
- EV-05 dws v1.0.55 支持 视图/仪表盘/图表/表单（推翻旧结论）→ references/dws_command_ref.md + aitable_platform_rules.md。
- EV-06 方案视觉锁定「案例视觉」（PR_DESIGN.md 替换）+ callout 语义底色/无代码字面残留 → assets/PR_DESIGN.md + references/report_style_guide.md v1.1。
- EV-07 view filter/group 协议已解（叶子=operands+eq+选项key；UI 样例反查为权威）→ dws_command_ref.md 实操纪要。
- EV-08 仪表盘 4 行布局实操（48 列网格 / chart filter ANY_OF / STATISTICS 配色 / STACKED_LINE 多系列 / GRID_VIEW 复用视图 / chart delete --yes）→ dws_command_ref.md 实操纪要 + scenario_01 S4.5。
- 回滚点：evolution/backups/20260905-1035_*.md（12 份全量快照）。

