# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 | Nam (`phamhanam`) | AI assistant | Chốt Bước 0 (`TEAM.md`, `docs/contracts/README.md`, `clarify.md`) + code lát 3 (`chonoi/sim/quan.py`) + script test headless | ước lượng ~15k–25k token | AI sai 2 chỗ nhỏ: dùng `PYTHONPATH=tests:.` trên Windows (phải dùng `;`) và lồng khối code trong heredoc; phát hiện khi chạy Git Bash và sửa ngay. |
