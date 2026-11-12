# argument-review fixtures

论证审读的回归样例：14 个短例，输入与预期分成两个文件。用于验证「格式指标合格」之外的论证审读能否发现自设靶子一类的缺陷，同时不误伤正常的限定、比较与反驳。

## 边界

- 全部来源与草稿是合成的 toy 文本。型号 `M-100`、`G-1`，标准号 `TS-200`，以及「2 号楼西侧走廊」都是虚构的，不与任何真实产品或真实场地对应。
- 不含用户会话、个人档案、真实产品资料、私密路径或内部主机，也不含任何外网链接。复制到别处不携带任何上下文。
- 本目录只有样例，不含规则。论证审读的规则写在 `de-ai-flavor` 的正文与引用文件里；样例与预期必须先冻结，规则改动之后进行，避免照规则倒推样例。

## 文件

| 文件 | 用途 |
|---|---|
| [inputs.json](inputs.json) | 受测代理唯一可见的输入：`id`、`role`、`request`、`sources`；正文例另有 `draft`，个别例另有 `user_question`、`format_record`、`before`、`after`、`review` |
| [expected.json](expected.json) | 只给评分者：逐 ID 的 `disposition`、`reason`、`must_report`、`must_not_report`、`must_keep`、`must_remove`、`tolerance` |

受测代理只拿到 `inputs.json` 里对应的一条（可整份传入，也可只传该条），不拿 `expected.json`。输入里不带「本例应保留／应修改」之类的标签，`id` 按序号编排，顺序与能否通过无关。

## 用例分布

| id | 角色 | 处置 | 覆盖点 |
|---|---|---|---|
| ar-01 | `prose_reviewer` | keep | 有来源、忠实原意且相关的反驳 |
| ar-02 | `prose_reviewer` | revise | 自设极端命题：把用户提问写成他人的错误主张 |
| ar-03 | `prose_reviewer` | keep | 明确实验对象、版本与条件的限定 |
| ar-04 | `doc_reviewer` | reject_review | 被格式全绿与「严谨限定」误导的放行结论 |
| ar-05 | `prose_reviewer` | revise | 相同数字推出假想误读 |
| ar-06 | `prose_reviewer` | keep | 有来源支持的安全缺陷 |
| ar-07 | `prose_reviewer` | revise | 格式指标全部合格但论证对象不存在 |
| ar-08 | `adjudicator` | reject_review | 错误引用 before、要求加回假想提醒 |
| ar-09 | `prose_reviewer` | revise | 正面措辞残留同一对立框架 |
| ar-10 | `prose_reviewer` | keep | 两种方案的能力与迁移成本比较 |
| ar-11 | `prose_reviewer` | revise | 放大来源主张后再批评 |
| ar-12 | `prose_reviewer` | keep | 指标口径差异说明，未假定读者犯错 |
| ar-13 | `prose_reviewer` | revise | 内部 `cannot_prove` 无选择地铺成正文提醒 |
| ar-14 | `prose_reviewer` | keep | 用户明确要求的假设分析与数学反证 |

分布：6 个 revise、2 个 reject_review、6 个 keep。`ar-08` 的 `before` 与 `after` 原句都在 `inputs.json` 里，可逐字核对。

## v2 修订记录（只补前提，不改判定）

v1 的四个保留例正文里有 sources 没有明示的前提。v2 只补足这些前提，使既定标签有事实依据；14 例的 `disposition` 分布仍为 6 revise / 2 reject_review / 6 keep，`must_report`、`must_not_report`、`must_remove` 未改动。

| id | v1 缺失的前提 | v2 的处理 |
|---|---|---|
| ar-01 | S1 只写「2 号楼西侧走廊」，未写单层；-70 dBm 只是划分线，未称为验收门限 | S1 补「单层」「验收门限 -70 dBm」，并注明只测这一层；draft 补测点间隔 10 m 一处细节 |
| ar-06 | 无固件版本，也没有「断电重启后回到出厂值 20 dBm」的观测 | 新增 S3 固件发布说明，写明固件 1.4.2 的断电恢复行为 |
| ar-10 | 未给覆盖推算，也未给改布局时的改动量比较 | S1 补按单跳累计覆盖（甲 440 m、乙 400 m）；S2 补两方案改布局改动量的比较 |
| ar-12 | S2 只有「本区域覆盖率 99%」，未指明口径 | S2 补同页口径注：覆盖率按位置计，即测点通过率 |

