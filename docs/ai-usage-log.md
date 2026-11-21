# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 | Nam (`phamhanam`) | AI assistant | Chốt Bước 0 (`TEAM.md`, `docs/contracts/README.md`, `clarify.md`) + code lát 3 (`chonoi/sim/quan.py`) + script test headless | ước lượng ~15k–25k token | AI sai 2 chỗ nhỏ: dùng `PYTHONPATH=tests:.` trên Windows (phải dùng `;`) và lồng khối code trong heredoc; phát hiện khi chạy Git Bash và sửa ngay. |
| 1 | Tú | Claude Code (Claude Opus 5.5) | HUD phase 1 (`index.html`), toast sự kiện, README sáng tạo, CREDITS, bằng chứng UI | ~1 phiên | AI định viết HUD từ đầu dù starter đã có; chạy test trên Windows lỗi do thiếu `python3` (không do code), phát hiện bằng `git stash` so sánh |
| Phase 1 | Thắng (`Thangvipsv4`) | Codex | QA: sửa interpreter subprocess dùng `sys.executable`; sửa test template để dùng fixture độc lập; thêm kiểm tra placeholder trong `tools/check_team.py`; cập nhật verification/proof/retro | Không có số liệu token | QA Lead cung cấp log PowerShell với Python 3.13.17: `check_team.py` PASS, headless gather 600 ticks PASS, unittest 32/32 PASS. Codex dùng log được cung cấp làm nguồn xác minh và ghi rõ attribution; `git diff --check` PASS trong Codex. |
