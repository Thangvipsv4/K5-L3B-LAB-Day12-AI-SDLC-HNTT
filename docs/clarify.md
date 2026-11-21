# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 10:04 | `tests/test_team_check.py::test_template_is_rejected` đọc trực tiếp `TEAM.md` và ép phải có lỗi, nên khi nhóm điền `TEAM.md` hợp lệ (`tools/check_team.py` OK) thì test này FAIL. Nhóm xử lý thế nào (giữ nguyên không sửa test hay cập nhật)? | Tạm giữ nguyên không sửa test theo rule `AGENTS.md`; tiếp tục dùng `tools/check_team.py` + 31/32 test còn lại, chờ giảng viên xác nhận. | Hải (PO) hỏi GV |
| 2 | 2026-11-21 (Phase 3, phút 0–7) | Thứ tự phần tử trong `customers[].reserved` (mảng id) là gì? Ticket chỉ quy định `cook_started.items` sắp kind rồi id và file/stock sắp theo id. | Giả định: `reserved` sắp **kind rồi id**, giống `cook_started.items`. | Nhóm (Tú chốt, chờ PO hỏi Anh Năm) |
| 3 | 2026-11-21 (Phase 3) | Lưu độ tươi thế nào để rẽ nhánh đúng ở ngưỡng 30 và đọc lại file không lệch? | Bên trong sim dùng số nguyên `u = fresh × 240` (gather −2/tick, quán −1/tick, ươn khi `u < 7200`). Đọc file: `Fraction(str(fresh)) × 240`, cách số nguyên < 1e-6 thì làm tròn. Ghi: `float(u/240)`. Chi tiết ở docs/plan/phase-3.md D2–D3. | Nhóm, theo gợi ý TIP của ticket |
| 4 | 2026-11-21 (Phase 3) | Nhóm 4 người có làm mở rộng `current` / `reservations` không? | Không làm, vì ticket ghi nhóm 4 người không bắt buộc. Ưu tiên lõi độ tươi và bàn giao kho. | Nhóm |
| 5 | 2026-11-21 (Phase 4) | Cảnh đo benchmark có render chạy thế nào? | Chạy trên cảnh lặn (`gather`) lõi với Út Sen đứng yên ở bến `[2, 0]`, seed 42, độ tươi, cá bơi và Cá Sấu Năm Chèo hoạt động; làm nóng 3s, đo 30s xuất `bench.json`. | Đặc tả ticket 04 |
