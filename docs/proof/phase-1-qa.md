# Phase 1 QA run log

- Date: 2026-11-21 (Asia/Saigon)
- Starting revision: `8caac8f` (`main`, matched `origin/main`; prior QA documentation edits were present and retained)
- Initial working tree for this follow-up: contained those uncommitted QA documentation edits
- Shell: PowerShell on Windows
- Evidence source: PowerShell run log and results supplied by QA Lead Vũ Trọng Thắng (`Thangvipsv4`). Codex did not rerun Python commands in its execution environment.
- Reported interpreter: Python 3.13.17

## Commands and observed results

| Command | Exit | Result |
|---|---:|---|
| `python tools/check_team.py` | 0 (reported) | **PASS**, per QA Lead supplied PowerShell log. |
| `python -m chonoi.headless --mode gather --seed 1 --ticks 600 --out out.jsonl` | 0 (reported) | **PASS**, per QA Lead supplied PowerShell log. |
| `python -m unittest discover -s tests -v` | 0 (reported) | **PASS: 32/32**, per QA Lead supplied PowerShell log. |
| `git diff --check` | 0 | **PASS**, checked in Codex before commit. |

## Findings and release gate

- QA changes: `tests/helpers.py` substitutes `sys.executable` for Python launchers in the contract command; `tests/test_team_check.py` now tests a fixed placeholder template fixture rather than reading the real `TEAM.md`; `tools/check_team.py` rejects placeholders in name, handle, and module fields.
- Python results are attributed to the QA Lead's supplied PowerShell log; Codex did not rerun them in its environment. The prior `docs/proof/phase-1-ui.md` record of 31/32 is superseded by this reported 32/32 run.
- No `phase-1` tag existed at start. The reported check results satisfy the QA gate; tag will be placed on the new QA commit.

This record distinguishes supplied execution evidence from checks run in Codex; PASS claims above are sourced to the QA Lead's PowerShell log.
