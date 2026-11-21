# haihai868 — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Phase 1 `sim/gather` (commit [7e4289a](https://github.com/Thangvipsv4/K5-L3B-LAB-Day12-AI-SDLC-HNTT/commit/7e4289a)): hoàn thành Lát 1 (oxy, ngạt 60 tick, 3 Máu, ngất LIFO, dive/surface/oxygen_empty/choke/faint) và Lát 2 (hái nút N1–N4 hồi 20s, bắt cá F1–F6, cooldown, cập bến, xuất file kho).
  - Phase 2: chuẩn bị logic cá bơi, sinh cá theo chu kỳ 360 tick và cơ chế quái vật Cá Sấu Năm Chèo M1 tuần tra/truy đuổi/recoil.
  - Vai trò PO: lập và theo dõi [docs/clarify.md](file:///d:/K5-L3B-LAB-Day12-AI-SDLC-HNTT/docs/clarify.md) (vấn đề `test_template_is_rejected`).
- Tôi đã review (kèm link):
  - Đọc chéo lát 3 và lát 4 của Nam (`sim/quan`, commit [e514ecd](https://github.com/Thangvipsv4/K5-L3B-LAB-Day12-AI-SDLC-HNTT/commit/e514ecd) và [6d174da](https://github.com/Thangvipsv4/K5-L3B-LAB-Day12-AI-SDLC-HNTT/commit/6d174da)).
- AI sai ở đâu và tôi phát hiện thế nào:
  - Khi triển khai ngất xỉu, AI ban đầu xóa thẳng giỏ đồ mà quên ghi nhận mảng `lost` theo thứ tự LIFO (nhặt sau mất trước) cho sự kiện `faint`. Phát hiện khi đối chiếu bảng sự kiện mục E trong PRD-0 và đã yêu cầu AI sửa lại ngay.
- Điều tôi học được:
  - Kiểm thử hộp đen với các scenario độc lập giúp xác minh chính xác các mốc thời gian (tick biên) mà không phụ thuộc vào toàn bộ tiến trình game.
