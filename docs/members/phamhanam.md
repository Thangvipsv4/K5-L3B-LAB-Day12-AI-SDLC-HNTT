# phamhanam — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - P1 (`7c029be`, `e514ecd`, `6d174da`): Setup TEAM/contracts; lát 3+4 `sim/quan.py` (lịch khách, `reserved`, nấu/phục vụ, boa, uy tín).
  - P2 (`a938bb6`): Nâng cấp `quan.py` 2 bếp, 4 bàn, 6 món, `day_plan`, `score` ở `quan_end`.
  - P3 (`113d9a0`, `39e106f`): Viết ADR-0003; `quan.py` v1.2 kho cá thể (hao fresh, giữ theo id tươi nhất, nhả khi ươn, giá theo tươi).
  - P4 (`9aa01a4`): Hoàn thiện `CHANGELOG.md`, `CREDITS.md`, cùng nhóm chốt 61 test PASS và gắn tag `phase-4` / `v1.0.0`.
- Tôi đã review & kiểm chứng:
  - Smoke tích hợp `gather -> quan`, kiểm thử v1.2 (ươn `I1` nhả/giữ lại `I2`, `base_price: 47`), chạy 61/61 unit tests PASS và `check_team.py`.
- AI sai ở đâu và tôi phát hiện thế nào:
  - P2: AI đoán `day_plan` là list thay vì dict (`cat` contract phát hiện). P3: AI sinh script test thiếu 3 tham số `InputState`, tra `inputs.py` sửa `TypeError`.
- Điều tôi học được:
  - Thiết kế giữ tương thích ngược khi refactor schema giúp team tích hợp an toàn, không làm vỡ luồng code của nhau.
