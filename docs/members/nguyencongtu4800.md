# nguyencongtu4800 — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Phase 1 HUD `client/ui`: cảnh báo ngạt/oxy thấp, trạng thái mặt nước, giỏ đầy, kho khả dụng, bảng đơn gọi, trạng thái bếp, món trên tay, toast sự kiện — [e19d24f](https://github.com/Thangvipsv4/K5-L3B-LAB-Day12-AI-SDLC-HNTT/commit/e19d24f)
  - README "Sáng tạo của nhóm" + CREDITS — [d435a93](https://github.com/Thangvipsv4/K5-L3B-LAB-Day12-AI-SDLC-HNTT/commit/d435a93)
- Tôi đã review (kèm link): (phase 1: đọc chéo phần QA của Thắng — điền link khi có)
- AI sai ở đâu và tôi phát hiện thế nào:
  - AI định "dựng HUD từ đầu" trong khi starter đã có thanh oxy/Máu/giỏ; đọc lại `index.html` mới thấy chỉ cần lấp chỗ thiếu.
  - AI chạy test trên Windows ra 20 lỗi; so với bản trước thay đổi (`git stash`) thấy y hệt → do thiếu lệnh `python3`, không phải do HUD.
  - Đếm ngược choke giả định `zero_oxy_ticks` đếm từ lúc oxy = 0; cần kiểm lại khi Hải xong lát 1.
- Điều tôi học được: UI chỉ đọc snapshot + bỏ qua trường thiếu giúp làm song song với sim mà không chờ ai.
