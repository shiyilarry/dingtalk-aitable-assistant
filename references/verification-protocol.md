# 交付验证协议（双轨：视觉辅助 / 纯代码）

> 适用：本 SKILL 的**所有交付前验证**（看板搭建、数据表同步、审计）。
> 背景：用户使用的模型**不保证具备视觉能力**。本协议保证——**无视觉也能完成 100% 的判定**，视觉只是"提速项"。
> 建立日期：2026-09-10（真实项目实证沉淀；所有命令与断言均实测过）

---

## 0. 三条铁律（比任何工具都重要）

1. **生成者不得用自己的口径证明自己**。脚本打印 `OK` ≠ 成功；必须用**平台侧独立源**复核。
2. **每个交付物至少有一个"平台侧独立源"**：CLI 回读（`dashboard get`/`chart get`）或服务端聚合（`record stats`/`record group-stats`）。
3. **视觉只作抽检，不作唯一依据**；无视觉时**不降低标准**——改用 DOM 断言 + CLI 断言覆盖同一批检查项。

---

## 1. 判定源分级（L1 最强 → L4 最弱）

| 级别 | 判定源 | 能证明什么 | 是否依赖视觉 |
|---|---|---|---|
| **L1** | **CLI 回读**：`dashboard get` / `chart get` / `field list` / `view get` / `record stats`·`group-stats` | 组件是否存在、布局数值、config 键集、字段归属、**数值是否与图表口径一致** | 否 |
| **L2** | **页面 DOM 断言**：元素存在/可见/尺寸/文本/类名变化 | 元素能否被点击、面板是否打开、toast 文案 | 否 |
| **L3** | **网络与控制台**：`page.on("response")` / `page.on("console")` / 元素属性 diff | 前端是否报错、接口是否 4xx/5xx | 否 |
| **L4** | **视觉**：截图 + 读图 | 排版美观度、留白、色彩、肉眼异常 | **是** |

**规则**：L4 只用于"L1–L3 都覆盖不到的观感类问题"（如留白、视觉重心）。**L4 发现的任何问题，都必须回到 L1/L2 复现并定位**，不得只凭截图下结论（截图会因裁剪/缩放/遮挡产生假象）。

> ⚠️ **L1 数值取值路径（2026-10-01 采纳 EV-202609-46）**：`record stats` 的数值在**两层嵌套 `results`** 里——路径＝**`data.results[0].results[0].value`**；**解析失败禁 `or 0` 兜底**（会把「解析失败」静默变成「行数 0」）；数值须与 `record query --all` 行数**双通道对照**后才写进复核报告。

---

## 2. 无视觉是否可行？—— 是，且有完整替代方案

| 视觉时代码里最容易被忽略的三件事 | 无视觉替代方案 |
|---|---|
| 用截图目测坐标去点 | **禁用坐标点击**；一律用 `xpath=` / `css=` / `text=` / `role=` 定位（跨 frame 有偏移，坐标必错） |
| 用眼睛看"有没有打开面板/有没有报错" | **文本断言**：`innerText` 匹配「文档错误/数据已保存」= BROKEN；匹配「图表类型/数值/分类」= 面板已开 |
| 用眼睛看"表格有没有数据/图表有没有柱子" | **DOM 计数 + CLI 复算**：`locator.count()` 数数据行；`record stats/group-stats` 独立算应显示值 |

---

## 3. 定位库（实测可用，直接复制）

### 3.1 页面分域（钉钉 AI 表格看板页）

| frame | URL 特征 | 里面有什么 |
|---|---|---|
| `frame[0]` | `alidocs.dingtalk.com/i/nodes/...` | 宿主页：**钉钉文档左栏**、顶栏 |
| `frame[1]` | `.../iframe/notable?...` | **AI 表格本体**：文档树、看板卡片、弹窗、编辑面板 |

### 3.2 关键元素定位（全部实测）

