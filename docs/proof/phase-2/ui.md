# Bằng chứng Phase 2 — client/ui (Tú, lát 4b)

Ảnh chụp bằng Edge headless ở **1280×720** từ `chonoi.live` (commit chứa file này).
Các màn chỉ có ở mode `day` (Shop, Summary…) được xem trước bằng `?mock=<màn>`, với dữ liệu lấy từ [`docs/contracts/snapshot.day.sample.json`](../../contracts/snapshot.day.sample.json). Lý do: `chonoi/sim/day.py` (Thắng) chưa có.

## Cách chạy lại

```bash
python3 -m chonoi.live --mode gather            # mở địa chỉ in ra -> Menu chính
# vào thẳng màn chơi:      http://127.0.0.1:8000/?play=1
# xem trước từng màn:      http://127.0.0.1:8000/?mock=gather|quan|dayintro|evening|result|shop|pause|summary
```

## Đối chiếu yêu cầu (docs/phase2.md mục 2 "Menu, Pause và HUD")

| Yêu cầu | Bằng chứng | Kết quả |
|---|---|---|
| Menu chính: Chơi, Thoát | [menu.png](ui/menu.png) | đạt |
| DayIntro: Ngày, món Má Tư yêu cầu; tự chuyển sau 4 s hoặc khi nhấn phím | [play_intro.png](ui/play_intro.png) (chạy thật, ghi "Tự vào sau 2 s") | đạt |
| EveningIntro: kho nhập, món nấu được | [evening.png](ui/evening.png) | đạt |
| DayResult: khách phục vụ/bỏ đi, tiền, boa, biến động uy tín | [result.png](ui/result.png) | đạt |
| Shop: mua oxy/hp, giá, cấp, "hiệu lực từ Ngày kế", tự đóng 600 tick | [shop.png](ui/shop.png) | đạt (UI). Mua thật cần Shop sim của Thắng |
| Summary: tổng tiền, điểm, uy tín cuối, món bán chạy nhất | [summary.png](ui/summary.png) | đạt (UI) |
| Pause Esc/P: mờ nền, Tiếp tục, Về menu, đứng mọi đồng hồ | [pause.png](ui/pause.png) | đạt (UI). Xem ghi chú 2 |
| HUD sáng: Máu, oxy < 25 % đổi màu và nhấp nháy, giờ ≤ 30 s đổi màu, độ sâu và vùng, giỏ, cần lấy (đã lấy/cần), hồi bắt cá, gợi ý hái/cập bến, "Thủy quái!" kèm viền tím, "Hết hơi!" | [gather.png](ui/gather.png), [play_game.png](ui/play_game.png) | đạt |
| HUD tối: đồng hồ ca, tiền ca, uy tín, kiên nhẫn từng bàn (< 25 % đỏ), tiến độ bếp, món trên tay, kho khả dụng | [quan_live.png](ui/quan_live.png) (chạy thật, 2 bếp, 4 bàn) | đạt |
| Chữ ≥ 18 px ở 1280×720 | Vẽ trên khung logic 853×480, nhân 1.5; chữ nhỏ nhất 12 px logic = 18 px | đạt |

## Ghi chú

1. **Sim không đổi.** Menu, DayIntro, EveningIntro và DayResult chỉ có ở client. Trong lúc các màn này hiện, client gọi `POST /hold` để sim đứng yên, nên không tick nào bị tiêu và headless không bị ảnh hưởng.
2. **Pause.** UI gửi một cạnh lên `pause` vào sim (Test Contract v1.1). Khi `inputs.py` chưa có nút `pause`, `live.py` tự giữ sim đứng. Khi Thắng thêm nút này, sự kiện `paused`/`resumed` sẽ ra đúng theo contract mà không cần sửa UI.
3. **Shop.** UI gửi `{"buy": "oxygen"|"hp"}` và cạnh `shop_done`. `live.py` chuyển `buy` sang `LiveInputs.set_buy()` khi hàm này có (Thắng).
4. **Lỗi đã bắt khi kiểm bằng ảnh chụp.**
   - Cờ `hold` của `live.py` trùng tên với trường giỏ `hold` của gather, nên đã đổi thành `ui_hold`.
   - Gọi `restartGame()` trước khi khai báo `let` làm script dừng (TDZ), nên đã chuyển lời gọi xuống cuối file.
   - Nhãn hai bếp B1/B2 đè nhau, nên đã rút gọn nhãn và so le vị trí.
   - Khung hình giờ có `try/catch`, lỗi vẽ hiện ngay trên màn hình.
5. Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests` cho 32/32 OK.
