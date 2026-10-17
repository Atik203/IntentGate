# Paper Final-Pass TODO — ICEEICT 2027

Working checklist for taking `IEEE-conference.tex` to submission quality.
Official rules (checked on iceeict.mist.ac.bd): **≤6 pages including figures, tables, and references · A4 · PDF ≤3 MB · all fonts embedded, no Type 3 · double-blind · similarity <30%.**

**Voice rule (fixed):** no first-person pronouns anywhere. Write `this study`, `this paper`, `the proposed method`, `the system`, or `the gate` as the subject instead of `we`/`our`/`us`.

Companions: guides `docs/prompt.md` + `docs/writing-guideline.md`; refs `IEEE-conference/references.bib` (copy of `docs/references.bib`).

## A. References (target 29–31, each verified)

- [ ] Fetch missing author lists via arXiv API: ClawGuard `2604.11790`, Task Shield `2412.16682`, ToolGate `2601.04688`, Progent `2504.11703`, MCP Safety Audit `2504.03767`
- [ ] Fix `docs/references.bib` placeholders: MCPTox authors (Z. Wang, Y. Gao, Y. Wang, S. Liu, H. Sun, H. Cheng, G. Shi, H. Du, X.-Y. Li); adaptive attacks author → "Henil Shalin Panchal" + exact ACL Anthology page; MELON → ICML 2025; Progent title → "Progent: Securing AI Agents with Privilege Control"
- [ ] Re-read ClawGuard (2604.11790): correct the related-work claim if the draft misstates what it does (no misrepresentation of concurrent work)
- [ ] Add ~16 verified entries: Greshake'23 · Perez & Ribeiro'22 · Zou'23 (GCG) · Spotlighting · Instruction Hierarchy · BIPIA (KDD'25) · SecAlign (CCS'25) · NeMo Guardrails · PFI (Kim et al., `2503.15547`) · ReAct · Sentence-BERT · ToolEmu · Design Patterns (`2506.08837`) · MCP Safety Audit · OWASP LLM Top 10 · MCP spec (Anthropic)
- [ ] Optional adds: Dietterich'98 (McNemar) · Trustworthy-LLM-Agents survey (`2503.09648`)
- [ ] Re-copy `docs/references.bib` → `IEEE-conference/references.bib`; cited ↔ listed consistency check

## B. Figures & tables

- [ ] Fig. 1: redraw architecture as vector (TikZ preferred; 600-dpi raster fallback); fix "veto forces `S = 0`" so it matches block semantics
- [ ] Fig. 2 (optional — drop first if page-tight): τ-sweep / Pareto curve from frozen `results/` data
- [ ] Tables: booktabs style — no vertical rules, no `resizebox`, `\small`/`\footnotesize`, caption above, "Ours" bold, units in headers
- [ ] Table set: (I) related-work comparison · (II) headline results · (III) ablations · (IV) utility/robustness (merge into text if tight)

## C. Sections (rewrite in order; compile after each)

- [ ] Abstract — six questions serial (area → gap → objective → approach → justification → outcome), ~170 words, ≤3 headline numbers
- [ ] I. Introduction — three paragraphs: context+gap+scope · merged lit review · gap+resolution+outcomes; cite at the claim
- [ ] II. Background & Related Work — add attack origins, model-level defenses, guardrails, contract/policy systems (ToolGate / Progent / ClawGuard / Task Shield / PFI); honest positioning
- [ ] III. Method — equations (contract, `S_sem`, `S`, veto, decision) + **Algorithm 1**; merge the two duplicate threshold paragraphs
- [ ] IV. Baseline: ToolGate — keep; add one Hoare `{P}T{Q}` sentence
- [ ] V. Evaluation — tighten; reproducibility sentence (gpt-4o-mini, all-MiniLM-L6-v2, seed 42, pinned commits)
- [ ] VI. Results — final E23/E24 numbers; remove `[TBD]` cells; E25/E26 → preliminary or limitations; fix "Section VI-E" → `\ref`
- [ ] VII. Discussion & Limitations — before Conclusion
- [ ] VIII. Conclusion — objective → contribution → findings → significance → future work (no new refs)
- [ ] Acknowledgment — LLM-usage disclosure; read ICEEICT "Use of a Large Language Model" policy first; keep anonymous-safe
- [ ] Pronoun sweep: `Select-String '\b(we|our|us)\b' IEEE-conference/IEEE-conference.tex` → zero hits

## D. QA gates (submission day)

- [ ] ≤6 pages including references; PDF ≤3 MB; A4; fonts embedded; 0 Type 3
- [ ] Double-blind scan: no names, emails, affiliations, self-identifying URLs
- [ ] `docs/prompt.md` §11 pre-delivery checklist pass (banned words, sentence starts, rhythm, lists, endings, counts)
- [ ] Notation audit: α, τ, δ, `S_sem`, `S_rule` defined at first use, consistent
- [ ] Original prose only (no pasted dataset/model definitions) — IEEE similarity <30% policy

## E. Bookkeeping

- [ ] Update `roadmap.md` checkboxes + `CHANGELOG.md` in the same commit that completes each step
- [ ] Author block: submission stays Anonymous; real block in gitignored `IEEE-conference/authors.local.tex` (Atik's info stored; 4 members + supervisor pending)
- [ ] Decide whether the built `IEEE-conference.pdf` stays tracked
- [ ] Push / PR to dev only when the team says go
