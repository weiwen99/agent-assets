---
name: de-ai-flavor
description: Strip AI-flavored writing from a document by measuring it against its own repo's house style, and review its arguments for claims nobody made. Use when prose reads machine-generated, when the user says 去 AI 味 / 去口语化 / 文风不对 / 读起来像 AI 写的 / 太重的 AI 味, when bold, em-dashes, blockquotes or tables are overused, when a doc must be rewritten without losing any fact, or when a review must report 论证套话 / 自设靶子 / 无依据防误解提醒 (straw-man claims, invented misreadings, unsourced caveats) in text that may not be edited at all.
---

Measure rhetorical density against the document’s own hand-written baseline, read its arguments in context, and preserve its facts. These are separate checks: repeated devices can be counted; whether a passage invents the claim it answers requires reading.

Two consequences shape everything below:

- A rhetorical device in the hand-written baseline may be house style. Use the baseline for its density, while reviewing each argument on its merits.
- Facts die silently in rewrites. Density and style are measurable; a dropped phone number is not. Protect facts first.

## Two modes

The same document is treated differently depending on what you may do to it:

- **Document mode / Rewrite mode** — run all six steps for document-quality work. Rewrite only within the user’s authorization. For an unchanged publication or audit, measure and review the original, report findings, and leave it untouched; before/after are identical.
- **Review mode** — read the whole requested range using [the shared method](references/argument-review.md), then report. Skip format steps 1–2 and 5, the four-head format table and verification items 1–2; they are **not applicable**. If before/after are supplied, use step 4 to inspect fidelity without editing. Any edit needs separate authorization.

Both modes end in four separately reported verdicts — **format, argument, fidelity, human read**. A clean format number never closes an argument finding, and no snapshot makes an unsourced claim sourced.

## 1. Measure before touching anything

Run this against the target file. Numbers, not impressions.

```python
import pathlib, re, sys
t = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
L = t.splitlines()
cjk = len(re.findall(r'[\u4e00-\u9fff]', t))
bold = re.findall(r'\*\*[^*]+\*\*', t)
rows = [l for l in L if l.strip().startswith('|')]
cells = [len(re.findall(r'[\u4e00-\u9fff]', c)) for l in rows for c in l.split('|')[1:-1] if c.strip()]
sents = [s for s in re.split(r'[。！？\n]', t) if len(re.findall(r'[\u4e00-\u9fff]', s)) >= 6]
lens = sorted(len(re.findall(r'[\u4e00-\u9fff]', s)) for s in sents)
def per(n):
    return f"{n/cjk*1000:.1f}/千字" if cjk else f"{n} 处（零汉字，密度不适用）"
print(f"汉字 {cjk}" + ("" if cjk else "   语言口径：不适用（零汉字，密度不适用）"))
print(f"加粗 {len(bold)} = {per(len(bold))}   去重 {len(set(bold))}")
print(f"破折号 {t.count('——')} = {per(t.count('——'))}")
print(f"表格行 {len(rows)}   引用块 {len([l for l in L if l.strip().startswith('>')])}")
print(f"最长单元格 {max(cells) if cells else 0} 字；>=80 字的 {len([x for x in cells if x>=80])} 个")
print(f"句长中位 {lens[len(lens)//2] if lens else 0}")
print(f"问句标题 {len([l for l in L if re.match(r'^#', l) and re.search(r'什么|怎么|如何|谁', l)])}")
```

**Language scope**: the per-1000 figures divide by hanzi count, so they describe Chinese prose. Zero hanzi — English, mostly code, a table of numbers — means counts only: the script prints `零汉字，密度不适用` instead of dividing by zero, and no per-1000 figure is acceptance for that document. Report `语言口径不适用` and, where a baseline exists, compare the raw counts.

**Completion criterion**: every number above printed, and the four figures that matter noted — bold/千字, dash/千字, longest table cell, question-form headings. For a zero-hanzi document: the counts plus the explicit language-scope note.

## 2. Take the baseline from the repo, not from taste

