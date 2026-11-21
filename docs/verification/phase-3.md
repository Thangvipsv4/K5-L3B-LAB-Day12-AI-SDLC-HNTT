# Phase 3 verification — inventory adapter and QA

Date: 2026-11-21 (local client date). Scope: Thắng-owned adapter, contract
freshness validation, and scenario v1.2 validation. No Gather/Quan simulation,
UI/HUD, `live.py`, or `kho.json` changes were made.

## Verified in this workspace

| Check | Result | Evidence |
|---|---|---|
| Inventory schema (exact item keys, nonempty IDs, allowed kinds, finite freshness in [0,100], unique IDs) | PASS | `tests/test_inventory.py` |
| Legacy count object rejected by v1.2 item-list validator | PASS | `ItemSchema.test_reject_count_schema_unknown_kind_duplicate_id_and_bad_freshness` |
| Atomic item file write/read and ID order | PASS | `ItemSchema.test_round_trip_item_file_sorts_by_numeric_id` |
| Integer freshness conversion, threshold neighbor, clamping and one-time spoil crossing | PASS | `ItemSchema` conversion and decay tests |
| Shared `IdAllocator` advances across allocated items | PASS | `ItemSchema.test_ids_are_unique_across_allocator_phases_and_shop_items` |
| Scenario v1.2 item hold/stock and reserved-ID checks | PASS | `V12Scenario` tests (freshness tuning supplied in test) |
| Full unittest suite (Phase 1–2 regression plus Phase 3 adapter tests) | PASS — 52 tests | `uv run --python 3.13 python -m unittest discover -s tests -v`; Python 3.13.16, 8.641s, exit 0 |
| `git diff --check` | PASS | Ran after final changes; exit 0 |

## Integration status and dependencies

The repository contract remains v1.1 and its checked-in `game.contract.json`
has no `freshness` tuning block. The Phase 3 plan (D6) says to keep v1.1 active
until Gather, Quan, and HUD integration is ready. The additive v1.2 scenario
path is activated only when a caller supplies the Phase 3 `freshness` block.

The actual game handoff smoke test for v1.2 is **BLOCKED**, not passed:

- `GatherSim.inventory_items()` in `chonoi/sim/gather.py` still returns a
  count dictionary and stores `hold` as kind strings.
- `QuanSim` in `chonoi/sim/quan.py` still accepts count dictionaries and its
  stock/reservation/cooking logic is count-based.
- `chonoi/runner.py`, headless/live inventory boundaries and the UI still
  consume/emit v1.1 shapes.

Those files are owned by other members and were left untouched per scope. As a
result, end-to-end v1.2 Gather → Quan transfer, live freshness decay during
gameplay, and v1.2 HUD display are not verified. Enabling `contract_version`
1.2 in `game.contract.json` before those dependencies land would break runtime
behavior, so it remains unchanged at 1.1.

## Commands

```powershell
$env:UV_CACHE_DIR = Join-Path $env:TEMP 'codex-uv-cache-phase2'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $env:TEMP 'codex-uv-python-phase2'
uv run --python 3.13 python -m unittest discover -s tests -v
git diff --check
```

Both commands were run here after the final code and documentation edits.
