# phamhanam — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Cùng nhóm hoàn tất Bước 0 (`TEAM.md`, `game.contract.json`, `docs/contracts/README.md`, ghi `docs/clarify.md` #1 cho `test_template_is_rejected`).
  - Triển khai lát 3 trong `chonoi/sim/quan.py` (commit `e514ecd`): lịch khách theo `first_customer_tick`/`customer_interval_s`, chọn món qua `Streams`, giữ chỗ `reserved` từ tồn vật lý `stock`, đếm ngược kiên nhẫn, `no_dish`, `customer_left` (`patience`/`closing`) và kiểm mâu thuẫn `scenario` mã `2`.
- Tôi đã review (kèm link):
  - Kiểm tra diff `chonoi/sim/quan.py`, chạy 28 test nền và 5 ca headless lát 3; đang đọc chéo lát 1 (`sim/gather`) của Hải trên `main`.
- AI sai ở đâu và tôi phát hiện thế nào:
  - AI đưa lệnh `PYTHONPATH=tests:.` bị lỗi `ModuleNotFoundError` trên Windows Git Bash (phải dùng `"tests;."`) và lồng dấu khối code trong heredoc làm gãy đoạn copy; mình phát hiện ngay khi chạy thử trên máy và sửa lại.
- Điều tôi học được:
  - Đối chiếu kỹ PRD-0 và `chonoi/web/index.html` trước khi code giúp tránh nhầm `stock` vật lý vs `reserved` và khớp chính xác tên trường snapshot.
