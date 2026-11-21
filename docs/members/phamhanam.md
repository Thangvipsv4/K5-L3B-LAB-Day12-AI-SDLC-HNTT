# phamhanam — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Phase 1 (`e514ecd`): Bước 0 (`TEAM.md`, `contracts`, `clarify.md` #1) và lát 3+4 `chonoi/sim/quan.py` (lịch khách, `reserved`, kiên nhẫn, nấu/phục vụ, boa, uy tín).
  - Phase 2 (`a938bb6`): nâng cấp `quan.py` hỗ trợ `day_plan`, 2 bếp `B1–B2`, 4 bàn `T1–T4`, 6 món, `score` ở `quan_end` và `snapshot()`.
- Tôi đã review & kiểm chứng:
  - Chạy `unittest discover -s tests` PASS; smoke tích hợp `gather -> quan` (`quan_end score=300`) và test kho 6 món (`customer_arrived C1` tick 120).
- AI sai ở đâu và tôi phát hiện thế nào:
  - Phase 1: AI đưa `PYTHONPATH=tests:.` lỗi trên Windows Git Bash (sửa thành `"tests;."`). Phase 2: AI giả định `day_plan` là list, nhưng khi `cat game.contract.json` thấy `dishes` là dict nên đã sửa code hỗ trợ cả dict lẫn list.
- Điều tôi học được:
  - Luôn `cat` kiểm tra contract thật trước khi code để tránh lệch schema khi ghép `day` mode.
