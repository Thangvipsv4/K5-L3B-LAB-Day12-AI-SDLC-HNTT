# Phase 4 verification — soak, contract, bench/QA

Date: 2026-11-21. Work performed for Vũ Trọng Thắng (`Thangvipsv4`).
`kho.json`, Gather/Quan gameplay modules, and Tú's UI/live modules were not
modified.

## Acceptance matrix

| TICKET-04 acceptance item | Verification | Result |
|---|---|---|
| Contract version 1.3 | `game.contract.json` root | PASS |
| `soak_cmd` declared and callable | `python3 -m chonoi.soak`; actual Windows run used `uv run --python 3.13 python -m chonoi.soak` | PASS |
| `bench_cmd` declared | Contract declares `python3 -m chonoi.bench` from `origin/main` | PASS |
| 10 continuous days, each gather → quan → shop; D6–D10 replay D1–D5 | Actual seed 7 soak run and `tests/test_soak.py` | PASS — 10/10 days, 0 crashes |
| Money, cumulative earned, reputation, upgrades and individual IDs persist | Ten-day deterministic runner and test instrumentation | PASS — ledgers carried; unique item/customer IDs; upgrades were purchased |
| Required soak JSON schema | [`soak.json`](../proof/phase-4/soak.json) | PASS — exactly `days`, `days_completed`, `crashes`, `results`, `duration_s`; each result has `day`, `earned`, `reputation`, `score` |
| Same-seed gameplay determinism (excluding wall-clock duration) | Two independent runs in unit test | PASS |
| Rendered benchmark, seed 42, 30 measured seconds, benchmark JSON | `uv run --python 3.13 python -m chonoi.bench --seed 42 --duration 30 --out docs/proof/phase-4/bench.json` | BLOCKED — Chrome did not submit a measurement within 93s; no artifact was written |
| Phase 1–4 regression suite | `uv run --python 3.13 python -m unittest discover -s tests -v` | Pending final run for this commit |
| Diff formatting | `git diff --check` | Pending final run for this commit |
| Accessibility/high contrast, clean-clone packaging, GitHub Release | Owned by other roles/modules and not exercised by this QA task | NOT VERIFIED HERE |

## Soak evidence

Executed command:

```text
uv run --python 3.13 python -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak.json
```

Python 3.13.16; observed `days_completed=10`, `crashes=0`, cumulative earned
from 70 to 724, reputation from 3.2 to 5.0, `duration_s=0.259487`, exit code 0.
The exact JSON artifact and run note are in [`docs/proof/phase-4/`](../proof/phase-4/).

The soak keeps a single `Streams` and `IdAllocator` alive for all ten daily
simulation instances. Each run uses the matching contract day plan, a fixed
item hold, one deterministic customer order, and a fixed serving policy. The
gameplay fields repeat for the same seed; `duration_s` is intentionally a
wall-clock measurement and is excluded from equality checks.

## Outstanding dependency

The benchmark runner is present, but its browser-based measurement timed out in
this environment. [`bench-blocked.md`](../proof/phase-4/bench-blocked.md)
records the command and observed failure. The Phase 4 release/visual
accessibility checks remain outside this Thắng-owned QA change and need their
assigned owners' evidence.