| 目标 | 定位方式 | 备注 |
|---|---|---|
| 左栏折叠 | XPath（frame[0]）：`/html/body/div[1]/div/div/div/div/div[1]/div/div[1]/div[4]/div/div/div[1]/div[1]/div[3]/div/div` | 28×28；截图前点它收左栏 |
| AI 表格隐藏边栏 | XPath（frame[1]）：`/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div[1]/div[2]/div[1]/div[1]/div[1]/div/div/div[2]/div/div/button[2]` | 24×24；收掉表格边栏 |
| 图表卡片容器 | `div.chart-item-wrapper` + `has_text("图表名")` | 卡片文本会含标题，注意用精确匹配避免误命中 |
| 卡片标题 | 卡片内 `div.name` | 精确文本 = 图表名 |
| **三点菜单按钮** | 卡片 header 区（`r.top < card.top+58` 且 `r.left > card.left+width-70`）内的 `button` | 图标为竖排三点（`path 3x12`）；**悬停后才出现** |
| 菜单项 | 文本：`编辑图表` / `重命名` / `导出为图片` / `删除` | **表格类（GRID_VIEW）没有「编辑图表」**，属正常 |
| 引导弹窗「跳过」 | 文本包含 `跳过`（真实文案 `跳过(1/4)`） | 点 1 次即关；多轮调用直到无命中 |
| 公告弹窗 | 顶部尺寸 ≤44 且 `class/aria-label` 含 `close` 的元素 | 例「全新组件上线」，必须点右上角 × |

### 3.3 悬停与点击的稳妥姿势

```python
# 悬停：真实鼠标移动 + 合成事件双保险（避免 Playwright actionability 超时）
card = fr.locator("div.chart-item-wrapper", has_text=TITLE).first
bb = card.bounding_box()                      # 页面坐标
page.mouse.move(bb["x"] + 30, bb["y"] + 20)
page.mouse.move(bb["x"] + bb["width"] - 26, bb["y"] + 20)   # 移到头部右侧
page.wait_for_timeout(1500)

# 点击：优先用「元素级 click()」绕开可操作性检查（页面常有遮罩拦截）
fr.evaluate("(t) => { /* 找到目标元素 */ el.click(); }", TITLE)
# 兜底：locator.click(force=True)
```

---

## 4. 断言模板（纯代码，可直接套用）

### A. 图表「能否编辑」（替代"点开看看"）

```python
# 前置：悬停卡片 → 点三点 → 点「编辑图表」
page.wait_for_timeout(4000)
res = fr.evaluate("""() => {
  const txt = document.body.innerText || '';
  return {err: /文档错误|数据已保存|请刷新重试/.test(txt),
          panel: /图表类型|数值|分类|聚合方式/.test(txt)};
}""")
verdict = "BROKEN" if res["err"] else ("OK" if res["panel"] else "UNKNOWN")
```
> 判定标准：**出现报错文案 = BROKEN；出现配置面板关键词 = OK**。二者都没出现 → 记 UNKNOWN 并补 CLI 断言。

### B. 布局合规（L1，权威）

```python
d = dws(["dashboard","get","--base-id",B,"--dashboard-id",D,"--format","json"])["data"]
lay = {l["i"]: l for l in d["layout"]}
# ① 实体 ↔ 布局一一对应（键名是 i，不是 chartId！）
assert len(lay) == len(d["charts"])
# ② 每行 w 合计 = 48（48 列网格）
rows = {}
for l in lay.values(): rows.setdefault(l["y"], []).append(l)
for y, items in rows.items():
    assert sum(i["w"] for i in items) == 48, ("行未铺满", y)
# ③ 表格类组件最小宽 16（否则 UI 会静默撑宽 → 顺推错位）
for c in d["charts"]:
    if c["chartType"] == "GRID_VIEW":
        assert lay[c["chartId"]]["w"] >= 16
```

### C. config 键集完整（L1，修"编辑报错"的判据）

⚠️ **两条必须知道的前提（2026-09-10 实证）**：
1. **`chart get` 回读的 config 是"归一化后"的**——平台会剥离空值键（如 `name`、`widthMap`、`hiddenFields={}`、`view=""` 等可能不出现）。所以**不能拿"写入形态"去比对"回读形态"**；
2. **断言必须按图型分级**，否则会出现"假失败"（本项目实测：把 STATISTICS 的环比/趋势类键当必需 → 误报 1 项）。

```python
OPT_STATS = {"comparisonCalculationType","comparisonDescColor","comparisonLayout",
             "comparisonPeriodType","comparisonType","trendColor","trendLayout"}  # 环比/趋势：可选
sample = {t: set(cfg(BETA_SAMPLE_ID[t])) for t in types}   # 样本取自“另一个已验证盘”的同型图

for name in targets:
    c, t = set(cfg(DASH, name)), chart_type(name)
    ref = sample[t]
    if t == "HISTOGRAM":                 # 唯一“缺键即崩”的图型 → 要求完全一致（本项目=35 键）
        miss = ref - c
    elif t == "STATISTICS":              # 环比/趋势类为可选
        miss = (ref - OPT_STATS) - c
    else:                                # 其余图型：不得缺少样本键（允许超集）
        miss = ref - c
    assert not miss, (name, sorted(miss))
```

