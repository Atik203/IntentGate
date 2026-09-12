# 📄 Paper #7 — IGAC (Intent-Governed Access Control)

![Paper](https://img.shields.io/badge/Paper-%237-1f6feb?style=for-the-badge)
![Role](https://img.shields.io/badge/Role-Closest%20(System)%2FSupporting-ffa726?style=for-the-badge)
![Threat](https://img.shields.io/badge/Threat%20to%20Novelty-Medium-High-f9966b?style=for-the-badge)
![Venue](https://img.shields.io/badge/Venue-SSRN%207195899%20(preprint)-6e40c9?style=for-the-badge)
![Verified](https://img.shields.io/badge/Verified-2026--09--12-8957e5?style=for-the-badge)

> *Verified via full paper text (SSRN preprint 7195899, Zhu & Wang — Accentrust / Georgia Tech / UIUC). Local copy: `pdfs/ssrn-7195899.pdf`.*

Paper Title:
Intent-Governed Tool Authorization for AI Agents

Authors & Year:
Zhu & Wang — 2026 (SSRN 7195899, preprint)

Link:
SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7195899

Summary:
IGAC is a **server-side authorization layer** for tool-using agents. It converts a trusted user request into a short-lived **intent certificate**, computes a monotone session policy, **narrows the statically authorized tool manifest**, and runs a **consistency gate** that checks each proposed tool call and payload effect against the certificate before execution. Certificate-inconsistent proposals are denied or routed to clarification; certificate-consistent but high-risk proposals enter draft/preflight/confirmation routing; low-confidence certificates never fall back to broad static scopes. It has a formal model (intent certificates, monotone session policy, intent-aware manifests, consistency predicates, least-privilege effect minimization) with a provable *static-policy non-expansion* guarantee (IGAC can add no authority beyond static OAuth/OpenPort scopes; a low-confidence certificate can only narrow). Evaluated as a reusable gateway over an **OpenPort** governance substrate: endpoint tests, 176 runtime-backed synthetic tasks, real-model classifier and planner pilots, 306 end-to-end model-task runtime trials, and a 36-trial benchmark-shaped external subset. Deterministic reference-certificate run reduces a composite exposure-or-path indicator 1.0000 → 0; in the real-model E2E runs the combined IGAC–OpenPort path records **0/198 completed unsafe executions**, but **unsafe *accepted authority* remains 0.0909–0.2727 and every residual is a non-executed draft**; strict benign completion is 0/108 (36/108 produce governed artifacts). Certificate precision is named as the principal remaining bottleneck.

Relevant to Our Idea:
IGAC is the second "intent-consistent tool-call authorization" system in the literature and is cited as an industry/access-control variant. It removes the Gap Map claim that the idea is entirely unoccupied and must appear in related work — but it is a *weaker threat* than TraceGrant: (1) it is **not adversarially benchmarked** on real injection/poisoning sets — its external evidence is a 36-trial "benchmark-shaped" subset and residual unsafe accepted authority remains in every real-model run (as drafts, not executed effects); (2) it is a **server-side, credential-centric** layer bound to OpenPort manifests (bulk export narrowed by scope), whereas ours is a **model-agnostic middleware at the agent's executor** checking per-call intent consistency with embeddings + hard rules; (3) its certificate generator needs rules/a model-assisted classifier/a deployment-specific hybrid (nonzero setup), and decisions are deny/clarify/review routing (confidence threshold) rather than a graded semantic score with a human-escalation band at the action chokepoint. Our differentiators hold cleanly: two separate adversarial benchmark studies (injection on InjecAgent, tool poisoning on MCPTox), each reported independently, graded scorer + escalate, zero per-tool/zero-server setup, stateless middleware.

Gap / Limitation Noted in Paper:
Self-admitted: "exact certificate bounds and adapter/effect contracts remain the principal systems problem"; residual unsafe accepted authority clusters in bounded-create/effect-bound categories and is only prevented from *executing* by draft routing (not by the intent check itself); 0/108 strict benign completion in the constrained real-model path. From our perspective: no InjecAgent/MCPTox evaluation; 36-trial external set far too small to be security evidence; certificate fidelity (an LLM-generated interpretation of intent) itself is the open bottleneck — the same vulnerability surface our parser faces, but theirs is server-side and per-request; no per-tool setup-cost metric (classifier/rules per deployment are hidden cost); SSRN preprint, not peer-reviewed.

---

## Section 2 — Expert Detailed Analysis

### Q1–Q9 Quick Reference

| # | Question | Short Answer |
|---|---|---|
| Q1 | What problem and why important? | Agent credentials are statically broad while a given user request is narrow; credential-only authorization (RBAC/OAuth scopes/MCP authorization) cannot tell whether a proposed call is justified by what the user asked. Same failure the benchmarks (AgentDojo/IPI/tool poisoning) demonstrate: the model's tool selection is insufficient evidence of authorization. |
| Q2 | What data (source, size, splits, ethics)? | No public benchmark; own evaluation stack: endpoint tests; 176 runtime-backed synthetic tasks; real-model classifier and planner pilots; 306 end-to-end model-task trials; 36 benchmark-shaped external trials (12-task transfer subset also reported). No human data. |
| Q3 | What features/inputs, how engineered? | Trusted request → intent certificate (classes, resource/effect bounds, expiry, request hash; no raw secrets). Monotone session policy; intent-aware manifest `Filtered = C∩VisibleOpenPort`; consistency predicate over (certificate, tool, payload, effect); routing per certificate confidence γ. |
| Q4 | What methods/models, overall pipeline? | Server-side gateway: POST /intent issues certificate → /manifest filters OpenPort manifest → /actions checks intent-tool-payload consistency → high-risk routes to review/draft/preflight/confirmation → audit with certificate IDs/hashes. Formal model with two guarantees: IGAC never expands static authority (non-expansion theorem); accepted calls imply certificate consistency (field-wise refinement). |
| Q5 | What baselines and why chosen? | Static (credential-only OpenPort) vs. Filtered (manifest) vs. Filtered+Gate (IGAC); trace-backed normalizer counterfactual at utility cost. Isolates manifest narrowing vs. per-call gate effect. |
| Q6 | How evaluated (metrics, setup, tests)? | Endpoint tests (narrowing, reason-code denials, payload-bound failure, review routing, audit, cross-key isolation); deterministic runtime conformance; scored E2E runtime; external benchmark-shaped subset; utility vs. residual accepted authority tradeoff; P95 latency. |
| Q7 | Key results vs baselines? | Deterministic reference: exposure-or-path 1.0000 → 0. Real-model: 0/198 completed unsafe executions vs. static 0.5–0.9 unsafe exposure; but 40/198 intent-inconsistent *drafts* accepted (residual unsafe authority 0.0909–0.2727); 0/108 strict benign completion; 12-task subset 0/24 unsafe completed, 5/24 unsafe accepted drafts. Non-expansion holds. |
| Q8 | Limitations and biases? | Certificate precision is the principal bottleneck; residual authority exists as drafts every run; benign completion quaternary low (0/108 strict); synthetic/self-built eval dominates; no real adversarial benchmark (36 external trials = ASB-shaped only); server-side OpenPort-bound design. |
| Q9 | Code/data/artifacts available? | SSRN preprint; no public code/repo confirmed; OpenPort is external substrate. |

### 1. Publication Status & Citation

| Field | Value |
|---|---|
| **Venue** | SSRN preprint 7195899 — not peer-reviewed at verification |
| **Last verified** | 2026-09-12 — full PDF text |
| **Code** | None confirmed |

**BibTeX:**
```bibtex
@misc{zhu2026igac,
  title={Intent-Governed Tool Authorization for {AI} Agents},
  author={Zhu, Genliang and Wang, Chu},
  year={2026},
  howpublished={SSRN preprint 7195899},
  note={Server-side intent certificate + manifest narrowing + consistency gate over OpenPort; 306 E2E trials, 0/198 completed unsafe executions but residual unsafe accepted authority 0.09--0.27 as drafts; no InjecAgent/MCPTox},
  url={https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7195899}
}
```

### 2. Core Contribution & Method

Intent certificate binds a trusted request message to authorization-relevant bounds (classes, resources, effects, expiry, request hash). Session policy is monotone — each certificate can only narrow static authority. The consistency gate (tool + payload + expected effect vs. certificate + substrate risk controls) returns Accept / Deny / Clarify / Draft / Preflight / Confirmation. Certificate confidence γ only affects routing: low confidence → clarification/draft, never broad static scopes. Formal non-expansion proof; accepted calls refine certificate fields.

### 3. Key Results (Extracted)

| Condition | Unsafe exposure | Unsafe accepted authority | Unsafe *completed* effects |
|---|---|---|---|
| Static (credential-only) | 0.5000–0.9259 | — | — |
| Filtered (manifest only) | 0.4444–0.7037 | — | — |
| Filtered+Gate (IGAC) | — | 0.0909–0.2727 (drafts only) | **0/198** (0/24 subset) |

### 4. Paper's Self-Admitted Limitations

Certificate precision and exact effect bounds are the open systems problem; residual unsafe authority persists in every real-model run (only blocked from *execution* by draft routing); strict benign completion 0/108; bounded-create/effect-bound categories are where failures cluster.

### 5. Direct Comparison to Our Idea

| Dimension | IGAC | Our Idea |
|---|---|---|
| **Placement** | Server-side authorization gateway (OpenPort substrate), credential-centric | Model-agnostic middleware at the agent executor (per-call tool_call chokepoint) |
| **Policy source** | Intent certificate from trusted request, but generator = rules/model-classifier/hybrid (deployment-specific, nonzero setup); certificate fidelity is the named bottleneck | Auto intent contract from trusted request once per session; embedding + hard-rule scorer, zero per-tool authoring |
| **Decision model** | Confidence-routed deny/clarify/draft/review; no graded semantic similarity | Graded S = α·S_sem + (1−α)·S_rule, τ×δ threshold, allow/block/escalate-to-human |
| **Guarantee** | Static-policy non-expansion (no new authority) | Per-call intent consistency against frozen contract (fail-closed) |
| **Adversarial eval** | None on real benchmarks (36 ASB-shaped external trials; residual unsafe accepted authority every run) | InjecAgent (1,054) + MCPTox (1,348, incl. tool poisoning) with ASR/FPR/latency/setup-cost; optional AgentDojo |
| **Vector coverage** | Injection covers only in benchmark-shaped subset; no tool poisoning | Injection + registration-time tool poisoning (MCPTox 353 tools) |

### 6. Our Positioning Strategy

| Role | Detail |
|---|---|
| **In our paper** | Closest (System)/Supporting — Medium-High threat; the second "intent-based tool authorization" system |
| **How we cite** | As "a server-side, access-control-flavored intent-authorization layer (intent certificate → manifest narrowing → consistency gate) with a formal static-policy non-expansion guarantee, but no adversarial benchmark evaluation, residual unsafe accepted authority in every real-model run, deployment-specific certificate generators, and an OpenPort server binding — in contrast to our model-agnostic, stateless per-call middleware gate validated in separate studies on InjecAgent and on MCPTox" |
| **Relationship** | Reinforces the research direction; weaker novelty threat than TraceGrant because it does not publish adversarial ASR evidence and does not cover our benchmarks |

### 7. Code & Reproducibility

| Field | Detail |
|---|---|
| **Repo** | None confirmed |
| **Substrate** | OpenPort (external governance layer) |
| **Eval scale** | 176 synthetic + 306 E2E + 36 external benchmark-shaped trials |
| **Reimplementation effort** | High for evaluation purposes (server substrate, adapter effect contracts); we cite intrinsics, do not reimplement |

### 8. Cross-References

| Paper in this review | Relationship |
|---|---|
| **ToolGate (Liu et al., 2026)** | IGAC's manifest/effect bounds are the access-control analogue of ToolGate's contracts; both need per-tool/deployment authoring, and neither has adversarial benchmark evidence on our pair |
| **TraceGrant (Liao et al., 2026)** | Both are "request-derived intent authority" systems; TraceGrant is security-evaluated (AgentDojo/ASB), IGAC is not (synthetic + small external subset) — write the three-way table (TraceGrant / IGAC / Ours) in related work |
| **MCPTox (Wang et al., 2025)** | MCPTox's registration-time poisoning is outside IGAC's model (static OAuth scopes assumed trustworthy) — IGAC cannot cover the poisoning vector we evaluate in a separate MCPTox study |
| **OWASP/MCP-auth framing (cited in IGAC Intro)** | Shared motivation: per-request authorization of the tool's intended effect is missing from MCP/OAuth credentials |

### 9. Relevance to Thesis

★★★★★★★★☆ (High — must cite; medium-high novelty threat from "someone else works on intent-based tool authorization")

**Justification:** IGAC proves the *space* (request → intent authority → tool-call check) is being pursued independently, so the literature index can no longer claim it is empty. But its server-side, manifest-narrowing design, unmeasured setup (certificate generators), total absence of adversarial-benchmark evidence, and self-admitted residual unsafe authority leave our position intact — two separate graded-scorer + escalation, zero-setup middleware studies on InjecAgent (injection) and on MCPTox (poisoning). Cite alongside TraceGrant in the related-work "request-derived authorization" paragraph and in the Gap Map row our plan rewrites.