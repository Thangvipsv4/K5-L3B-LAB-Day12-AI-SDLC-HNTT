# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Chơi ngay — 3 lệnh từ bản clone sạch (macOS / Linux)

```bash
git clone https://github.com/Thangvipsv4/K5-L3B-LAB-Day12-AI-SDLC-HNTT.git
cd K5-L3B-LAB-Day12-AI-SDLC-HNTT
python3 -m chonoi.live --mode day
```

Mở địa chỉ in ra (mặc định <http://127.0.0.1:8000/>), chọn **Chơi**. Một Ngày gồm: DayIntro → lặn (`gather`) → EveningIntro → quán (`quan`) → Kết quả → Shop.
Muốn chơi riêng một buổi thì thay `--mode day` bằng `--mode gather` hoặc `--mode quan`. Windows dùng `python` thay cho `python3`.

### Yêu cầu môi trường

| Cần | Ghi chú |
|---|---|
| **Python 3.10+** | Chỉ dùng thư viện chuẩn, không cần `pip install`. Nhóm chạy 3.11. |
| **Trình duyệt hiện đại** | Chrome, Edge, Firefox hoặc Safari để chơi. |
| **Chrome / Chromium / Edge** | Chỉ cần cho lệnh benchmark. Ở chỗ lạ thì đặt `CHONOI_BROWSER=<đường dẫn>`. |

### Điều khiển

| Phím | Buổi sáng (lặn) | Buổi tối (quán) | Màn khác |
|---|---|---|---|
| `W A S D` / mũi tên | bơi (S là lặn xuống) | đi lại | ↑ ↓ chọn ở menu |
| `E` | hái ở mặt nước, cập bến | nấu ở bếp, lấy món, bưng ra bàn | |
| `Space` | bắt cá (dưới nước) | | Enter/Space: xác nhận, qua intro |
| `Esc` / `P` | tạm dừng | tạm dừng | `M` ở màn tạm dừng: về menu |
| `1` / `2` / `Enter` | | | Shop: mua bình oxy / áo phao / đóng Shop |
| `H` | **tương phản cao** bật/tắt | như bên trái | như bên trái (có nhớ lựa chọn) |
| `R` / `L` | chơi lại / nhật ký sự kiện | như bên trái | |

### Cảnh báo và tương phản cao

- **Thủy quái ở gần:** banner "Thủy quái!" có biểu tượng ⚠, viền màn hình tím. Ở chế độ tương phản cao, Cá Sấu có thêm viền vàng.
- **Oxy sắp hết:** thanh oxy đỏ nhấp nháy khi dưới 25%, banner "Oxy sắp hết — quay lên!". Hết oxy thì hiện "Hết hơi!" kèm đếm ngược tới lần mất Máu kế tiếp.
- **Khách sắp giận:** khi kiên nhẫn dưới 25% thì hiện banner "Khách bàn … sắp giận!" (đếm giây), dấu giận đỏ và giọt mồ hôi trên đầu khách, thẻ đơn chuyển đỏ.
- **Tương phản cao** (phím `H` hoặc `/?hc=1`): HUD nền đen viền trắng, màu cảnh báo bão hòa, cảnh phía sau tối bớt. Bằng chứng: [docs/proof/phase-4/](docs/proof/phase-4/).

### Lệnh cho kiểm thử

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v                                   # toàn bộ test
python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out out.jsonl                 # headless (gather|quan|day)
python3 -m chonoi.headless --mode day --days 5 --seed 1 --ticks 120000 --out day.jsonl        # trọn 5 Ngày
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json                              # benchmark có render (bench_cmd)
```

- `bench_cmd` (`python3 -m chonoi.bench`) mở trình duyệt headless ở 1280×720 vào cảnh lặn seed 42, Út Sen đứng yên tại bến. Lệnh làm nóng 3 s, đo 30 s, rồi ghi `bench.json` gồm `avg_fps`, `p1_low_fps`, `frames`, `measured_s`, `load_ms`.
- Thêm `--show` để thấy cửa sổ khi đo.
- Lệnh soak (`soak_cmd`) được khai trong [`game.contract.json`](game.contract.json).

Khung Python trong `chonoi/` dựa trên starter, chi tiết ở [`docs/STARTER.md`](docs/STARTER.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.

## Sáng tạo của nhóm (HNTT)

> Mọi phần dưới đây chỉ nằm ở client trình duyệt (`chonoi/web/index.html`): **không đổi luật, không chạy ở headless**, nên không ảnh hưởng Test Contract.

| Phase | Sáng tạo | Ở đâu | Người |
|---|---|---|---|
| 1 | Thông báo sự kiện (toast) tiếng Việt có biểu tượng cho mọi event PRD (`dive`, `choke`, `faint`, `hold_full`, `paid`, `customer_left`…) | `index.html` → `EVENT_MSG`, `collectToasts`, `drawToasts` | Tú |
| 1 | Cảnh báo ngạt: viền đỏ nhấp nháy + đếm ngược tới lần mất Máu kế tiếp; nhắc khi oxy < 25% | `index.html` → `drawGather` | Tú |
| 1 | Bảng "Đơn gọi" buổi tối: tên món tiếng Việt, trạng thái đơn, thanh kiên nhẫn đổi màu xanh → cam → đỏ | `index.html` → `drawQuan` | Tú |
| 1 | Đồ họa chợ nổi: bình minh trên sông, rặng dừa nước, tia nắng, rong đáy, cá quẫy đuôi, hoa súng/điên điển, ghe ở bến, bọt nước khi lặn; tối là sàn ghe ván gỗ, dây đèn lồng, bếp cà ràng có lửa/hơi, khách đội nón lá với vòng kiên nhẫn | `index.html` → `drawGather`, `drawQuan` | Tú |
| 1 | HUD khung gỗ: tim, sao uy tín, xu tiền, ô giỏ có hình nguyên liệu, bảng Đơn gọi, phím tắt dạng keycap; `L` bật nhật ký sự kiện + id (cho QA) | `index.html` | Tú |
| 2 | Các màn Menu, DayIntro, EveningIntro, DayResult, Shop, Summary, Pause. Sim đứng yên (`/hold`) khi đang ở màn không chơi, nên không tiêu tick | `index.html`, `live.py` | Tú |
| 2 | Cá Sấu Năm Chèo vẽ tay (mắt đỏ khi đuổi), bảng "Má Tư dặn" đã lấy/cần, gợi ý hái/cập bến/bắt cá khi tới gần | `index.html` | Tú |
| 3 | HUD độ tươi: thanh tươi từng ô giỏ, hàng ươn gạch đỏ, kho theo độ tươi, giá tạm tính theo độ tươi trên thẻ đơn (đọc được cả kho đếm v1.1 lẫn kho cá thể v1.2) | `index.html` | Tú |
| 3 | Sông phù sa có sóng động, lục bình trôi, ghe chợ nổi có cây bẹo, nhà sàn/dừa/ghe neo trên bờ (thị sai), camera bám người chơi + minimap; quán nhà bè rộng, Út Sen đi có bước chân, khách ăn có đũa và tô bốc khói | `index.html` | Tú |
| 4 | Cảnh báo có biểu tượng ⚠ (thủy quái, oxy, khách sắp giận) + chế độ tương phản cao (`H`) | `index.html` | Tú |
