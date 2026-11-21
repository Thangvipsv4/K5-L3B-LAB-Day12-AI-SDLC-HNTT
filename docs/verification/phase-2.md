# Phase 2 verification — Day / Shop / Pause

## Scope and restrictions

This QA change implements the v1.1 headless/day simulation path and does not edit `chonoi/sim/gather.py`, `chonoi/sim/quan.py`, `chonoi/live.py` or `chonoi/web/`. The latest main also contains the team's UI/live Phase 2 work (`4b2d66f`); its screenshots and UI checklist are recorded in [phase-2 UI proof](../proof/phase-2/ui.md).

## Acceptance matrix

| AC | Verification | Evidence | Status |
|---|---|---|---|
| Mode `day`, `--days 1..5`, phase lifecycle and in-memory stock handoff | Two-day fixed-fixture headless smoke with 1-tick gather/quan phases | [Integration record](../proof/phase-2/integration.md) | PASS |
| Day plan events, persistent money/earned/reputation and `days_completed` / `days_complete` | DaySim unit coverage and smoke output | [Integration record](../proof/phase-2/integration.md) | PASS |
| Shop oxygen/HP purchases, `bought` / `buy_failed`, early close and 600 active-tick timeout | ShopSim unit tests | [Integration record](../proof/phase-2/integration.md) | PASS |
| Upgrade levels become active on the following day | Two-day fixture checks oxygen capacity on day 2 | [Integration record](../proof/phase-2/integration.md) | PASS |
| Pause/resume freezes simulation and phase timers | Session unit test and pause-during-Shop integration fixture | [Integration record](../proof/phase-2/integration.md) | PASS |
| Menu, DayIntro, EveningIntro, Shop, Summary, Pause and HUD | Team UI smoke and screenshot evidence | [UI proof](../proof/phase-2/ui.md) | PASS for displayed UI; gameplay Shop input is covered by sim/headless tests |
| Fixed scenario fixture (`random_fish: false`, preset hold) | `tests/fixtures/day_mode.json` | [Integration record](../proof/phase-2/integration.md) | PASS |
| Phase 1 regression | Full `unittest` suite | [Integration record](../proof/phase-2/integration.md) | PASS as part of 42/42 suite |
| Diff formatting | `git diff --check` | This worktree | PASS |

`game.contract.json` remains contract version 1.1, and its day plan/shop data is read as tuning. Python was provisioned only in `%TEMP%` through `uv` because this shell has no global Python launcher. All listed checks were run successfully; see the proof log for exact commands and outputs.
