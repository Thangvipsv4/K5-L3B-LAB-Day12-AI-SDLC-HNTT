# Retro nhóm

## Phase 1 (QA — 2026-11-21)
- Điều tốt: tách test template thành fixture riêng, để test phản ánh validator chứ không trạng thái TEAM thật; helper subprocess ưu tiên chính interpreter đang chạy test.
- Kết quả QA: theo log PowerShell do QA Lead cung cấp (Python 3.13.17), `check_team.py` PASS, headless gather 600 ticks PASS, unittest 32/32 PASS; `git diff --check` cũng PASS khi kiểm tra trong Codex.
- Nguồn xác minh được ghi rõ trong `docs/proof/phase-1-qa.md`; Codex không chạy lại Python tại môi trường của mình.
- 1 hành động: giữ thói quen chạy test với interpreter hiện hành và tách fixture kiểm thử khỏi dữ liệu repo thật.
- Tag `phase-1` được tạo trên commit QA sau khi xác nhận chưa có tag trùng.

## Phase 2 (nhanh)
- Điều tốt:
- Điều tệ:
- 1 hành động cho Phase 3:

## Phase 4 (cuối)
- Rà lại hành động Phase 2: đã làm chưa? vì sao?
- Điều tốt / điều tệ:
- Số liệu: số commit theo người, cách đọc code của nhau, token theo người:
- Một lần AI sai và cách nhóm phát hiện:
- Nếu làm lại, đổi gì:
