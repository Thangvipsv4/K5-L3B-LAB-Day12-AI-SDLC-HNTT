# Phase 4 soak run evidence

Run in this workspace with Python 3.13.16 via `uv` on 2026-11-21.

Equivalent contract invocation:

```text
python3 -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak.json
```

Windows execution used the cached interpreter explicitly:

```text
uv run --python 3.13 python -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak.json
```

Observed summary:

```text
days=10, days_completed=10, crashes=0
earned: 70 → 724
reputation: 3.2 → 5.0
duration_s: 0.259487
exit code: 0
```

The JSON emitted by this run is stored verbatim in [`soak.json`](soak.json).
Repeated-seed determinism (excluding `duration_s`), all ten day results,
five-day plan repetition, persistent ledgers, and unique item/customer IDs
are covered by `tests/test_soak.py`.
