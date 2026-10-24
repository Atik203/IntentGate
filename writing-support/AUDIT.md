# AUDIT.md — Mode 4 review of `IEEE-conference/IEEE-conference.tex`

Date: 2026-10-24. Basis: `writing-support/PROJECT_BRIEF.md` (claim-evidence map) and the paper
source. Confirmed errors are separated from judgment calls. No detector score is targeted.

## Critical — fix before submission

| # | Location | Issue | Why it matters | Action |
|---|---|---|---|---|
| C1 | §III-C Eq. (2) | Paper defines `S_sem = cos(...)`; code uses `(cos+1)/2` mapped to [0,1] (`scorer.py:30`) | Equation contradicts the implementation; τ=0.75 is only meaningful on the [0,1] scale | Change Eq. (2) to `(cos+1)/2` |
| C2 | §III-B Eq. (1) | Contract `C=(A,K,H)` is never mapped to the actual schema (`goals`, `expected_tool_categories`, `permitted_data_access`, `side_effect_limits`) | Artifact reviewers cannot reconcile paper and code; invites a reproducibility objection | Add one mapping sentence |
| C3 | Abstract, Conclusion | "requires zero setup" / "zero setup cost" | Contradicts §VI: the parser is an LLM call once per session. Overclaim | Reword to "no hand-authored per-tool contracts" |
| C4 | §II Defenses | "coverage is incomplete (65/801 MCPTox tools...)" reads as ToolGate's reported result | The 65/801 figure is this paper's reimplementation, not ToolGate's published coverage | Attribute to "this reimplementation" |
| C5 | Table I | Column "Benchmarks" with "Not reported" for CaMeL, StruQ, Task Shield, ToolGate | False as a general claim: CaMeL and Task Shield report AgentDojo, ToolGate reports ToolBench | Retitle column "InjecAgent/MCPTox" and use Yes/No |
| C6 | §VI Limitations | "Contract coverage for MCPTox tools outside the evaluated subset remains low by design" | Reads as IntentGate's own per-tool coverage; IntentGate has no per-tool contracts. Belongs to B2 | Qualify as the ToolGate baseline's limitation |
| C7 | §II Defenses | "ClawGuard ... reports results on six injection benchmarks" | Repo evidence confirms InjecAgent + MCPTox only; the count is unverified | Soften to the two verified benchmarks |

## Major — clarity or claim-strength fixes

| # | Location | Issue | Action |
|---|---|---|---|
| M1 | §I, §II, §III | "contract" names both the request-derived intent contract and ToolGate's per-tool contracts | Add one distinguishing clause at first use; keep "intent contract" for ours |
| M2 | §V-F | "0/13 cases newly crossing τ" while all 13 are already above τ reads as a contradiction | Reword: all 13 were already allowed; mimicry moved no additional case across τ |
| M3 | §IV, §V-C | Two different 583s (extended B2 contracts, escalated calls) appear three lines apart | Label "583 contracts" and "583 escalated calls" |
| M4 | §II Research gap | "head-to-head comparison ... on both benchmarks" overstates the MCPTox side (8.1% distinct coverage) | Scope to "the covered subset of a tool-poisoning benchmark" |
| M5 | §II Defenses | "report no head-to-head evaluation on InjecAgent or MCPTox" is absolute | Hedge with "to our knowledge" |
| M6 | §I P1/P3 | "This study tests..." and "This paper introduces..." duplicate; "more than thirty attack techniques" unverified | Merge sentences; drop the count |
| M7 | §V-F | "MCPTox failures cluster in ... classes no contract covers" is ambiguous (B2 vs IntentGate) and conflicts with the design | Reword: calls look like legitimate queries, so no request-level rule fires |
| M8 | §V-G | Validation paragraph runs 10+ sentences; DeepSeek refusal sentence is choppy | Split into two paragraphs; tighten DeepSeek |
| M9 | §III-C/D | Code sets `S=0` on veto; Eq. (3) implies α-fusion even when the veto fires | Add "a veto sets S=0 before thresholding" |
| M10 | Table I | Progent's "LLM/action" cell says "Policy updates", which does not answer the column | Change to "No (updates)" |

## Moderate — judgment calls, no forced change

| # | Location | Issue | Recommendation |
|---|---|---|---|
| D1 | §V-D | Post-hoc power = 1.0 invites reviewer criticism | Keep only if supervisor-required; otherwise report effect sizes/CIs |
| D2 | Whole paper | "This paper" appears 7 times | Vary 2–3 with "this study" / "the system" |
| D3 | §III-D | "24.5% target other tools" leaves "other" undefined | Add "tools outside the user's tool set" if space allows |
| D4 | Conclusion | "artifact is released after acceptance" vs the public repository | Confirm intended availability wording |
| D5 | §V-F | "inflates S by only +0.0112 on average" | Use "mean" and keep four decimals |

## Minor

| # | Location | Issue |
|---|---|---|
| N1 | §V-F | Missing spaces around ∈ (fixed by the M2 rewrite) |
| N2 | §III-C | "This paper reports the operating point" → "The study reports" |
| N3 | §V-A | "enhanced settings" is a benchmark term; keep it despite the banned-word list |
| N4 | Whole paper | 32 references, all cited; no missing keys; leave as is |

