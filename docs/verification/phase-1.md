# Ma trận truy vết Phase 1

Ngày xác minh QA: 2026-11-21 · nhánh `main` · baseline `8caac8f`.

## Lệnh kiểm thử thực tế

Kết quả dưới đây dựa trên log PowerShell do QA Lead cung cấp: Python 3.13.17; các bước xác minh đều PASS. Codex không chạy lại Python trong môi trường hiện tại.

| Lệnh | Kết quả |
|---|---|
| `python tools/check_team.py` | **PASS** — log PowerShell do QA Lead cung cấp. |
| `python -m chonoi.headless --mode gather --seed 1 --ticks 600 --out out.jsonl` | **PASS** — log PowerShell do QA Lead cung cấp. |
| `python -m unittest discover -s tests -v` | **PASS** — 32/32 test theo log PowerShell do QA Lead cung cấp. |
| `git diff --check` | **PASS** — kết quả kiểm tra hiện tại trong Codex. |

Trạng thái ban đầu của QA follow-up: `HEAD` khớp `origin/main` tại `8caac8f`, có tài liệu QA chưa commit và các thay đổi QA runner/validator/test; tag `phase-1` chưa tồn tại. Test template hiện dùng fixture placeholder riêng, còn validator từ chối placeholder, nên TEAM thật có thể hợp lệ.

| AC | Cách kiểm chứng | Bằng chứng | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| Bộ kiểm tra nhóm | `python tools/check_team.py` | [Bản ghi chạy QA](../proof/phase-1-qa.md) | PASS theo log PowerShell do QA Lead cung cấp. |
| Gather headless seed 1, 600 ticks | Lệnh headless theo yêu cầu | [Bản ghi chạy QA](../proof/phase-1-qa.md) | PASS theo log PowerShell do QA Lead cung cấp. |
| Toàn bộ unittest | `python -m unittest discover -s tests -v` | [Bản ghi chạy QA](../proof/phase-1-qa.md) | PASS, 32/32 theo log PowerShell do QA Lead cung cấp. |

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt: các bước `check_team`, headless 600 ticks, 32/32 unittest và `git diff --check` đều PASS theo nguồn nêu trên.
- Thay đổi được giới hạn trong test helper, test validator và công cụ kiểm tra nhóm; không sửa logic game.
- Tag `phase-1`: đủ điều kiện QA; sẽ được tạo trên commit QA nếu chưa tồn tại.
