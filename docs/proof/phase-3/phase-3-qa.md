# Phase 3 QA proof — adapter scope

Run date: 2026-11-21. Executed with the repository's available isolated
Python 3.13.16 (`uv run --python 3.13`). No externally supplied logs are used.

## Actual command result

Command:

```text
uv run --python 3.13 python -m unittest discover -s tests -v
```

Observed output summary:

```text
Ran 52 tests in 8.641s
OK
Process exit code: 0
```

This includes the Phase 1–2 regression suite and new Phase 3 adapter/scenario
unit tests. Adapter-level inventory file round-trip, schema rejection,
freshness threshold, ID progression, and v1.2 scenario checks passed.

## Handoff boundary

The v1.2 simulation handoff test is **BLOCKED** by the current member-owned
interfaces, not represented as a successful test. Gather still exports a
count map; Quan still consumes a count map. The aggregate v1.1 Gather → Quan
smoke test in the regression suite passes, but it does not prove Phase 3
individual-item behavior. `game.contract.json` is still v1.1; enabling v1.2
before Gather/Quan/UI integration is ready is intentionally deferred under
the Phase 3 integration plan.

`kho.json` was not modified and remains untracked outside the Phase 3
changeset. Its SHA-256 remains `1D03E6DAB41631B3C63786E2386F71312AE82CB5A45583C2216E018FB27EE3B5`,
matching the pre-work value. No protected member module was edited.
