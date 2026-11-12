# Argument review

The method behind step 3's separate argument check, and the whole of review mode. This file is its only home; `SKILL.md` points here and does not restate it.

## What it reviews

Format measurement watches rhetorical density. The fact snapshot watches whether values survived a rewrite. This review watches **propositions and inference**: which claim a sentence answers, who made that claim, and what the passage still does once its facts are stated on their own.

It runs in any language. The hanzi-based figures in `SKILL.md` step 1 belong to format mode: in review mode density, baseline and language scope are **not applicable**, and no per-1000 number accepts or rejects a document.

## Two shapes it catches

**The target nobody set.** The author answers a claim that no source and no user made: a question becomes someone else's error, and the error is then refuted. The refutation reads fluently, needs no evidence of an opponent, and leaves the reader holding a proposition the text itself invented.

**The invented misreading guard.** The author protects a claim from a mistake nobody raised in the source: a shared number becomes "some readers will think the two standards are one", and the paragraph argues with that reader instead of stating what the number covers. The guard adds a second claim to maintain, in place of the fact. It can also omit the reader entirely: "the matching number cannot establish the complete standard" still introduces an inference to deny. Locate that inference in the task or argument; a useful preceding explanation of the two numbers does not supply it. In contrast, a statement that a measurement covers only the tested configuration directly defines that measurement's scope. Keep that condition without attributing a mistaken belief.

A synthetic pair, toy objects only:

| draft | what the sentence carries |
|---|---|
| Some readers may assume link L-1 replaces link L-2; the board actually carries both, with independent drivers. | the fact: the board carries both links, with independent drivers |
| Both devices sample at 1.2 ms; that shared figure does not make TS-200 and TS-300 one standard. | the fact: each device's period, and which standard each one targets |

In both rows the tail is worth keeping and the head is not: no source asserted the replacement or the identical standard. Delete the frame, state the fact positively, and the paragraph loses nothing but its opponent.

## Write plainly first

State the object's capability, mechanism, conditions and evidence. When criticising a user's or a source's claim, quote the proposition as it was made and keep its strength: a local limitation stays local, `may` does not become `does`. An assumption the author raises is presented as an assumption — which real question it serves and how it will be checked — not as another party's mistake.

## Separate the frame from the facts

A rebuttal carries two things: the **frame** (someone is wrong) and the **facts** it drags in. Judge them apart. Facts that are true, sourced and relevant to the current question stay, as plain statements. A criticism of another party keeps its frame only when the actual claim can be located in a source, user statement or requirement. A question is not an assertion: answering a question does not license attributing the answer’s negation to its asker. Explicit hypotheses and proofs follow the exceptions below.

A factual example labelled a counterexample has two separate checks: whether the example is supported, and which proposition it refutes. Coexistence on one board is a useful observation; it does not make an invented claim that one link should do everything a real controversy. For summaries of counterevidence, name the actual hypothesis being tested at its original scope. Where that hypothesis was introduced solely to reject it, retain the observations and remove the rebuttal framing at every occurrence.

## The five questions

Read every passage that compares, negates, counters, concedes or guards against misreading, and ask:

1. Which part of the current question does this passage answer?
2. If it rebuts: where was that claim made? Has the original question, or a milder claim, been widened into the thing being refuted?
3. If the author raised the assumption: does it serve the current question, or was it set up to be knocked down?
4. With the facts stated on their own, what explanation does the frame still supply?
5. Rewritten as a positive statement, does a pointless opposition survive?

## Handling branches

| finding | disposition |
|---|---|
| a real condition | state the condition |
| a conceptual or metric difference | name the objects and their definitions |
| a sourced criticism | keep the source and the original proposition, at its original strength |
| a frame with no owner | delete under the edit authorization; keep the carrying facts as separate statements |
| an ambiguity the source really has | bound the value or term (which configuration, which version) instead of attributing a misreading to readers |
| review mode | report the finding; propose wording, do not edit |

## What is not a self-set target

The following forms are legitimate when their facts and scope hold. Check each sentence's role: a paragraph can contain a useful definition and an invented warning after it; the definition does not validate that warning. There is no blanket exemption for a passage labelled a qualification.

- a normal technical comparison of two designs, including migration cost
- a conceptual or metric difference explained from the definitions
- a known defect or limitation a source states
- a derivation, or a counterexample the author explicitly frames as an assumption — including a mathematical counterexample that refutes a general claim by constructing one case
- a qualification tied to a named model, configuration, version or test condition
- hypothesis analysis the user explicitly asked for

For criticism, locate the actual claim; for explanation or proof, identify its task-relevant role. Check whether each qualification names something real — not whether the sentence contains 不能 / 也 / 而非 / 不是. Those words carry content inside a valid comparison; deleting them to reach a "positive" style deletes the finding.

## Relevance of qualifications

A sourced qualification still needs a role in the current answer. An internal evidence ledger may list many things an observation does not establish. In prose, state the observation's scope and carry forward the gaps that change the present interpretation, decision or use. Leave unrelated possibilities in the ledger. Copying that list into a sequence of reader warnings is an argument-relevance defect even if each warning is true and there is a source for the list; a house-style baseline is not needed to identify it.

Check the proposed revision as well as the verdict: condensing an irrelevant list into one sentence retains the same defect. In review mode, identify the defect and propose the scoped wording without editing the file. Read-only authorization does not require reclassifying a substantive defect as optional style.

## Coverage

Read the requested range whole; do not sample. Record it per section: complete or not, findings located. Review the propositions in concluding summaries independently: a summary can revive a frame already removed from a case study. When a defect repeats, list the repeated positions and their disposition; mentioning a summary as a recurrence is not a decision about its wording. Captions and readable in-figure text count as text; an unreadable image or truncated source stays listed as uncovered. The record proves which range was read, never that the reading was right.

Only suspicious passages get a row — original position, discussion object and context, problem, handling, re-check verdict. A table for every normal sentence is noise.

## Closing a finding

A keep reason names the branch above, the source or context it rests on, and the explanatory work that survives. "It is a rigorous qualification" and "each section's evidence boundary is itself content" are the generic phrases that let this class of defect through before: they name no source, no object and no work. They do not close a finding.

Completion requires reading the requested range and resolving reported findings and known issues from the task. Unreadable material remains uncovered. A clear document review reports no remaining findings in that review; it does not claim the regression fixtures were run. Fixture runs are separately recorded evidence about the method, not a guarantee of future correctness.

## Before and after

- Quote the original sentence and its position. A finding without a re-readable original is not a confirmed finding.
- Fix both objects: a file gets path, content hash and line or paragraph; git material gets commit and path.
- Claiming a rewrite dropped a fact requires the pre-edit sentence and the gap in the current text. Without both, mark it unverified; an unlocatable claim is not confirmed fact loss.
- A sentence the reviewer proposes passes the same five questions as the author's.

## Report

Four parts, separately: **format**, **argument**, **fidelity**, **human read** — with not-run reported as not-run. The argument part carries the covered range, each finding with position and disposition, and the keep reason for each. A density figure inside the band is one line of that report; it cannot offset an argument finding, and "the text is only a draft" is not a disposition.