> **判据优先级**：**键集断言只是"预警"；「能否点开编辑图表」（L2）才是最终判据**。L1 报警但 L2 通过 → 先核对是否属于"归一化/可选键"，不要急着重写配置。

### D. 数值正确（L2/L1，服务端复算）

```bash
# 不分组聚合（statsType 必须大写）
dws aitable record stats --base-id B --table-id T --stats '[{"fieldId":"F","statsType":"COUNT"}]' -f json
# 分组聚合（statsType 必须大写 · v1.0.62 起统一）
dws aitable record group-stats --base-id B --table-id T --group '[{"fieldId":"G"}]' \
    --stats '[{"fieldId":"M","statsType":"SUM"}]' -f json
```
> 用服务端结果与"图表应有值"逐项比对；**这是唯一能证明"图上数字对"的手段**（截图上肉眼读数不可靠）。

### E. 页面无报错（L3）

```python
errors = []
page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
page.on("response", lambda r: errors.append("%s %s" % (r.status, r.url)) if r.status >= 400 else None)
# …操作…
assert not errors, errors
```

### F2. 组件渲染断言（L2 · 必须"先滚入视口"）

⚠️ **钉钉看板的组件是按视口惰性渲染的**：滚出视口的图表/表格会被卸载 → **整页截图或 DOM 查询都会拍到"空表/空图"的假象**（本项目实测：截图上 4 张表"只有行号没列"，滚入视口后复测全部正常）。

```python
el = fr.locator("div.chart-item-wrapper", has_text=NAME).first
el.scroll_into_view_if_needed()          # ① 先滚进视口
page.wait_for_timeout(2500)              # ② 等渲染
cells = fr.evaluate(JS_COUNT_TEXTS, NAME)  # ③ 再断言（统计卡片内非数字文本数）
assert cells > 10, "表格无列（可能是 view 未设置 / 无数据）"
el.screenshot(path="shots/tbl_%s.png" % NAME)   # ④ 元素级留痕
```

**判定阈值（按组件类型）**：

| 组件 | 通过标准 | 备注 |
|---|---|---|
| 指标卡 | 卡片内出现数字文本 | 数值须与服务端聚合一致 |
| 图表 | 卡片内出现系列/坐标轴文本，或 DOM 有 svg 图形节点 | 空图多因 `view` 非空或数据为 0 |
| 表格 | **出现列名（≥2 个非数字文本）** | 仅"行号"= 未渲染/`view` 缺失；**表头在、无数据行 = 底表本来就空（正常）** |

### F. 元素可见性（L2，替代"看一眼"

```python
loc = fr.locator("div.chart-item-wrapper", has_text=NAME)
assert loc.count() >= 1
assert loc.first.is_visible()
box = loc.first.bounding_box()               # 尺寸>0 才算真的渲染出来
assert box and box["width"] > 100 and box["height"] > 80
# 元素级截图留痕（不用于判定，仅存档）
loc.first.screenshot(path="shots/%s.png" % NAME)
```

### G. formula 字段复算对账法（L1 · 证明"公式列算得对"，不依赖目视）

> 适用：含公式字段（对等判定 / 差异标记 / 派生口径）的同步与审计。

formula 字段 CLI 不可建、不可写——**但可被 `record group-stats` 按值分组**，据此形成独立判定通道：
1. 本地按公式语义**全量复算**每一格，统计各结果值的分布；
2. 服务端 `record group-stats --group '[{"fieldId":"<公式字段>"}]'` 取实测分布；
3. 两分布**逐项对账**，全等即通过。

**判据**：分布逐项一致。**边界**：复算必须严格还原公式语义——先小样本定标「空 / 0 / 空文本」的参与方式（实测：平台公式中空白参与数值比较按 0 处理，曾因"空≠0"假设偏差 86 格）；语义还原错则复算失真。

### H. 时间保真三层证据链（时间 / 编码类数据必做）

三层逐层留证（每层独立结论、不得跳层；结论必须写明是"读取侧"还是"入库侧"问题）：

