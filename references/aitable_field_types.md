# 钉钉AI表格字段类型与读写格式（2026-09 实测）

## 字段对象结构（必记）
```json
{"fieldName":"字段名","type":"文本/类型值","config":{...}}
```
- **不是** name/property；选填、数字等都要 `config`。

## 常用类型速查
| 类型值 | 说明 | config 示例 |
|---|---|---|
| text | 文本（首列主字段常用） | {} |
| number | 数字 | {"formatter":"INT"} 或 FLOAT_2 / THOUSAND |
| currency | 货币（金额建议用它，带 ¥） | {"currencyType":"CNY","formatter":"FLOAT_2"}（formatter 可省略默认 FLOAT_2） |
| singleSelect | 单选 | {"options":[{"name":"甲"},{"name":"乙"}]} |
| multipleSelect | 多选 | {"options":[{"name":"甲"}]} |
| date | 日期 | {"formatter":"YYYY-MM-DD"} |
| user | 人员（单选多选） | {"multiple":false} |
| department | 部门（钉钉组织架构树） | {"multiple":false}；写入 [{"departmentId":"298295560","name":"信息数据部"}] |
| checkbox | 勾选 | — |
| url | 链接 | 写入 {"text":"...","link":"https://..."} |
| richText | 富文本 | 写入 {"markdown":"..."} |
| unidirectionalLink | 单向关联（显示对方主字段） | {"linkedTableId":"<tableId>","multiple":false}（仅同 Base 内；反向不会自动建） |
| bidirectionalLink | 双向关联（对方表自动生成反向字段） | {"linkedTableId":"<tableId>","multiple":false}；删除时对端同步删除 |
| lookup | 关联引用（须基于本表已有单向/双向关联字段） | {"associateField":"<本表关联字段ID>","valuesField":"<被关联表字段ID>","aggregator":"SUM\|COUNT\|MAX\|MIN..."} |
| filterUp | 查找引用（无需关联，按条件筛选+聚合/取值） | {"aggregator":"SUM\|COUNT\|AVERAGE\|MAX\|MIN\|VALUES","targetSheet":"<表id>","filters":[{"fieldId":"<源表字段>","operator":"equal","currentSheetFieldId":"<本表字段>","link":"AND"}],"valuesField":"<源表取值字段>"} |
| creator/createdTime… | 系统字段（只读） | 自动回填 |

## 写记录 value 格式
| 类型 | 写入 |
|---|---|
| text | "内容" |
| number | 123 或 "123" |
| singleSelect | "选项名"（须已存在于选项集） |
| date | "2026-08-01" |
| user | [{"userId":"...","corpId":"..."}] |
| checkbox | true/false |

## 约束（血泪教训）
1. 首列即主字段：**不可隐藏、不可删除** → 首列必须是**有实际业务意义的字段**（名称/编码/日期/类型等），禁止把"自编序号"类占位列放首列；各表首列放什么，在方案档案 §5 逐表标注。
2. 自编单号/自动编号：当方案业务需要（单据号/流水号等）或**用户明确要求**时才创建，字段类型用界面「自动编号」（自增流水，可配前缀/位数/起始值），可作记录主键；但**同样不得建在首列**（主字段位留给业务字段）。该类型 CLI 可建性尚未核验——建列以界面操作为准，勿臆造 type 值。
3. **字段类型创建后不可改**：类型在方案阶段与用户确认；名称/选项可改。
4. 公式字段当前服务端**不支持创建**；依赖公式的展示需求引导到界面配置或本地计算后同步。
5. **关联字段（单向/双向）CLI 实测可创建**（2026-09-05 实测成功）：此前"关联可能失败就降级 text"属过度防御；方案设计应优先使用真关联。lookup（关联引用）需先存在关联字段；filterUp（查找引用）可不依赖关联。**filterUp「取原值」= `aggregator:"VALUES"`（2026-09-09 实测 CLI 可创建；UI 界面建的原值查找引用回读亦为 VALUES）**——此前测 NONE/FIND_FIRST/FIRST/ANY 均被拒（"not supported for external configuration"），VALUES 才是正确枚举；filters 元素可带 `link:"AND"`。config 结构见上表，实施前用 `dws schema` 校验，失败再降级并在报告说明。
6. 关联/引用字段只读不可直接写入；关联关系写入用 record create/update 的 `{"linkedRecordIds":["recId..."]}`。
7. 关联显示仅对方主字段；要展示其它字段用关联引用/查找引用。
8. 选项值被记录使用后删除会导致历史数据丢失。
9. 单选/多选「同步其他表选项」（含级联筛选）是界面配置能力：CLI **不能创建**同步字段。实测（2026-09-07）：界面同步建立后两表选项 **id 完全共享**（同一选项池）；CLI field create 即使显式传 option id 也会被服务端**忽略并重新生成** → 无法 CLI 复制同步；同步字段的写入与普通单选一致（按选项名）。需在方案中给出界面步骤。
10. 金额类字段用 currency（CNY），数字类用 number；从外部导入的单号/编码列存**字符串值**（防 1E+ 科学计数法）；需表格自动生成流水单号的场景用「自动编号」字段（见第 2 条），两者场景不同勿混用。
11. department（组织树）列写入值 = `[{"departmentId":"...","name":"..."}]`（2026-09-07 实测）；若某列要同时作跨表 filterUp 相等匹配键，建议镜像一个 text 键列（组织树值随组织架构变，text 键需靠命名规范保持一致——设计决策点在方案中与用户确认）。
12. **number 字段读回为字符串**（2026-09-24 采纳 EV-202609-30）：`record query` 回读的 cells 值对 number 统一按**字符串**返回（形如 `"8576"`）→ 算术 / 等值校验**必须数值归一**（int / float / 字符串三态；字符串 strip → float → int 降级），且左右两侧用**同一归一函数**；裸 `!=` 会把「值相同、类型不同」全判为不一致（伪差异）。text / 日期本就字符串 → 归一函数对未知类型保守降级为字符串比较，不得强行转数。
13. **singleSelect / multipleSelect 选项传值：先核值、再核形态**（2026-10-01 采纳 EV-202609-42）：报 `SELECT_OPTION_NOT_FOUND` 的排查次序＝① `field get` 对 option id **逐字符复核**（转抄漏字符是肉眼盲区）→ ② 核选项归属 → ③ **最后**才怀疑传值形态（`{"id"}` / `{"id","name"}` / 选项名多形态均可用）；**「形态不支持」结论必须先经零污染实验（对已存在行 no-op update）证伪**方可下。书写取值优先「选项名字符串」（依赖选项名唯一；同名 / 近名风险用 id 形态）。