## Checks that passed

- No first-person pronouns, no em dashes, no prose semicolons, no banned sentence starts.
- Banned-word scan hits only "enhanced" (benchmark setting, allowed).
- All headline numbers match the frozen experiment reports (see brief §6–7).
- 6 pages, Type-1 fonts, ≤3 MB (last verified build 2026-10-20; re-verify after edits).

## Edit plan (Mode 1, rung B)

Order: equations (C1, M9) → schema mapping (C2) → claim attribution (C3–C7) → terminology and
scoping (M1, M4, M5) → wording and structure (M2, M3, M6–M8, M10) → minor (D2, N2). Every edit
preserves numbers, symbols, citation keys, and section order. Target: length-neutral; re-run the
two-PDF build and the six verification checks afterwards. No new claims, no new citations.

## Follow-up: abstract pass (Mode 1, 2026-10-24)

Five edits applied after the audit: split the 32-word opener; removed the "This paper presents"
frame; scoped the headline results to static attacks; named the qwen3.5:4b replication; replaced
the meta "two benchmarks cover..." sentence. Abstract is now 199 words across 12 sentences
(9--23 words), with no first person, em dash, semicolon, or banned word. Post-edit judgment:
clarity 9.0, specificity 9.5, claim accuracy 9.0, structure 9.0, voice 9.5, AI-pattern risk 8.5,
overall about 9.0/10. Detector scores remain unpredictable and were not targeted.

## Follow-up: post-merge compliance pass (Mode 4/1, 2026-10-24)

The Phase 8 merge (`5b1b701`) changed ten paper lines. Audit of that diff found one voice-rule
violation ("to our knowledge"), one pre-existing prose label ("Ours is IntentGate"), one
over-broad utility sentence ("preserves utility"), and a missing pilot size for the qwen3.5:4b
replication. Applied: "to our knowledge" replaced with "the reviewed literature reports no";
"Ours is IntentGate" replaced with "IntentGate uses"; "preserves utility" narrowed to
"preserves more of them" (call-level); and `n=100` per condition added to the qwen sentence.
Both PDFs rebuilt at 6 pages; all 23 checks pass.

Left open for the authors: (1) `docs/experiments/09_paper_code_audit.md` item 15 still quotes
"n=100 attack cases per condition, E18"; the paper now says "n=100 per condition" and does not
cite internal experiment IDs. (2) The affiliation line reads "Independent University Bangladesh";
confirm the official styling ("Independent University, Bangladesh") with the author. (3) Table
labels still use the conventional "Ours"; prose has no first-person pronoun.

## Follow-up: author abstract revision (Mode 1, 2026-10-24)

The author supplied a longer six-question draft. The revision keeps the author's order and
wording, deletes the meta/evaluation setup sentences, and restores supported context to reach
271 words. The draft's "100 requests" was replaced with the paper's main evaluation sizes
(2,108 InjecAgent cases, 1,348 MCPTox cases); "dynamic attacks" was replaced with tool
poisoning and the static-attack scope; ".70%" became "0.7%"; and "attack vectors" became ASR.
Both PDFs rebuild at 6 pages, 32 references, Type-1 fonts, with no first person, em dash, or
semicolon. The current abstract is 271 words and 15 sentences.

## Follow-up: author introduction revision (Mode 1, 2026-10-25)

The author supplied a roughly 650-word Introduction draft. The revision trims it to 355 words
in three paragraphs, following `docs/prompt.md` §10: P1 covers access, attacks, defenses, the
gate, and benchmark scope; P2 reviews six prior systems with one paper per sentence; P3 states
the open question and the measured results. The author's sentence order and wording are kept
where they are clear.

Two corrections: "Only one defense mechanism will derive the policy directly from the task"
became "a few derive the policy directly from the task" (Progent and ClawGuard both do), and
the ToolGate 145-contract result is scoped to MCPTox, where the paper reports indistinguishability
from the unprotected agent. The other edits are grammar, terminology ("attack success",
"attack-influenced tool calls"), and punctuation.

Result: 355 words, 3 paragraphs; both PDFs at 6 pages, 32 references, Type-1 fonts; no first
person, semicolon, or em dash. The general 2-7 sentence checklist conflicts with §10's
one-paper-per-sentence rule for six papers, so P2 follows the specific Introduction rule.

## Follow-up: Background and Related Work trim (Mode 1, 2026-10-25)

The author supplied an 804-word draft and preferred a shorter version. The applied text is 601
words for Threat Model/Defenses/benchmarks and 118 for Research gap (719 total; the table adds
92, so the section is 811). Kept the citation-bearing Prompt Flow Integrity, TrustAgent, and
emulated-environment sentences; removing them would leave three uncited references. Minor
fixes: "uses" instead of "utilizes", "execute an unauthorized tool call", split StruQ/SecAlign
for accuracy, "user's objective" in the gap, and "the ToolGate baseline". No padding; the text
stays within the 750 cap.