| 层 | 对象 | 判据 |
|---|---|---|
| L1 文件原文 | 编码与时间形态 | **全量**严格解码（如 GBK 零替换字符）——**禁抽样断言** |
| L2 解析结果 | 程序读出的值 | 与原文逐字符比对 |
| L3 库内现值 | 落库后的值 | 按批次窗口统计形态指标（如秒位为 0 的占比）定位"丢秒"批次 |

**「日期错位」的唯一铁证判据**：逐行差集中出现**"库内多余行"（extra>0）**；extra=0 ⇒ 不存在日期错位，偏差只在秒位（实测：逐行差集 extra=0，秒位丢失集中在特定入库批次）。

### I. 写后复核：容忍「读后写延迟」

平台读链路存在**读后写延迟**（实测：写入后即时重查读到 0 行、数秒~20 秒后可见；**字段配置类写操作同样适用**——`field update` 追加单选选项后服务端返回 `verified`，读侧仍为旧值，约 1 分钟后双读通道才可见）→ **禁止以「即时回读」判定写入失败**。

- **触发面（渠道）**：`record upsert`（含「随本批新建的单选选项」维度，筛选索引建立更慢）与 `field update`（字段配置 / 选项变更）**均含**。
- **复核参数**：一律「**先等 ≥60s（硬底线）再回读、等间隔轮询**」——1 分钟为**用户明确需求**（跨项目两次实证：选项追加后回读无新值；立即拉数不完整），**不得因表小或赶时间而跳过**；轮询总窗口建议 ≥4 次 × ≥15s，大批量写入 / 新建选项宜再放宽。
- **铁律①：「服务端受理」≠「读侧可见」**——返回 `status=success` / `verificationStatus=verified` 只代表写入已被受理，**不得据此判定复核通过**。
- **铁律②：禁止以「写 / 读通道回显 id 是否一致」判断是否落地**——实测 `field update` 写通道回显的选项 id 与读通道不一致（两个读通道彼此一致）→ 复核判据按「**名称 + 原 id 保留集合 + 数量变化**」构造。
- **排查次序（复核疑似「没写进去」时）**：① 先按**非选项列**（如店铺名称）交叉验证是否已落库 → ② 再判选项索引是否就绪 → ③ 排除「视图过滤」假设时用 `view list` 逐条核对视图 filter（CLI `--filters` **不读视图配置**，与 UI 视图是两条互不相交的链路）。

### J. 缺口 / 差异集核对：现算 + 口径分层（两个维度都不可省）

- **口径维度（多源写入的表）**：采集侧台账 ≠ 库内实况。台账记的是"采集动作状态"，库内还有夜间批 / 人工件 / 其他系统等多条写入链路（实测：两口径相差 380 格"假缺口"——库内实际有数据；另有 90 格"台账说齐、库内 0 行"）。
  → 对外清单**一律以库内实况现算为准**；「台账 ∩ 实况」交集才是铁定要补项，其余分列并标注核实建议。
- **时点维度**：差异集不是静止的——旧时点清单会漏掉窗口内新入库（实测：全量完成后待更新集 41 格 → 写前重查 48 格）。
  → **写前一刻重算**，预览与写入间隔最短。
- **纪律**：任何"缺多少"的结论必须注明**口径 + 现算时间**。

### K. 逐格比对：先类型归一，再比较（2026-09-24 采纳 EV-202609-30）

`record query` 回读的 number 字段值统一按**字符串**返回（形如 `"8576"`）——**等值比较禁止裸 `!=`**：一侧 int 一侧 str 会把值相同的格全判为「不一致」（伪差异），两侧同为字符串时又可能掩盖真实差异（求和的 `int + str` 直接 TypeError）。
→ **纪律**：比对前先过归一（int / float / 字符串三态：strip → float → int 降级），**左右两侧用同一归一函数**；text / 日期字段本就字符串 → 归一函数对未知类型**保守降级为字符串比较**，不得强行转数。

### L. 执行凭证对账：工具的反馈是「客户端视角」，判据只认目标侧回读（2026-09-24 采纳 EV-202609-35）

写操作工具的回报（返回码 / 审计日志 / 超时）**都是客户端视角**——服务端收到请求即原子执行；客户端在响应前超时 / 断连时，日志会记「失败 / 缺失」，但服务端**可能已执行完成**（实测：审计记 405,140 行 vs 计划 410,553 行，出现 5,413 行「账面缺口」——逐条归因后全部为客户端视角失真，目标侧实况全齐）。
→ **对账纪律**：① 差额**先归因再下结论**——先做多重集匹配（成对顺序互换 → 合计相等即消解），再查单点（客户端超时 → 目标侧核验）；② 权威判据＝**目标侧回读**（容忍读后写延迟，见 §4-I）；③ **未归因完成的差额不得触发重写**（create 非幂等，重写＝重复风险；与 §4-I、error_handling.md 幂等分档同源）。

