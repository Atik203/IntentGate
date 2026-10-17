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
- [x] Fig. 2: τ-sweep (ASR/FPR vs τ, knee at τ=0.75) from frozen `results/gated/pareto.json`, vector pgfplots
- [x] Tables: booktabs style, no vertical rules, no `resizebox`, captions above, "Ours" bold; stale A2 ablation numbers fixed (14.7% / 263 — the draft had B1's numbers)
- [x] Table set: (I) related-work (full-width `table*`) · (II) headline · (III) ablations · (IV) utility/robustness pilots

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