这些都是合成设定，不是外部观测：补进去的数值与行为由样例自身规定，不引用任何真实产品或真实试验，也不能当作外部事实引用。

## v3 修订记录（只修两处预期内在矛盾）

v2 冻结之后，把「预期要求」逐条对回「来源实际支持的内容」时，确认了两处预期自身的矛盾。v3 只修这两处：标签、类别与判分口径不动，其余 12 例逐字段未改，分布仍为 6 revise / 2 reject_review / 6 keep。

| id | 已确认的矛盾 | v3 的处理 |
|---|---|---|
| ar-04 | `must_keep` 第三项要求「维持现有天线的部署决定可作为正面陈述保留」，但唯一来源 S1 只写 12 个测点、3 个低于 -70 dBm、位于金属货架背面，没有任何支持该决定的依据；同一例的处置是 `reject_review`，`must_report` 又要求指出正文需要修订，两条要求互相抵消 | `must_keep` 只留来源实写的两项（12 个测点；3 个低于 -70 dBm 且位于金属货架背面）；「更换增益不改变遮挡关系」移入 `tolerance`，允许作为一般物理解释出现，不再作为必须回读的来源事实，也不当作「可以继续部署」的证明；删除要求保留部署决定的一项 |
| ar-13 | 输入没有写本轮决策范围，预期却要求删掉雨季衰减、五年器件老化等提醒；「与本轮无关」只能由评分者自己的相关性判断得出 | 在 `inputs` 补合成 `user_question`「安排本周同一层走廊的复测，写一段结论」，明确本轮范围，且不在 `request` 里给答案；`tolerance` 相应限定为可保留测量区域（单层、10 m 间隔）与当时条件（11 月一个班次）这一类范围限定及复测建议，对雨季衰减、五年老化等不作无限容许 |

两处都只动合成样例自身的设定与措辞，不引用外部观测。ar-04 的 `reason` 补记了部署决定的来源缺口，并明说指出它属正确发现、不列入 `must_not_report`；ar-13 的 `must_report`、`must_not_report`、`must_remove` 四项一字未改。v1、v2 期间对这些点的既有记录（baseline 对 ar-06、ar-10 的来源缺失指摘，r3 评分对 ar-04 部署决定与遮挡关系、ar-13 季节/老化相关性的记录）原样保留，未改判为误报。

## 冻结与运行协议

1. **先冻结。** 运行前记录 `inputs.json` 与 `expected.json` 的 sha256（见下「冻结记录」）。两个文件任一改动，都要重新记 hash，并把 14 例全部重跑；不保留旧 hash 下的部分结果。
2. **同模型、同配置比版本。** 同一组样例分别跑旧版与新版技能，两次使用同一模型与同一套配置（温度、工具权限、上下文预算一致），只换技能版本。模型或配置变了就另起一轮，不与上一轮混算。
3. **新版跑两次新上下文。** 两个彼此独立、互不共享历史的新上下文各跑一遍。任何一次漏报、误删或错判都记录并从样例或规则侧修复；不得只报其中结果较好的一次。
4. **原始输出落盘。** 每次运行保存实际输入（对应当前 hash）与模型返回的原文，不改写、不摘要后归档；评分与报告都引用原始输出。
5. **预期不进入受测上下文。** 公开分发目录同时包含输入与预期，目录隔离本身不是安全保证。运行时只向受测上下文提供输入和方法，不检索本README或expected.json；需要工具读取时显式限制允许的路径，并记录额外读取这一隔离偏差。评分由未参与该次改写的独立评分角色完成，写作者不自评通过。
6. **不预设旧版失败。** 报告写实际结果，包括旧版通过的样例。
7. **有限的保证。** 这组样例针对的是已知的六类正文错误、两类评审错误和六类应保留论述，只证明这些样例上的表现，不构成对未来文档的普遍保证，也不支撑「零错误」一类表述。没跑过的组合不写结论，报告里不出现未执行运行的成绩。