Measure **2–4 hand-maintained documents in the same repo** — the ones with the most commits, or the ones a human obviously keeps editing. Prefer a long-lived `AGENTS.md`, a runbook, a migration plan. Run the same script on each.

A real measurement, made with the script above (whole-file figures — do not mix in "excluding tables" counts, or the band will not match the script):

| | target | `AGENTS.md` | `segment-migration-strategy.md` | `architecture-and-tables.md` |
|---|---|---|---|---|
| 加粗/千字 | 33.4 | 21.2 | 7.9 | 6.6 |
| 破折号/千字 | 9.6 | 1.8 | 0.6 | 0.7 |

Target sat at 12.1 afterwards — inside the band, and the band's width (6.6–21.2) is the honest answer to "what does this repo look like": it is wide, so aim inside it rather than at a point.

**Set the target between the baselines**, and say so in the report: the goal is "this document belongs to this repo", not "this document matches my taste". A document pulled *below* the baselines is a new outlier in the other direction — check the per-section numbers before declaring done, because a narrative section legitimately carries fewer labels than an enumerable one. **The band is a whole-document figure, never a per-section quota.**

Then grep the baselines for each pattern the target overuses. Same device, same words? It is **house style** — keep the instances that echo it, drop the rest. A document whose dash count is 16× the baseline is still house-compatible at the baseline's count.

## 3. Classify what you found into four heads

| head | symptom | fix |
|---|---|---|
| **Format overload** | bold on ordinary mid-sentence nouns; prose stuffed into table cells; blockquotes as per-section disclaimers | bold only on enumerable labels or first-use terms; extract cells ≥ 80 chars into paragraphs; delete disclaimer blocks |
| **Syntax habit** | em-dash appended as afterthought (`说完了——再补一句`); `A 是 X，B 是 Y` antithesis | colon or full stop for the afterthought; state the claim directly |
| **Meta-discourse** | the author talking about their own writing or data: `一句话`, `这里不编原因`, `以数据为准`, `别照抄`, `真正的壁垒`, `最能说明问题的是` | delete. Keep the substance if it carries fact, restated as plain assertion |
| **Structural template** | every case/section sharing one labelled shape; per-section boundary blocks; question-form headings and table headers | let content do the sectioning; headings and headers become noun phrases |

The four heads cover rhetoric. **Propositions and inference are reviewed separately**: whether each claim an opposing sentence answers was ever made, and whether the passage still does work once its facts are stated on their own. The method lives in [`references/argument-review.md`](references/argument-review.md) — five questions per comparing, negating or qualifying passage, coverage of the whole requested range, a named keep reason for every closed finding. Load that file and work from it; the method has no second copy.

**Completion criterion**: each format finding has a target location and a matching—or absent—baseline instance when format checks apply. In both modes the argument review returns coverage for every section of the requested range and a location for each finding; uncovered material remains explicit.

## 4. Build the fact inventory, then rewrite

**Before any rewrite**, preserve the original and extract the following fact inventory. Use its diff to locate possible omissions, then check their meaning.

