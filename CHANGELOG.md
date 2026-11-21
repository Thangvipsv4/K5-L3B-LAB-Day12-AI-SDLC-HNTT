# Changelog

Tất cả thay đổi đáng chú ý của dự án **Chợ Nổi** (nhóm **HNTT**) được ghi nhận tại đây.

## [1.0.0] - Phase 4 (Bench, Soak, Đóng gói & Phát hành)
- **Bench & Soak**: Bổ sung `bench_cmd` (đo FPS/p1_low/load_ms ở 1280×720) và `soak_cmd` (chạy headless nhiều ngày liên tiếp, kiểm tra không crash) trong `game.contract.json` v1.3.
- **UI & Trợ năng**: Thêm 3 cảnh báo trực quan (thủy quái gần, oxy sắp hết, khách sắp giận) và chế độ tương phản cao trên `chonoi/web/index.html`.
- **Tài liệu & Phát hành**: Hoàn thiện `README.md` (hướng dẫn chạy $\le 3$ lệnh), `CHANGELOG.md`, `CREDITS.md`, `docs/verification/phase-4.md`, và `docs/retro.md`.

## [phase-3] - Phase 3 (Schema kho cá thể & Độ tươi v1.2)
- **Adapter & Schema (`chonoi/inventory.py`, `chonoi/scenario.py`)**: Chuyển kho từ đếm số lượng sang mảng cá thể `{"id", "kind", "fresh"}` với đơn vị nội bộ `240 u/điểm` (`SPOIL_U = 7200`).
- **Gather (`chonoi/sim/gather.py`)**: Giỏ `hold` cá thể, hao `0.5/s` (`-2 u/tick`), phát `spoiled` (`location: "hold"`), mất đồ LIFO khi `monster_hit`/`faint`.
- **Quán (`chonoi/sim/quan.py`)**: `stock` cá thể, hao `0.25/s` (`-1 u/tick`), giữ chỗ `reserved` theo `id` (tươi nhất trước), nhả và giữ lại 1 lần khi ươn (`unfulfillable` nếu thiếu), `base_price = floor(price * avg_fresh / 100)`.
- **HUD (`chonoi/web/index.html`)**: Hiển thị độ tươi và nhận biết hàng ươn trên giỏ, kho và món ăn.

## [phase-2] - Phase 2 (Day mode, Shop, Quái & Mở rộng Quán)
- **Day & Shop (`chonoi/sim/day.py`, `chonoi/sim/shop.py`, `chonoi/runner.py`)**: Chu trình `day_start -> day_plan -> gather -> quan -> shop`, nâng cấp oxy/HP áp dụng từ ngày kế, hỗ trợ `pause`/`resume`.
- **Gather**: Cá bơi, sinh đàn theo chu kỳ (`fish_spawned`), thêm nút `keo_neo`, loài `ca_keo`, và cá sấu `M1`/`M2` (`patrol`/`chase`/`recoil`, `monster_hit`, `invuln_ticks`).
- **Quán**: Mở rộng 2 bếp (`B1–B2`), 4 bàn (`T1–T4`), menu 6 món, lọc menu theo `day_plan`, tính `score = earned + 100 * floor(reputation)`.
- **UI**: Màn hình Menu, DayIntro, EveningIntro, DayResult, Summary, Pause và Shop UI.

## [phase-1] - Phase 1 (Core MVP Lặn & Quán)
- **Gather**: Di chuyển dưới nước, oxy/ngạt/choke, hái nút thực vật, bắt cá, giỏ LIFO.
- **Quán**: Lịch khách `120 + 900*k`, giữ chỗ `reserved` theo `(order_tick, id bàn)`, nấu/phục vụ/trả tiền, boa `0.2`, uy tín `+0.2/-0.5`.
- **UI & QA**: HUD tối thiểu đọc `snapshot()`, smoke test headless & kiểm chứng `docs/verification/phase-1.md`.