## 判分口径

- `disposition` 三值：`revise` 表示正文须按 `must_remove` 去掉相应意义范围并保留 `must_keep` 的事实；`keep` 表示正文可原样保留；`reject_review` 表示被审的评审记录或意见无依据，应驳回且不得据此往正文加内容。
- `must_report` 是要点核对：受测角色必须给出的发现或裁决，措辞不限。`must_not_report` 列出常见的错误报告与错误放行理由，命中任一项即该例不合格。
- `must_keep` 是事实性断言（数值、单位、条件、来源归属）。核对它们在修订文本或裁决理由中仍可回读，不要求字符一致。
- `must_remove` 是**意义范围**，用描述写法给出，不是字符串禁词表。评分判断的是该意义是否仍以任何措辞出现，不做词表匹配，也不因为换了一组同义词就判为已删除。
- 保留例允许润色与断句，不要求字符不变；但**不得以删除否定词、限定条件或对比措辞作为通过方式**——`不能`、`也`、`而非`、`不是` 在保留例里承载的是内容。
- 格式指标（加粗密度、破折号、表格、问句标题、长单元格）不参与判分，既不加分也不扣分；输入里附带的格式检查记录按规则处理，不代替论证结论。

## 结构检查（只查结构）

```bash
python3 - <<'PY'
import json, pathlib
d = pathlib.Path("skills/de-ai-flavor/fixtures/argument-review")
inp = json.loads((d / "inputs.json").read_text(encoding="utf-8"))
exp = json.loads((d / "expected.json").read_text(encoding="utf-8"))
ids = [c["id"] for c in inp["cases"]]
eids = [c["id"] for c in exp["cases"]]
assert len(ids) == 14 and len(set(ids)) == 14, "ID 数或唯一性不对"
assert ids == eids, "两份文件的 ID 顺序或集合不一致"
assert all(c["disposition"] in {"revise", "keep", "reject_review"} for c in exp["cases"])
for c in inp["cases"]:
    assert c["role"] and c["request"] and c["sources"], c["id"]
    assert "draft" in c or {"before", "after", "review"} <= set(c), c["id"]
for c in exp["cases"]:
    assert c["reason"] and "must_keep" in c and "must_remove" in c, c["id"]
print("structure ok:", len(ids), "cases",
      {k: sum(1 for c in exp["cases"] if c["disposition"] == k)
       for k in ("revise", "reject_review", "keep")})
PY
```

这只证明 ID 唯一、两个文件对齐、字段齐备。它**不**证明任何一例的语义判断已被核对——语义核对只有跑过模型并对照原始输出的评分才算。

## 冻结记录

当前冻结的是 v3。更早两版的 hash 只用于说明既有结果跑在哪一版输入上，不再作为当前判分依据：

- v2：`inputs.json` `3b086af0c8b819c528e95029efa00cf05be590911e005d2e6797f68e08016d75`、`expected.json` `8d35c94e8c98a1bef798880a84299b6958043adfb111c0be5255a9b0fec87032`（交付侧归档于 `fixtures-v2/`）
- v1：`inputs.json` `a4b32e9c4c4b6e55fd018f6f06c7f4bb3289c50bb98ee669008a7591018f4d64`、`expected.json` `2e6039214d7ffa4fc0b622bdfdf8a1e0d4361987d105f42b9291e9ffa84915dc`（交付侧归档于 `fixtures-v1/`，旧技能对照所用）

| 文件 | sha256 |
|---|---|
| `inputs.json` | `40ae8a950ca8b07c5a824adde574dcdd3205b43926592da2908a2a92dd4d6161` |
| `expected.json` | `fbe1419273e250757267b8f0c84a262eef885629b78224b1150f3c09fae9ddce` |

本 README 自身的 hash 由冻结记录另行保存：写进本文会改变本文，自引用无效。v1、v2 期间的结果不得与 v3 输入混算；换到 v3 后 14 例须整体重跑。

## 与方案的关系

样例按方案「五 回归验收」的类别清单编写，覆盖六类应修正的正文问题、两类评审问题与六类应保留论述。本目录不含规则，也不含运行结果；规则改动、两轴评审、同步与激活都不在这里记录。
