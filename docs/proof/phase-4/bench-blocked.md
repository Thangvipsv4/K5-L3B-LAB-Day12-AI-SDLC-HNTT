# Phase 4 benchmark status — BLOCKED

The benchmark module and command are now present on `origin/main`, and the
contract declares `python3 -m chonoi.bench`. QA attempted the required run:

```text
uv run --python 3.13 python -m chonoi.bench --seed 42 --duration 30 --out docs/proof/phase-4/bench.json
```

The command exited 1 after 93 seconds because Chrome at
`C:\Program Files\Google\Chrome\Application\chrome.exe` did not submit a
measurement. No `bench.json` was written. This is recorded as BLOCKED; no
benchmark result is claimed.
