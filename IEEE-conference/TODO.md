# Paper Final-Pass TODO — ICEEICT 2027

Working checklist for taking `IEEE-conference.tex` to submission quality.
Official rules (checked on iceeict.mist.ac.bd): **≤6 pages including figures, tables, and references · A4 · PDF ≤3 MB · all fonts embedded, no Type 3 · double-blind · similarity <30%.**

**Voice rule (fixed):** no first-person pronouns anywhere. Write `this study`, `this paper`, `the proposed method`, `the system`, or `the gate` as the subject instead of `we`/`our`/`us`.

Companions: guides `docs/prompt.md` + `docs/writing-guideline.md`; refs `IEEE-conference/references.bib` (copy of `docs/references.bib`).

## A. References (30 entries, each verified — DONE)

- [x] Fetch missing author lists via arXiv API — done (ClawGuard: Zhao, Li, Zhang, Sun; Task Shield: Jia, Wu, Qin, Squicciarini; ToolGate: Liu et al. 8 authors; Progent verified; MCP Safety Audit: Radosevich, Halloran)
- [x] Fix `docs/references.bib` placeholders — done (MCPTox full authors + pages 35811–35819; adaptive attacks author "Panchal, Henil Shalin" + pages 7101–7117 + DOI; MELON → ICML 2025; Progent title → "Securing AI Agents with Privilege Control"; Task Shield → ACL 2025 long, DOI/pages)
- [x] Re-read ClawGuard — claim CONFIRMED: it evaluates on InjecAgent + MCPTox (among six benchmarks) and derives constraints from the stated objective; note the "user-confirmed rule set" nuance when rewriting §II
- [x] Add ~16 verified entries — done, 17 added (Greshake'23 · Perez & Ribeiro'22 · Zou'23 · Spotlighting · Instruction Hierarchy · BIPIA KDD'25 · SecAlign CCS'25 · NeMo · PFI · ReAct · Sentence-BERT · ToolEmu · Design Patterns · MCP Safety Audit · OWASP LLM Top 10 · MCP spec · Dietterich'98); survey skipped (target met)
- [x] Re-copy `docs/references.bib` → `IEEE-conference/references.bib` — done (bibtex scratch-validated: 30 entries; cited ↔ listed final check happens in D)


## B. Figures & tables (DONE)

- [x] Fig. 1: redrawn as vector (inline TikZ in `IEEE-conference.tex`; `fig1.png` removed); veto semantics fixed ("veto $\Rightarrow$ block (fail-closed)")
- [x] τ-sweep figure (ASR/FPR vs τ, knee at τ=0.75) from frozen `results/gated/pareto.json`, vector pgfplots
- [x] Tables: `\hline` cell-grid style (per request), no `resizebox`, captions above, "Ours" bold; stale A2 ablation numbers fixed (14.7% / 263 — the draft had B1's numbers)
- [x] Table set: (I) related-work (full-width `table*`) · (II) headline · (III) ablations · (IV) utility/robustness pilots
- [x] Polish (2026-10-18): Fig. 1 overlap fixes (ingress arrows moved to the box edges so the gate title is clear; return-path label spacing); new ASR bar chart with per-bar value labels (renders as Fig. 2; τ-sweep becomes Fig. 3); larger axis fonts; all figures vector (no dpi limit). Still 6 pages clean.
- [x] Expert review pass (2026-10-18, second round): Fig. 1 reworked — single agent→gate arrow (horizontal bus removed), gate title given ≥2.5 pt clearance from the border, all annotation labels repositioned (no overlaps at 400–600 dpi), annotation fonts raised to 8 pt; table column widths fixed — zero stray hyphenations left ('track-ing', 'InjecA-gent', 'de-fense' all gone, verified in the PDF text); `dh/ds` expanded in §V-A; §IV renamed "ToolGate Baseline (B2)"; abstract wording unified ("hand-authored"); BibTeX casing fix for [3] (NeurIPS).

## C. Sections (DONE; ICEEICT LLM-policy read pending in D)

- [x] Abstract — six questions serial, ~150 words; headline set only (19.0→0.7%, 20.7→10.7%, 16–20 ms, 145 vs. 0)
- [x] I. Introduction — three paragraphs: context+gap+scope · two-group lit review · gap+resolution+outcomes; cite at the claim
- [x] II. Background & Related Work — attack origins (Greshake, Perez, Zou), model-level + data-level defenses, boundary systems (ToolGate / Progent / ClawGuard / Task Shield / PFI), ASB/OWASP/MCP cites; ClawGuard "user confirmation" nuance added; no claim of first
- [x] III. Method — equations (contract tuple, `S_sem` cosine, `S`, decision) + **Algorithm 1**; duplicate threshold paragraphs merged into scorer
- [x] IV. Baseline: ToolGate — Hoare `{P}T{Q}` sentence added
- [x] V. Evaluation — reproducibility sentence (gpt-4o-mini, all-MiniLM-L6-v2 [cited], seed 42); McNemar [cited]; heuristic-evaluator note
- [x] VI. Results — "Section VI-E pending E23" removed; E24 numbers in; E25/E26 → "in progress" sentence; `\ref` fixes; A2 ablation corrected
- [x] VII. Limitations — before Conclusion; E23-pending text replaced; heuristic-evaluator caveat added
- [x] VIII. Conclusion — objective → contribution → findings → significance → future work; no new refs
- [~] Acknowledgment — LLM-usage disclosure kept; **still to read ICEEICT "Use of a Large Language Model" policy (step D)**
- [x] Pronoun sweep — zero hits for `we|our|us` (verified with the build)
- [x] Cited ↔ listed — all 30 bib entries cited; bibliography renders 30 (verified in build)

## D. QA gates (PASSED)

- [x] ≤6 pages (exactly 6) including references; 228 KB ≤ 3 MB; A4 confirmed in the compile log; **all fonts Type 1 embedded, 0 Type 3** (the fonts must be embedded — IEEE + ICEEICT rule, verified via the PDF font audit)
- [x] Double-blind scan clean: anonymous author block, no names/emails/affiliations/self-identifying URLs in tex or bib
- [x] `docs/prompt.md` §11 pass: 0 banned words, no `When/If/While/...` sentence starts, no trailing `-ing`, no `etc.`, counts clean (em-dashes only as table placeholders)
- [x] Notation audit: LLM/MCP/ASR expanded at first use; α/τ/δ/`S_sem`/`S_rule`/A/K/H/e_C/e_c defined at first use; "ReAct-style" terminology unified
- [x] Original prose only; ICEEICT "Use of an LLM" policy read — acknowledgment complies (declared, non-intellectual preparation use, author review). Turnitin check not possible locally — upload-side task

## E. Bookkeeping

- [x] `roadmap.md` + `CHANGELOG.md` updated with every step (A–D commits)
- [~] Author block: **lead author's real details (Md. Atikur Rahaman, UIU, email, ORCID) + placeholders for the three remaining members and the supervisor — total 5 authors (4 members + supervisor), laid out as a compact 3+2 two-row grid** (forced with `\and[\hfill\break]`); anonymous block kept commented in the tex; structured record in gitignored `IEEE-conference/authors.local.tex`. Camera-ready option once affiliations are known: collapse to the single-line shared-affiliation style if all authors are at UIU. **Before CMT: swap to the anonymous block (double-blind).**
- [x] Built `IEEE-conference.pdf` stays tracked and is refreshed with each step
- [ ] Push / PR to dev only when the team says go (atik pushed through the latest commit)
