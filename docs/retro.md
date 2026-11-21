# Retro nhóm

## Phase 2 (QA — 2026-11-21)
- Điều tốt: orchestration được tách khỏi luật Gather/Quán; unit test có sim con giả, smoke test dùng fixture cố định đủ kho với cá/khách ngẫu nhiên tắt.
- Kết quả: full suite 41/41 PASS, smoke headless hai ngày PASS, `git diff --check` PASS. Python 3.13.16 được cài vào TEMP bằng uv để chạy kiểm tra.
- Hành động: tiếp tục dùng fixture deterministic và sim doubles cho test điều phối; mở rộng smoke khi thêm phase hoặc input contract.
- Phạm vi điều khiển Pause hiện được kiểm qua headless; UI/live không được sửa theo giới hạn công việc.

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

## Phase 4 (cuối — PO điều phối)
- Rà lại hành động Phase 2: Đã thực hiện đầy đủ. Nhóm duy trì việc sử dụng các fixture deterministic độc lập và sim doubles cho các test điều phối (`DaySim`, `QuanSim`, `GatherSim`). Các bài test không phụ thuộc vào trạng thái toàn cục nên toàn bộ test suite chạy ổn định.
- Điều tốt:
  - 4 thành viên phân công theo đúng sở trường và hợp đồng: Thắng (adapter/QA), Nam (Quán), Tú (HUD), Hải (Gather/PO).
  - Tích hợp mượt mà qua các contract version (v1.0 -> v1.1 -> v1.2 -> v1.3) nhờ thiết kế adapter thông minh (`u = fresh * 240`) giữ nhánh `main` luôn xanh 100% qua tất cả các phase.
- Điều tệ:
  - Môi trường Windows có một số điểm khác biệt về CLI (lệnh `python3` vs `python`, separator `;` vs `:` trong PYTHONPATH) cần xử lý bằng các lệnh tương thích đa nền tảng.
- Số liệu:
  - Số commit theo người: Hải (4 commit chính: phase 1, phase 2, v1.1 snapshot align, phase 3 gather items & decay), Nam (3 commit cho quan và contracts), Thắng (QA, test suite, adapter, verification), Tú (HUD và tài liệu UI).
  - Cách đọc code của nhau: cặp Hải <-> Nam đọc chéo module Gather <-> Quán; cặp Tú <-> Thắng đọc chéo HUD <-> QA.
  - Token ước tính: Hải ~45k, Nam ~45k, Tú ~35k, Thắng ~40k.
- Một lần AI sai và cách nhóm phát hiện:
  - AI ban đầu đề xuất tính độ tươi trực tiếp bằng số thực (float), dẫn đến sai số dấu phẩy động ở phép so sánh ngưỡng 30 (7199.9999 thay vì 7200). Nhóm phát hiện sớm qua thảo luận kỹ thuật (Quyết định D2/D3 trong kế hoạch Phase 3) và yêu cầu AI sử dụng đơn vị nguyên $u$ ($240$ đơn vị/điểm tươi), triệt tiêu hoàn toàn rủi ro lệch nhánh.
- Nếu làm lại, đổi gì:
  - Thống nhất môi trường chuẩn (như container hoặc virtualenv với wrapper script) ngay từ 10 phút đầu tiên để toàn đội không mất thời gian xử lý khác biệt OS giữa Windows và Linux/macOS.
