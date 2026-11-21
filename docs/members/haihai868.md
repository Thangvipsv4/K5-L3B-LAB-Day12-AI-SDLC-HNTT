# haihai868 — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Phase 1 & 2 `sim/gather`: hoàn thành lặn, oxy, ngạt, 3 Máu, ngất LIFO, hái nút, bắt cá/sinh cá 360 tick, quái Cá Sấu M1 tuần tra/đuổi/recoil.
  - Phase 3 `sim/gather`: chuyển sang kho cá thể, biểu diễn tươi `u = fresh * 240`, hao $0.5$/s (2 u/tick) ở đầu bước, phát `spoiled` khi $u < 7200$ theo id, mất đồ cá thể theo LIFO, xuất kho và snapshot chuẩn v1.2 song song v1.1.
  - Vai trò PO: lập [docs/clarify.md](file:///d:/K5-L3B-LAB-Day12-AI-SDLC-HNTT/docs/clarify.md), định dạng [docs/phase3.md](file:///d:/K5-L3B-LAB-Day12-AI-SDLC-HNTT/docs/phase3.md).
- Tôi đã review (kèm link):
  - Đọc chéo lát 3 & 4 của Nam (`sim/quan`) và tài liệu kế hoạch Phase 3 của Thắng/Nam.
- AI sai ở đâu và tôi phát hiện thế nào:
  - Khi triển khai độ tươi, AI định trừ float trực tiếp làm sai số dấu phẩy động ở ngưỡng 30; tôi phát hiện qua tài liệu ticket và yêu cầu dùng đơn vị nguyên $u$ ($240$ đơn vị/điểm tươi) theo adapter.
- Điều tôi học được:
  - Thiết kế kiến trúc với biểu diễn số nguyên quy ước loại bỏ hoàn toàn lỗi rẽ nhánh do sai số float tại các ngưỡng điều kiện.
