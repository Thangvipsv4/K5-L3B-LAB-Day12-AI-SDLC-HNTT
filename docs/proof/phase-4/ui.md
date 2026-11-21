# Bằng chứng Phase 4 — Đóng gói + cảnh báo UI (Tú)

Ticket: [docs/phase4.md](../../phase4.md) mục 1.1 (benchmark), 1.2 (cảnh báo), 1.3 (clone sạch).

## 1. Benchmark có render — `bench_cmd`

```bash
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json
```

- **Cảnh đo:** gather lõi, scenario rỗng (cá bơi/sinh, Cá Sấu Năm Chèo, hiệu ứng mặc định), Út Sen đứng yên tại bến. Seed 42.
- **Khung vẽ:** canvas đúng **1280×720 px**, đã kiểm trong trang (`cv.clientWidth × clientHeight`). Lần đầu đo ra 1264×625 vì viền cửa sổ headless, đã sửa.
- **Làm nóng / đo:** 3 s / 30 s, bằng `requestAnimationFrame`. `load_ms` tính từ lúc lệnh khởi chạy tới khung hình đầu tiên của cảnh đo.

Kết quả ([bench.json](bench.json)): máy Windows 11, Edge headless, Python 3.11.

| Trường | Giá trị | Mục tiêu | Kết quả |
|---|---|---|---|
| `avg_fps` | 60.0 | ≥ 60 | đạt |
| `p1_low_fps` | 52.72 | ≥ 30 | đạt |
| `frames` | 1801 | | |
| `measured_s` | 30.016 | | |
| `load_ms` | 1669 | ≤ 10 000 | đạt |

**Chẩn đoán:** vẽ trung bình khoảng 2.5 ms/khung.

Lần đo đầu (trước tối ưu) chỉ đạt 46.9 FPS headless. Nguyên nhân: mỗi khung tạo hơn 80 gradient và dùng `shadowBlur` khi vẽ bằng CPU. Cách sửa:
- vẽ sẵn nền trời và nước vào canvas phụ;
- thay `shadowBlur` bằng bóng đổ giả;
- dùng màu đặc cho cá, lục bình và đá.

## 2. Cảnh báo dễ nhận biết + tương phản cao

| Cảnh báo | Chữ / biểu tượng | Thường | Tương phản cao |
|---|---|---|---|
| Thủy quái ở gần | banner "Thủy quái!" có ⚠, viền màn hình tím. Ở chế độ tương phản cao, Cá Sấu có thêm viền vàng | [warn_gather.png](warn_gather.png) | [warn_gather_hc.png](warn_gather_hc.png) |
| Oxy sắp hết | thanh oxy đỏ nhấp nháy dưới 25%, banner "Oxy sắp hết — quay lên!" có ⚠. Khi hết oxy thì "Hết hơi!" kèm đếm ngược | cùng ảnh trên | cùng ảnh trên |
| Khách sắp giận | banner "Khách bàn T2 sắp giận!" (còn N s) có ⚠, dấu giận đỏ và giọt mồ hôi trên đầu khách, thẻ đơn đỏ | [warn_quan.png](warn_quan.png) | [warn_quan_hc.png](warn_quan_hc.png) |

Tương phản cao bật/tắt bằng phím **`H`** hoặc `/?hc=1`, có nhớ lựa chọn trên máy. Ở chế độ này:
- HUD nền đen, viền trắng; chữ trắng; màu cảnh báo bão hòa;
- cảnh phía sau tối bớt.

Cả ba cảnh báo đều đã chụp ở chế độ này.

## 3. Clone sạch → chạy bản có giao diện trong 3 lệnh

Đã thử bằng `git clone` commit `bc56b44` vào một thư mục trống:
1. `git clone …`
2. `cd K5-L3B-LAB-Day12-AI-SDLC-HNTT`
3. `python -m chonoi.live --mode day`

Kết quả: trang chính trả HTTP 200, `/state` báo `phase: gather`, `day: 1`, không lỗi. `bench_cmd` chạy từ chính bản clone đó cũng ghi `bench.json` đủ 5 trường.

**Giới hạn:** máy thử là Windows (`python`). Trên macOS/Linux, README dùng `python3` với cùng các lệnh và chỉ cần thư viện chuẩn; nhóm chưa chạy trên máy macOS/Linux thật.

## Sửa thêm

`chonoi.live --mode day` trước đây không truyền `--days` vào `Session`, nên chỉ chơi được 1 Ngày và không tới màn Summary. Giờ mặc định 5 Ngày (trọn game).

Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests` cho 52/52 OK.
