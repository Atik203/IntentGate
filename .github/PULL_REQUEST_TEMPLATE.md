## Summary

<!-- What does this PR do? One paragraph. -->

## Roadmap item

<!-- e.g. Phase 4 — Gate 2; link the roadmap line/issue -->

- [ ] `roadmap.md` checkboxes updated in this PR

## Type

- [ ] feat — new functionality
- [ ] fix — bug fix
- [ ] docs — documentation only
- [ ] test — tests only
- [ ] exp — experiment / results
- [ ] chore — tooling, config

## Test plan

<!-- Commands run + observed results. Paste the pytest summary line. -->

- [ ] `pytest -q` passes locally (paste summary)
- [ ] CI green

## Security checklist

- [ ] No bypass path introduced; `tests/test_no_bypass.py` green
- [ ] Ordering invariant preserved; `tests/test_gate_ordering.py` green
- [ ] Gate-call JSONL logging preserved (`S`, `S_sem`, `S_rule`, decision, latency)
- [ ] Fail-closed defaults intact for missing/unknown contract fields
- [ ] No secrets, `.env`, `data/raw/`, or `results/*.jsonl` committed

## Notes for reviewers

<!-- Design tradeoffs, blueprint sections touched, known limitations. -->