```python
import json, pathlib, re
t = pathlib.Path(SRC).read_text(encoding='utf-8')
json.dump({
  "links": sorted(set(re.findall(r'\]\(([^)]+)\)', t))),
  "images": sorted(set(re.findall(r'!\[[^\]]*\]\(([^)]+)\)', t))),
  "inline_code": sorted(set(re.findall(r'`([^`]+)`', t))),
  "numbers": sorted(set(re.findall(r'\d[\d,.]*', t))),
  "section_refs": sorted(set(re.findall(r'§[0-9][0-9.]*', t))),
  "headings": [l for l in t.splitlines() if l.startswith('#')],
  "separators": len([l for l in t.splitlines() if l.strip() == '---']),
}, open(SNAP, 'w'), ensure_ascii=False, indent=1)
```

Then, after every edit — including the small ones, which is where things actually disappear — re-run the same extraction and diff against the snapshot. **Three failure modes it catches that no amount of reading will:**

- inline code spans inside a table row you replaced wholesale
- a `§x.y` cross-reference whose target section you just deleted
- a separator line swallowed by a slice whose end index sat on the next heading

Every miss must be either restored or explained in one sentence. "It was inside the section we deleted" is an explanation; silence is not.

**The snapshot proves a set, not a meaning.** It holds unique links, code spans, numbers and headings: it can show that a value vanished, never that the number still belongs to the same object. So for every sentence you changed and every conclusion you touched, check five things against the source: what the number is attached to, its value with its unit, the version or configuration that bounds it, who it came from, and the strength of the claim (`可以` → `必须`, one configuration → all). Unchanged sentences need no table.

**Completion criterion**: diff reports zero misses, or every miss has a written reason; and every changed sentence or touched conclusion has the five-item check recorded.

## 5. Then de-colloquialize, in this order

Headings first — this is where spoken-outline habits hide, and they are the most visible.

- **A heading is a noun phrase, not a sentence or a question.** `我们做了什么` → `方案与实现`; `你怎么参与` → `参与方式`; `这件事真正的意义` → `闭环的意义`. Test each: does it end like a clause? Rewrite it.
- **Same rule for table headers.** `解决什么` → `解决的问题`; `怎么触发` → `触发方式`; `面向谁` → `适用对象`. Headers are labels, not questions.
- **Same rule for bold list labels.** `**什么时候才需要本地克隆**` → `**需要本地克隆的情形**`.
- **Second person goes.** `你不需要克隆仓库` → `不需要克隆仓库`. A document states; it does not address the reader.
- **Filler adverbs go**: 其实 / 顺手 / 恰好 / 一路 / 过一会儿. But check each — `差额恰好是 176` is precision, not filler.
- **Keep engineering idiom.** `撞了三条 404` / `跑通` / `卡住` / `翻代码` are the register of the repo; `返回 404` / `调用成功` is a different, worse one. Rewriting these is over-reach, not polish.

## 6. Verify

Five checks, in increasing cost:

1. **Density** — re-run the format measurement from step 1. Every figure inside the baseline band, or counts against the baseline's counts for zero-hanzi text.
2. **Pattern checklist** — re-run the four-head pattern search from step 3's table. Count each head: overused bold mid-sentence, whole-sentence bold, `不是…而是` antithesis, meta-discourse phrases, question-form headings/headers, cells ≥ 80 chars. Each should be at or near zero, with the surviving instances explainable ("these three are enumerable labels").
3. **Argument** — apply [the shared method](references/argument-review.md) to the final text, or the unchanged text in review mode. Report its completion conditions independently of format.
4. **Fidelity** — diff the snapshot, then the five-item check on changed sentences and touched conclusions from step 4.
5. **Human read** — where available, hand the before and after to a person for an independent judgement. State explicitly whether this happened; agent review and numeric checks do not constitute human acceptance.

## Deletion is not a style problem

Two rules learned the hard way:

- **Only you can decide what to delete.** When a section feels weak, propose deletion — do not silently drop it. But once the user says delete, **the real work is the references it strands**: `§3.3` pointers, cross-links, "see the table above". After deleting a section, grep the whole file for its number and its title, and re-point or remove each hit. Nothing warns you.
- **Never assert a baseline you did not take.** A "before" snapshot taken mid-rewrite is not a before — if two sections were already rewritten by hand, comparing them across that snapshot shows no difference and misleads whoever reads it. Date-stamp the baseline and say which parts it covers.

## Reporting

- Lead with the numbers table: target vs baseline vs before vs after — or state that format measurement was **not applicable** (review mode, zero-hanzi text).
- **Report four verdicts separately: format, argument, fidelity, human read.** Say which ran and which did not; a not-run is reported as not-run. A density inside the band is one line of the report, never the conclusion.
- List every fact-diff miss with its reason, or state there were none, and name the changed sentences checked for object, unit, version/condition, source and strength.
- For the argument review: give the covered range, each finding with its position and disposition, and what closed it. Coverage proves which range you read, not that the judgement was right.
- When you changed your mind mid-task (wrong target, wrong threshold, a claim that did not survive a check), say so in the report. A finding that reverses an earlier claim is worth more than a clean narrative.
