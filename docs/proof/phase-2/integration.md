# Phase 2 headless integration proof

## Fixed fixture

`tests/fixtures/day_mode.json` seeds Day mode with the full day-1 plan in the gather hold, disables random fish and customer arrivals, and sets gather/restaurant phase clocks to one tick. This keeps the integration path deterministic and fast while exercising the real GatherSim and QuanSim handoff. The separate DaySim unit test uses fake child sims to exercise orchestration independently.

## Intended smoke invocation

The smoke test in `tests/test_day.py::DayOrchestration.test_headless_fixture_hands_off_stock_and_runs_two_days` invokes the public headless entry point with `--mode day --days 2`, the fixed fixture, pause/resume during Shop, one oxygen purchase, and Shop close inputs. It checks phase events, next-day upgrade activation, frozen Shop time, and the final completion count.

## Execution record

- `python`, `python3`, and `py` were not available on PATH. Python 3.13.16 was installed into `%TEMP%` using `uv`; no Python files or dependencies were added to the repository.
- `uv run --python 3.13 python -m unittest discover -s tests -v` — **PASS**, 42 tests in 8.212 s (including Phase 1 regression).
- Two-day headless smoke (`--mode day --days 2 --seed 17 --ticks 12`, fixed fixture, pause/resume and oxygen purchase) via `uv run --python 3.13 python -m chonoi.headless` — **PASS**, exit 0; output contained 19 event rows and final `reason=days_complete`, `days_completed=2`.
- `git diff --check` — **PASS**, exit 0.
- The fixture and test suite exercise the real headless day path; the separate DaySim unit test uses fake child sims to isolate orchestration.
- Shop smoke emits `paused`, `resumed`, and a successful oxygen `bought` event; the Shop timer stays at 600 through the paused snapshots.
- No inventory file is used or written by this Day mode path. Existing root `kho.json` was left untouched.

Equivalent direct command (using temporary inputs/output):

```powershell
uv run --python 3.13 python -m unittest discover -s tests -v
uv run --python 3.13 python -m chonoi.headless --mode day --days 2 --seed 17 --ticks 12 --scenario tests/fixtures/day_mode.json --inputs <generated-inputs.json> --snapshot-every 1 --out <temp-output.jsonl>
```

The unittest includes that smoke command with temporary inputs and output paths.
