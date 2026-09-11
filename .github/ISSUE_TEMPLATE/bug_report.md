---
name: Bug report
about: Report a defect in IntentGate (not a security vulnerability — see SECURITY.md)
title: "[Bug] "
labels: bug
---

**Describe the bug**
A clear description of what is wrong.

**To reproduce**
1. Branch/commit:
2. Command(s):
3. Expected vs actual:

**Environment**
- OS / Python version:
- Model backend (gpt-4o-mini / deepseek-v4 / mimo / muse / other):
- Gate config (`alpha`, `tau`, `delta`, benchmark_mode):

**Test evidence**
Paste `pytest -q` summary and any relevant JSONL trace lines (redact secrets).

**Security note**
Do not file security issues here — use private reporting per `SECURITY.md`.
