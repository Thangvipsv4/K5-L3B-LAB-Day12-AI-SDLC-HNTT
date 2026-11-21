# Bằng chứng Phase 3 — HUD độ tươi (Tú)

Ticket [docs/phase3.md](../../phase3.md) mục 1.2 "HUD hiển thị". Schema ở [docs/contracts/README.md](../../contracts/README.md) mục 7.
Ảnh chụp bằng Edge headless ở 1280×720.

**HUD đọc được cả hai schema**, nên đã đẩy thẳng lên `main` trước khi bật v1.2:
- v1.1 (kho đếm): hiện như Phase 2, không có thanh độ tươi.
- v1.2 (kho cá thể `{id, kind, fresh}`, `reserved` là mảng id): thêm độ tươi và đánh dấu hàng ươn.

## Cách xem lại

```bash
python3 -m chonoi.live --mode gather      # rồi mở /?mock=gather&v=12 | quan | evening | shop (thêm &v=12)
```

`&v=12` nạp [`snapshot.v12.sample.json`](../../contracts/snapshot.v12.sample.json). Không có `&v=12` thì dùng mẫu v1.1.

## Đối chiếu

| Hiển thị | Bằng chứng | Kết quả |
|---|---|---|
| Giỏ: thanh độ tươi dưới từng ô (xanh ≥ 50, cam < 50, đỏ < 30); hàng ươn mờ, gạch chéo đỏ; nhắc "n món đã ươn — không nấu được" | [v12_gather.png](ui/v12_gather.png) | đạt |
| "Cần lấy": chỉ tính hàng **chưa ươn** vào "đã lấy", hiện nhãn "1 ươn" riêng | [v12_gather.png](ui/v12_gather.png) (cá lóc 0/2, 1 ươn) | đạt |
| Kho quán: khả dụng = chưa ươn và chưa giữ chỗ; số ươn; thanh và % của cá thể kém tươi nhất | [v12_quan.png](ui/v12_quan.png) | đạt |
| Đơn gọi: độ tươi TB phần đang giữ và giá tạm tính `floor(giá × TB/100)`, khớp công thức chốt giá ở `cook_started` | [v12_quan.png](ui/v12_quan.png): (97.2 + 44.7×3)/4 = 57.8 % → 69k | đạt |
| EveningIntro: kho nhập kèm độ tươi TB và số ươn; "món nấu được" bỏ hàng ươn | [v12_evening.png](ui/v12_evening.png) | đạt |
| Shop: kho dư kèm độ tươi (ghi "không hao ở Shop") | [v12_shop.png](ui/v12_shop.png) | đạt |
| Toast `spoiled` (giỏ/kho); toast `cook_started` hiện giá đã chốt và độ tươi TB | code `EVENT_MSG` | đạt (chờ sim phát event) |
| Không phá v1.1 khi chạy thật | [v11_gather_live.png](ui/v11_gather_live.png), [v11_quan_live.png](ui/v11_quan_live.png) | đạt |

## Ghi chú

- Ngưỡng ươn đọc từ `cfg.freshness.spoiled_below` (`live.py` gửi khối `freshness` của contract). Chưa có khối này thì dùng 30.
- `live.py` vẫn gọi `read_inventory(path)`. Khi Thắng đổi adapter v1.2 thì `--inventory` cá thể sẽ chạy mà không cần sửa UI.
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests` cho 42/42 OK.
