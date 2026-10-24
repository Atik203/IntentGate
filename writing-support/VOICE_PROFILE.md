# VOICE_PROFILE.md — IntentGate paper

**Confidence: Low.** No verified author-written sample was supplied. The manuscript text was
language-polished by an LLM (per the acknowledgment), so it cannot be used to infer the author's
own voice. The features below come from the supervisor style guides (`docs/prompt.md`,
`docs/writing-guideline.md`) and the current manuscript register. Treat them as constraints, not
as a measured voice. Ask the author which files they wrote themselves before any rung C/D work.

## Samples

| File | Words | Status |
|---|---|---|
| — | — | none verified as author-written |

## Features (from guides and current manuscript)

- **Person:** no first person (`I`, `we`, `our`, `us`). Subjects: "this paper", "this study",
  "the gate", "the system", "the proposed method". Use these sparingly and vary them.
- **Tense:** past for experiments and observations ("attack success fell"), present for facts,
  definitions, and figure/table references ("Figure 2 shows").
- **Sentence rhythm:** short to medium, one idea per sentence. Avoid chains of three or more
  clauses. End sections on the last fact, without a summary sentence or hopeful ending.
- **Paragraph shape:** 2–7 sentences, mixed lengths. The current manuscript has several 8–10
  sentence paragraphs (intro P1, validation P); split or trim them.
- **Connectors:** plain (`because`, `so`, `but`, `then`, `after`, `while`). No "Furthermore",
  "Moreover", "Additionally", "Notably", "Crucially".
- **Hedging:** one hedge per claim at most (`suggests`, `is consistent with`). Empirical claims
  carry the metric, dataset, and magnitude when available.
- **Numbers:** exact values with units and denominators ("0.7% (13 of 2,108)"). No vague
  quantifiers ("several", "various", "numerous") when a number exists.
- **Punctuation:** no em dashes, no prose semicolons, no contractions, no `etc.` Straight quotes.
- **Spelling:** US English ("artifact", "behavior", "normalization").
- **Avoided words (supervisor list):** tapestry, testament, realm, cornerstone, beacon, pivotal,
  paramount, salient, multifaceted, delve, synergy, leverage, foster, underscore, showcase,
  navigate, landscape, paradigm, holistic, seamless, comprehensive, notably, crucial, intricate,
  interplay, meticulous, vibrant, valuable, enhance (except "enhanced" as a benchmark setting),
  highlight/emphasize as participial tails, "serves as / stands as / acts as / represents /
  features" as copula substitutes, "studies show / experts argue" without a citation.
- **Banned sentence starts:** When, If, While, Although, Despite, Whether, By [verb]ing.
- **No three-item lists twice in a row.** Use two or four items.

## Terms that must survive editing

IntentGate, intent contract, `S_sem`, `S_rule`, `S`, τ, δ, α, allow/block/escalate, ASR,
attack-influenced calls, valid rate, setup cost, `no_contract`, ToolGate, Progent, ClawGuard,
Task Shield, CaMeL, InjecAgent, MCPTox, gpt-4o-mini, qwen3.5:4b, all-MiniLM-L6-v2.

## Application rules

- Fix recurring slips (long sentences, repeated "this paper") without flattening the register.
- Preserve every number, citation key, equation symbol, and cross-reference.
- If a passage must change meaning to fix an overclaim, mark it for author confirmation.
