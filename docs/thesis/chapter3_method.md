Chapter 3. Proposed Method

3.1 Working principle

IntentGate checks a proposed tool call against the user's original request.
The system parses this trusted request once, before loading tool definitions
or tool responses. The parser produces a frozen intent contract containing
goals, expected tool categories, permitted data access, and side-effect limits.
Tool responses can influence the agent's next proposed action. They cannot
change this contract during the evaluated session.

The gate is outside the agent prompt. Every executed call passes through
GateMiddleware.execute(), which checks the call before invoking its executor.
The benchmark treats an escalation as a prevented execution and records it
separately. Interactive approval is outside the reported benchmark protocol.

Anderson's reference-monitor model requires protected mediation on every access,
with a mechanism small enough for analysis and testing
([Anderson, 1972, Volume I, Section 3.2.2](https://csrc.nist.gov/files/pubs/conference/1998/10/08/proceedings-of-the-21st-nissc-1998/final/docs/early-cs-papers/ande72a.pdf)).
IntentGate adopts this placement for tool execution, but its ordering and
no-bypass tests establish implementation checks rather than a proof of
tamper resistance or correct intent interpretation.

3.2 Technical formulation

Let u be the trusted request, c = P(u) its frozen contract, and a a proposed
tool call containing a name and argument values. The encoder E maps the
serialized contract and naturalized call to vectors. The implementation uses
the following semantic score, including its conversion to the unit interval:

\[
S_{\mathrm{sem}}(c,a)
 = \operatorname{clip}_{[0,1]}
   \left(\frac{1+\cos(E(c),E(a))}{2}\right).
\]

The rule engine returns S_rule and records whether a critical constraint
triggered. A critical violation sets S to zero. Otherwise, the gate combines
the two components using the fixed weight alpha:

\[
S(c,a)=
\begin{cases}
0, & \text{critical rule violation},\\
\alpha S_{\mathrm{sem}}(c,a)+(1-\alpha)S_{\mathrm{rule}}(c,a),
 & \text{otherwise}.
\end{cases}
\]

The evaluated configuration uses alpha = 0.7, tau = 0.75, and delta = 0.1.
The score and both components appear in each trace record. The decision is:

\[
d(c,a)=
\begin{cases}
\mathrm{allow}, & S(c,a)\geq\tau,\\
\mathrm{escalate}, & \tau-\delta\leq S(c,a)<\tau,\\
\mathrm{block}, & S(c,a)<\tau-\delta.
\end{cases}
\]

Only allow reaches the executor in benchmark mode. The escalation interval is
one-sided and ends below tau. Changing delta alone changes the escalation
share, but it does not change the execution threshold in this mode.

3.3 Threshold selection and the utility constraint

Neyman and Pearson study tests that minimize one error while restricting the
other ([Neyman and Pearson, 1933](https://doi.org/10.1098/rsta.1933.0009)).
This study uses that error-budget framing for threshold selection.
The null case is a legitimate call. Preventing that call is a false positive,
including an escalation without execution in benchmark mode.
The attack error is allowing an unauthorized call, while benchmark ASR also
depends on the task evaluator and the agent's later actions.
The embedding score is not a likelihood ratio, so this framing does not claim
the optimality supplied by the Neyman-Pearson lemma.

For a fixed encoder, parser, fusion weight, and benchmark protocol, define
ASR_hat(tau) as the measured attacker success fraction. Define
B_hat(tau) as the fraction of independently labeled legitimate calls that
receive block or escalate. A target epsilon specifies the acceptable clean-call
blocking budget. The threshold-selection objective is:

\[
\widehat{\tau}\in
\operatorname*{arg\,min}_{\tau\in\mathcal{T}}
\widehat{\mathrm{ASR}}_{\mathrm{selection}}(\tau)
\quad\text{subject to}\quad
\widehat{B}_{\mathrm{selection}}(\tau)\leq\epsilon.
\]

The candidate set T and epsilon must be fixed before inspecting held-out test
results. No feasible threshold is also a reportable result. Selected thresholds
need evaluation on disjoint cases, with uncertainty for the clean-call rate.
An observed selection-set bound alone does not establish a population bound.

The existing [E9 Pareto table](../experiments/04_gate2_gated_eval.md) and
[cached Pareto artifact](../../results/gated/pareto.json) show the measured
tradeoff used to choose tau = 0.75. The [E13 analysis](../experiments/05_phase5_full_evaluation.md)
replays full-run traces at other thresholds. These are empirical operating-point
analyses. The original selection was not a prospectively validated
Neyman-Pearson calibration procedure, and the frozen Phase 5 results remain
unchanged. Replaying a fixed trajectory also cannot predict every later action
that a new live threshold would produce.

The [E23 benign suite](../experiments/07_phase7_pilots.md) supplies a direct
clean-call blocking measurement. Its user-tool-allowed rate is a utility proxy.
Neither valid ReAct output nor an allowed user-tool call alone proves that the
whole benign task succeeded. A transfer study must report its selection and
test slices separately, including changes in encoder or attack delivery.

3.4 Algorithm and assumptions

The system first parses u and validates the resulting contract. Missing
high-risk permissions use fail-closed defaults. The contract embedding is
cached at first gate use and reused for later calls in the session.
Each proposed call then passes through the rule engine and the semantic
scorer. The middleware logs the result and invokes the executor only for an
allowed decision under the benchmark protocol. Tool observations return to
the agent without returning to the intent parser.

The following table states the limits of this procedure. A failure example
is evidence for the listed boundary only within the evaluated cases.

| Assumption | Failure after violation | Evidence and scope |
|---|---|---|
| The initial request is trusted and reaches the parser before attacker content. | A contaminated request can produce an attacker-authorized contract. Later scoring cannot repair the trust decision. | Ordering tests check the implemented boundary. E16 does not test malicious original requests. |
| Tool definitions and responses are untrusted, but the executor implements the stated operation. | A poisoned operation can look consistent with the user's request. Similarity cannot establish tool provenance or hidden runtime behavior. | E16 records allowed read-like residuals near tau and registration-poisoning failures. E26 must be interpreted using its recorded delivery and execution setting. |
| One trusted request defines a session. | A later legitimate change can be blocked by the frozen contract. A harmful sequence can also contain individually plausible calls. | Multi-turn drift is explicitly deferred in the Phase 7 roadmap. E16 and E26 do not establish safety under changing user intent. |
| The backbone produces calls in the shared ReAct format. | A model that emits only prose supplies no executable call for gate evaluation. Low measured ASR can then reflect output incompatibility. | E18 includes Qwen participation and excludes Luna from the supported comparison because of invalid or prose-only output. |

The E26 adaptive pilot can test delivery changes or threshold-aware candidate
search under its stated budget. Its evidence does not cover every adaptive
attacker. In particular, a fixed set of paraphrases is a bounded stress test,
and a gate-query search is an adaptive call-level test only when candidates
depend on earlier returned scores. The final report must distinguish these
settings from live end-to-end attacker success.

3.5 Contribution and evidence boundary

The proposed method combines a request-derived contract with CPU embedding
scores and deterministic constraints at the execution boundary. It removes
manual per-tool contract authoring from this implementation. Parsing still
requires a model call or a documented fallback, and its cost belongs in the
setup measurement. The method does not prove that every allowed action is safe.

The semantic-only ablation also embeds the structured contract. Its comparison
with the full gate therefore studies fusion and rules, rather than removing
the contract itself. The raw-request ablation addresses the structured-policy
question separately. Outcome differences need matching call arguments and
ground-truth labels before they can be called prevented attacks or false
positive blocks. This condition also applies to cached E31 comparisons.
