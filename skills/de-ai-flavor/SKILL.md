---
name: de-ai-flavor
description: Strip AI-flavored writing from a document by measuring it against its own repo's house style. Use when prose reads machine-generated, when the user says 去 AI 味 / 去口语化 / 文风不对 / 读起来像 AI 写的 / 太重的 AI 味, when bold, em-dashes, blockquotes or tables are overused, or when a doc must be rewritten without losing any fact.
---

AI flavor is not a set of banned words. It is **density**: every rhetorical device the author reached for, used several times more often than the surrounding hand-written documents do. So you never invent a target style — you measure the **baseline** from the repo you are editing and pull the document down to it.

Two consequences shape everything below:

- A device that already exists in a hand-written doc is **house style, not AI flavor**. Keep it; only the count is wrong.
- Facts die silently in rewrites. Density and style are measurable; a dropped phone number is not. Protect facts first.

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
print(f"汉字 {cjk}")
print(f"加粗 {len(bold)} = {len(bold)/cjk*1000:.1f}/千字   去重 {len(set(bold))}")
print(f"破折号 {t.count('——')} = {t.count('——')/cjk*1000:.1f}/千字")
print(f"表格行 {len(rows)}   引用块 {len([l for l in L if l.strip().startswith('>')])}")
print(f"最长单元格 {max(cells) if cells else 0} 字；>=80 字的 {len([x for x in cells if x>=80])} 个")
print(f"句长中位 {lens[len(lens)//2] if lens else 0}")
print(f"问句标题 {len([l for l in L if re.match(r'^#', l) and re.search(r'什么|怎么|如何|谁', l)])}")
```

**Completion criterion**: every number above printed, and the four figures that matter noted — bold/千字, dash/千字, longest table cell, question-form headings.

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

**Completion criterion**: each finding has a line number in the target and a matching—or absent—instance in a baseline.

## 4. Build the fact inventory, then rewrite

**Before any rewrite**, snapshot every fact in the file so the diff can prove nothing was lost.

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

**Completion criterion**: diff reports zero misses, or every miss has a written reason.

## 5. Then de-colloquialize, in this order

Headings first — this is where spoken-outline habits hide, and they are the most visible.

- **A heading is a noun phrase, not a sentence or a question.** `我们做了什么` → `方案与实现`; `你怎么参与` → `参与方式`; `这件事真正的意义` → `闭环的意义`. Test each: does it end like a clause? Rewrite it.
- **Same rule for table headers.** `解决什么` → `解决的问题`; `怎么触发` → `触发方式`; `面向谁` → `适用对象`. Headers are labels, not questions.
- **Same rule for bold list labels.** `**什么时候才需要本地克隆**` → `**需要本地克隆的情形**`.
- **Second person goes.** `你不需要克隆仓库` → `不需要克隆仓库`. A document states; it does not address the reader.
- **Filler adverbs go**: 其实 / 顺手 / 恰好 / 一路 / 过一会儿. But check each — `差额恰好是 176` is precision, not filler.
- **Keep engineering idiom.** `撞了三条 404` / `跑通` / `卡住` / `翻代码` are the register of the repo; `返回 404` / `调用成功` is a different, worse one. Rewriting these is over-reach, not polish.

## 6. Verify

Three checks, in increasing cost:

1. **Density** — re-run step 1. Every figure inside the baseline band.
2. **Pattern checklist** — re-run the step-3 grep. Count each head: overused bold mid-sentence, whole-sentence bold, `不是…而是` antithesis, meta-discourse phrases, question-form headings/headers, cells ≥ 80 chars. Each should be at or near zero, with the surviving instances explainable ("these three are enumerable labels").
3. **Human read** — hand the before and after to someone and ask which reads human. This is the only check that can falsify the other two, and the only one you cannot run yourself. **State explicitly which of the three you ran.**

## Deletion is not a style problem

Two rules learned the hard way:

- **Only you can decide what to delete.** When a section feels weak, propose deletion — do not silently drop it. But once the user says delete, **the real work is the references it strands**: `§3.3` pointers, cross-links, "see the table above". After deleting a section, grep the whole file for its number and its title, and re-point or remove each hit. Nothing warns you.
- **Never assert a baseline you did not take.** A "before" snapshot taken mid-rewrite is not a before — if two sections were already rewritten by hand, comparing them across that snapshot shows no difference and misleads whoever reads it. Date-stamp the baseline and say which parts it covers.

## Reporting

- Lead with the numbers table: target vs baseline vs before vs after.
- Say which checks you ran and which you did not.
- List every fact-diff miss with its reason, or state there were none.
- When you changed your mind mid-task (wrong target, wrong threshold, a claim that did not survive a check), say so in the report. A finding that reverses an earlier claim is worth more than a clean narrative.