---

## 5. 视觉轨（模型支持多模态时）

**用途**：排版/留白/视觉重心/色彩等观感类问题；以及"表格里到底显示了哪些列"这类**快速定性**。
**规范**：
1. 截图前**先点两条 XPath**（左栏折叠 + 隐藏边栏）+ 清弹窗 → 画面干净、信息密度最高；
2. 优先 `full_page=True`；要点看细节时用 `clip` 局部放大；
3. **截图结论必须回到 L1/L2 复现**（例：截图看起来"空"，要用 `dashboard get` 确认布局 + DOM 断言确认渲染，再定性）；
4. 深浅色主题都截（深色下细节对比更清晰）——如用户已切换主题，直接沿用。

---

## 6. 交付前检查清单（逐项打勾）

| # | 检查项 | 判定源 | 通过标准 |
|---|---|---|---|
| 1 | 组件数量/名称齐全 | L1 `dashboard get` | `len(charts)` = 计划数；名称无默认名（`STATISTICS Chart` 等） |
| 2 | 布局合规 | L1 | 实体↔布局一一对应；每行 w=48；表格 w≥16 |
| 3 | config 键集完整 | L1 `chart get` | 与同型可编辑样本键集一致（HISTOGRAM 35 键） |
| 4 | 字段归属正确 | L1 | `sheet` 存在；`measure/dimension/filter` 字段属于该表；`view=""` |
| 5 | 数值正确 | L1 服务端聚合 | 与"应有值清单"逐项一致 |
| 6 | 可编辑 | **L2 DOM 断言** | 逐图点「编辑图表」→ 无报错文案、面板关键词出现 |
| 7 | 页面无控制台/接口错误 | L3 | 无 4xx/5xx、无 error |
| 8 | 观感抽检 | L4 视觉 | 无留白/错位/遮挡（有视觉时执行；无视觉则跳过并在交付说明中注明） |
| 9 | 留痕 | — | 每项检查输出命令与结果，存档到 `tmp_excel_dump/audit_*/` |

---

## 7. 失败时的最小诊断顺序（省时铁律）

1. **先看真实错误码**（`dws` 返回的 `code`/`message`/`details`），不猜；
2. `DASHBOARD_STORAGE_NOT_READY` → **没有 UI 会话窗口** → 用 `DashSession`（自开页面 + 每 4 笔 reload 续窗）；
3. `Dashboard layout item changed concurrently` → **该行超载**（某行 w>48 或被撑宽）→ 用「取配置→删除→按目标位置重建」绕开，**不要再叠加自定义重试**（CLI 已内重试 3 次）；
4. 编辑报错（UI 文案）→ **config 键集不全** → 用同型可编辑样本覆盖数据绑定后回写；
5. 图"空" → ① `view` 是否非空（红线：必须空）；② 数据表/视图是否有效；③ 服务端聚合复算是否本来就为 0；
6. 表格"只有行号没列" → ① **`view` 是否被清空**（GRID_VIEW 必须给 viewId）；② 是否**未滚入视口**（惰性渲染）；③ `hiddenFields` 是否异常；
7. 以上都排除后才动用视觉，并记录为"平台侧行为"写入知识库。

---

## 8. 本次实测留痕（2026-09-10 · 项目实证 · 数值已脱敏）

| 检查项 | 命令/断言 | 结果 |
|---|---|---|
| 两盘布局 | `dashboard get` 逐行 w 合计 | B 版 6 行全 48；旧盘 7 行全 48（收口后） |
| 渠道两图键集 | `chart get` vs 同型样本 | 修前 23–24 键（缺 11 键）→ 修后 **35 键 = 样本** |
| 可编辑（L2） | 悬停→三点→「编辑图表」→ 文本断言 | 两盘各 3 张图 **OK（无报错文案）**；表格类菜单无「编辑图表」，非故障 |
| 数值（L1） | `record stats` / `group-stats` | 在售 SKU / 事实表行数 / 4C 四色系×双渠道 共 8 项数值——**逐项与图表口径吻合 ✓**（具体数值脱敏） |
| UI 定位 | 两条 XPath 点击 | 左栏折叠 frame[0] ✅；隐藏边栏 frame[1] ✅ |
