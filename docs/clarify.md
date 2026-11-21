# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 10:04 | `tests/test_team_check.py::test_template_is_rejected` đọc trực tiếp `TEAM.md` và ép phải có lỗi, nên khi nhóm điền `TEAM.md` hợp lệ (`tools/check_team.py` OK) thì test này FAIL. Nhóm xử lý thế nào (giữ nguyên không sửa test hay cập nhật)? | Tạm giữ nguyên không sửa test theo rule `AGENTS.md`; tiếp tục dùng `tools/check_team.py` + 31/32 test còn lại, chờ giảng viên xác nhận. | Hải (PO) hỏi GV |
