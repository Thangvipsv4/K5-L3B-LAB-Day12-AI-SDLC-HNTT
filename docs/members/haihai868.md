# haihai868 — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Phase 1 & 2 `sim/gather`: hoàn thành lặn, oxy, ngạt, 3 Máu, ngất LIFO, hái nút, bắt cá/sinh cá 360 tick, quái Cá Sấu M1 tuần tra/đuổi/recoil.
  - Phase 3 & 4 `sim/gather`: kho cá thể, biểu diễn tươi `u = fresh * 240`, hao $0.5$/s (2 u/tick) ở đầu bước, phát `spoiled` khi $u < 7200$, mất đồ LIFO dạng cá thể, snapshot và bàn giao chuẩn v1.2/v1.3.
  - Vai trò PO: lập [docs/clarify.md](file:///d:/K5-L3B-LAB-Day12-AI-SDLC-HNTT/docs/clarify.md), định dạng [docs/phase3.md](file:///d:/K5-L3B-LAB-Day12-AI-SDLC-HNTT/docs/phase3.md), [docs/phase4.md](file:///d:/K5-L3B-LAB-Day12-AI-SDLC-HNTT/docs/phase4.md), điều phối retro [docs/retro.md](file:///d:/K5-L3B-LAB-Day12-AI-SDLC-HNTT/docs/retro.md).
- Tôi đã review (kèm link):
  - Đọc chéo module `sim/quan` của Nam ([39e106f](https://github.com/Thangvipsv4/K5-L3B-LAB-Day12-AI-SDLC-HNTT/commit/39e106f)) và kế hoạch tích hợp của Thắng.
- AI sai ở đâu và tôi phát hiện thế nào:
  - AI trừ trực tiếp float ở độ tươi làm sai số dấu phẩy động ở ngưỡng 30; tôi phát hiện qua tài liệu ticket và yêu cầu dùng đơn vị nguyên $u$ ($240$ đơn vị/điểm tươi) theo adapter.
- Điều tôi học được:
  - Thiết kế kiến trúc với số nguyên quy ước loại bỏ triệt để lỗi rẽ nhánh do sai số float tại các ngưỡng điều kiện.
