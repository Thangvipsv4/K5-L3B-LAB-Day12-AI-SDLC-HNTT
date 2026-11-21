# TICKET-02 — Một ngày ở chợ nổi (Phase 2)

> **Thông tin Phase 2**:
> - **Thời gian**: 55 phút (1:00–1:55) · Day 12 · AI SDLC
> - **Tiêu chuẩn**: Test Contract v1.1
> - **Mốc quan trọng**: Hạn đẩy tag `phase-2` lúc **1:55** (Phát hành: 10:19)

Hai buổi đã nối được. Khách hàng chốt số liệu chuẩn và muốn chơi trọn một vòng ngày:
- **Sáng**: Út Sen xem thực đơn để biết cần tìm nguyên liệu gì.
- **Tối**: Quán dùng phần mang về để phục vụ khách.
- **Cuối ngày**: Người chơi dùng tiền kiếm được mua nâng cấp trong Shop cho lần lặn sau.

---

## 1. Lõi (mọi nhóm) — Số liệu chuẩn

Thay số đã chọn ở Phase 1 bằng các giá trị dưới đây. Cập nhật cấu hình, spec và test cùng lúc. Tiền tính theo nghìn đồng, mô phỏng chạy **60 tick/s**.

### 1.1. Buổi sáng — Lặn & Hái

| Hằng số | Giá trị chuẩn |
| :--- | :--- |
| **Thời lượng** | 180 s (10.800 tick). |
| **Vùng nước** | $x \in [0, 100]$, $d \in [0, 30]$. Chặn ở các mép. Mặt nước ở $d \le 0.5$.<br>Các phân vùng: Nông ($d < 10$), Giữa ($10 \le d < 20$), Sâu ($d \ge 20$). |
| **Bến và xuất phát** | Bến tâm `[2, 0]`, bán kính 3 m. Xuất phát `[2, 0]`, hướng $0^\circ$ (`+x`). |
| **Bơi** | 4.0 m/s, đạt tốc độ hoặc dừng trong $\le 0.1$ s (6 tick). |
| **Oxy và ngạt** | • Cơ sở 30 s (1.800 tick). Dưới nước $-1$ oxy/tick, mặt nước $+6$/tick, kẹp ở mức tối đa.<br>• Ở dưới nước với oxy bằng 0: mất 1 Máu mỗi 60 tick, tính cả bước vừa chạm 0.<br>• Reset nhịp khi oxy $> 0$ hoặc lên mặt nước. Ngạt xuyên bất tử và không làm rơi hàng. |
| **Giỏ và hái** | 12 ô, mỗi nguyên liệu 1 ô. Hái ở mặt nước trong $\le 2.0$ m, lấy 1, mọc lại sau 20 s (1.200 tick). Xét bến trước nút hái. |
| **Nút hái** | • Bông điên điển: `N1` `[12, 0]`, `N2` `[28, 0]`<br>• Bông súng: `N3` `[44, 0]`, `N4` `[60, 0]`<br>• Kèo nèo: `N5` `[76, 0]`, `N6` `[90, 0]` |
| **Bắt cá** | Phím `catch` (`Space`), chỉ dưới nước, chọn đàn gần nhất trong $\le 2.0$ m, hòa theo id. Cần đủ chỗ cho cả đàn. Hồi 0.5 s (30 tick) tính từ lần bắt thành công.<br>• Sản lượng đàn (`yield`): cá linh 3, cá lóc 1, cá kèo 2. |
| **Đàn cá bơi** | • Tốc độ 1.5 m/s trong $x \in [4, 96]$.<br>• Vùng bơi theo độ sâu: Cá linh $d \in [3, 12]$, cá lóc $[8, 20]$, cá kèo $[22, 28]$.<br>• Đổi hướng theo seed ở bước bơi thứ 120, 240… trước khi di chuyển.<br>• Tới mép: Phản xạ phần quãng đường còn lại và đảo thành phần hướng vuông góc với mép (chạm góc đảo cả hai). |
| **Điểm sinh** | $x \in \{15, 30, 45, 60, 75, 90\}$.<br>• Độ sâu sinh: Cá linh $d \in \{5, 10\}$, cá lóc $\{10, 16\}$, cá kèo $\{24, 27\}$.<br>• Có 36 cặp loài–vị trí, trong đó có 30 vị trí hình học khác nhau. |
| **Sinh cá** | • Đầu ca có 8 đàn ở 8 điểm khác nhau, trần tối đa 12 đàn.<br>• Tại $\text{phase\_tick} = 360 \cdot k$ ($k \ge 1$): sau khi cá bơi, sinh tối đa một đàn nếu còn dưới trần và có điểm cách mọi đàn đang sống $> 1$ m. Bỏ lượt nếu hết điểm.<br>• Trọng số chọn loài: linh 40%, lóc 30%, kèo 30%, chuẩn hóa lại theo các loài còn điểm hợp lệ. Sau đó chọn đều một điểm của loài và lấy hướng ban đầu theo seed. Cá mới tham gia từ bước sau. |
| **Kết thúc** | • `docked`: Khi tương tác trong bán kính bến.<br>• `time`: Khi hết giờ ở bất kỳ độ sâu nào. Cả hai đều giữ phần còn trong giỏ.<br>• `fainted`: Khi Máu bằng 0, mất toàn bộ giỏ. |

---

### 1.2. Cá Sấu Năm Chèo, Máu và ngất
- **Khởi tạo & Tuần tra**:
  - Máu cơ sở 3, hồi đầy đầu mỗi Ngày. Cá Sấu hoạt động ở độ sâu $d \in [10, 30]$.
  - Quái `M1`: Tuần tra từ `[60, 24]` đến `[64, 24]`.
  - Quái `M2` (xuất hiện từ Ngày 3): Tuần tra từ `[85, 18]` đến `[89, 18]`.
  - Waypoint đầu tiên là vị trí xuất phát. Trong mode `gather` độc lập, dùng bố trí của Ngày 1.
- **Trạng thái di chuyển**:
  - `patrol`: Di chuyển 1.0 m/s tới waypoint đích, đổi sang waypoint kia cho bước sau khi đến nơi.
  - `chase`: Nếu người chơi ở $d \ge 10$ và khoảng cách $\le 10$ m, chuyển sang `chase` và bơi về phía người chơi với tốc độ 3.0 m/s.
  - Trở về `patrol`: Khi khoảng cách $> 16$ m hoặc người chơi trồi lên độ sâu $d < 10$. Chặn Cá Sấu theo biên map và dải độ sâu của loài.
- **Va chạm & Sát thương**:
  - Sau khi cả hai di chuyển: Nếu khoảng cách $\le 1.5$ m, người chơi ở $d \ge 10$ và đã hết thời gian bất tử:
    - Mất 1 Máu.
    - Rơi $\lfloor\text{số nguyên liệu đang mang} / 2\rfloor$ theo cơ chế LIFO (nhặt sau mất trước).
    - Nhận bất tử 90 tick (`invuln_ticks = 90`).
    - Mỗi bước tối đa nhận một hit (chọn con gần nhất, hòa theo id).
    - Trong thời gian bất tử: Không nhận hit và không làm Cá Sấu chuyển sang `recoil`.
- **Phản lực của Cá Sấu (`recoil`)**:
  - Con gây hit chuyển sang `recoil` trong 60 bước tính từ bước sau.
  - Lùi theo hướng ngược với người chơi đã chốt lúc chạm (nếu trùng tâm thì dùng vector `+x`), mỗi bước di chuyển $2/60$ m trước khi chặn mép và không gây hit trong thời gian này.
  - Hết 60 bước `recoil` thì trở về `patrol`, bắt đầu xét phát hiện / va chạm từ bước kế tiếp.
  - Khi Máu chạm 0: Ngất ngay lập tức (`faint`), buổi tối vẫn mở quán với kho bàn giao rỗng.

---

### 1.3. Buổi tối — Mở Quán

| Hằng số | Giá trị chuẩn |
| :--- | :--- |
| **Thời lượng** | 180 s (10.800 tick). |
| **Phòng / Xuất phát / Tốc độ** | $x \in [0, 16]$, $z \in [0, 10]$ / Xuất phát `[8, 5]` / Tốc độ đi 4.0 m/s, đạt tốc độ hoặc dừng trong $\le 6$ tick. Chặn biên và đi xuyên nội thất. |
| **Bếp** | `B1` `[2, 8]`, `B2` `[5, 8]`. |
| **Bàn** | `T1` `[9, 2]`, `T2` `[13, 2]`, `T3` `[9, 6]`, `T4` `[13, 6]`. |
| **Tương tác** | Bán kính $\le 1.5$ m. Chọn đối tượng gần nhất, hòa thì ưu tiên Bếp trước Bàn rồi đến id. Tay cầm tối đa 1 món. Bếp lấy đơn `reserved` cũ nhất theo `order_tick` rồi đến id bàn. |
| **Khách** | • Lượt đầu tiên tại tick 120, sau đó cứ mỗi $120 + 900 \cdot k$ ($k \ge 0$) nếu còn bàn trống.<br>• Đến ghế trống có id nhỏ nhất, giữ nguyên liệu ngay khi gọi món.<br>• Kiên nhẫn 60 s (3.600 tick), thời gian ăn 10 s (600 tick). |
| **Boa và uy tín** | • Tiền boa = $\lfloor\text{giá} \times 0.2\rfloor$ nếu thời gian kiên nhẫn còn lại $\ge 50\%$ ($\ge 30$ s) lúc giao món.<br>• Thu tiền boa dương: Uy tín $+0.2$. Uy tín khởi đầu game là 3.0, kẹp trong khoảng $[0, 5]$.<br>• Khách hết kiên nhẫn bỏ về trong ca làm giảm $0.5$ uy tín. |
| **Đóng ca** | Khách còn đang ăn được thanh toán ngay, khách còn đang chờ rời bàn mà không trừ uy tín. Dọn sạch món và phần giữ chỗ của đơn. Cấu hình `burn_s: null` trong phần lõi. |
| **Điểm số (`score`)** | $\text{score} = \text{earned} + 100 \times \lfloor\text{reputation}\rfloor$. Trong đó `earned` là tổng thu (gồm tiền món và tiền boa). |

#### Thực đơn (Menu)
Lưu công thức, thời gian nấu và giá dưới dạng dữ liệu. Hai nguyên liệu mới: `ca_keo` (cá kèo) và `keo_neo` (kèo nèo).

| ID món | Món | Công thức | Thời gian nấu | Giá bán |
| :--- | :--- | :--- | :---: | :---: |
| `ca_loc_nuong_trui` | Cá lóc nướng trui | `ca_loc` ×1 | 6 s | 60 |
| `goi_bong_sung` | Gỏi bông súng | `bong_sung` ×2 | 4 s | 40 |
| `lau_ca_linh_dien_dien` | Lẩu cá linh bông điên điển | `ca_linh` ×3 + `bong_dien_dien` ×1 | 10 s | 120 |
| `canh_chua_ca_loc` | Canh chua cá lóc bông điên điển | `ca_loc` ×1 + `bong_dien_dien` ×1 | 8 s | 90 |
| `ca_keo_nuong` | Cá kèo nướng muối ớt | `ca_keo` ×2 | 6 s | 70 |
| `lau_mam` | Lẩu mắm miền Tây | `ca_linh` ×2 + `ca_keo` ×1 + `keo_neo` ×1 + `bong_dien_dien` ×1 | 12 s | 200 |

---

## 2. Lõi — Vòng ngày, kế hoạch và Shop

### Vòng lặp ngày và kế hoạch
$$\text{DayIntro} \to \text{gather} \to \text{EveningIntro} \to \text{quan} \to \text{DayResult} \to \text{Shop} \to \text{DayIntro (hoặc tổng kết sau Ngày 5)}$$

- **Khởi đầu ngày**: Má Tư công bố món định nấu và tổng nguyên liệu cần lấy. HUD hiển thị tiến độ `đã lấy / cần`.
- **Chuyển tiếp**: Cập bến, hết giờ hoặc ngất xỉu $\to$ mở quán với kho bàn giao.
- **Lưu giữ trạng thái**: Tiền (`money`), tổng thu (`earned`), uy tín (`reputation`) và cấp nâng cấp được bảo lưu qua Ngày. Oxy và Máu hồi đầy theo cấp có hiệu lực. Giỏ làm mới và **kho dư bị hủy bỏ sau Shop**.
- **Cơ chế gọi món trong ngày (`day`)**:
  - Khách chọn ngẫu nhiên đều theo seed từ các món trong kế hoạch có đủ nguyên liệu (sau khi trừ phần đang giữ chỗ).
  - Số suất trong kế hoạch dùng để tính mục tiêu thu gom; khách vẫn có thể gọi tiếp món đủ nguyên liệu kể cả khi đã bán vượt chỉ tiêu.
  - Quán chạy riêng lẻ độc lập dùng cả 6 món.
  - Có bàn trống mà không đủ nguyên liệu nấu món nào $\to$ phát `no_dish`.
  - Không có thưởng riêng khi gom đủ danh sách.
- **Kết thúc ngày**: Ngày chỉ hoàn tất khi Shop đóng (kể cả Ngày cuối). Một Ngày không pause dài tối đa 22.200 tick. Shop có thể đóng sớm.

#### Kế hoạch thực đơn 5 Ngày
| Ngày | Món và số suất kế hoạch | Nguyên liệu cần | Số ô cần (thực tế nếu bắt theo đàn) |
| :---: | :--- | :--- | :---: |
| **D1** | `ca_loc_nuong_trui` ×3, `goi_bong_sung` ×3 | `ca_loc` ×3, `bong_sung` ×6 | 9 |
| **D2** | `ca_loc_nuong_trui` ×2, `lau_ca_linh_dien_dien` ×2 | `ca_loc` ×2, `ca_linh` ×6, `bong_dien_dien` ×2 | 10 |
| **D3** | `goi_bong_sung` ×2, `canh_chua_ca_loc` ×2, `ca_keo_nuong` ×2 | `bong_sung` ×4, `ca_loc` ×2, `bong_dien_dien` ×2, `ca_keo` ×4 | 12 |
| **D4** | `lau_mam` ×1, `ca_loc_nuong_trui` ×2, `goi_bong_sung` ×1 | `ca_linh` ×2, `ca_keo` ×1, `keo_neo` ×1, `bong_dien_dien` ×1, `ca_loc` ×2, `bong_sung` ×2 | 9 (11) |
| **D5** | `lau_mam` ×1, `lau_ca_linh_dien_dien` ×1, `ca_loc_nuong_trui` ×1 | `ca_linh` ×5, `ca_keo` ×1, `keo_neo` ×1, `bong_dien_dien` ×2, `ca_loc` ×1 | 10 (12) |

---

### Shop và nâng cấp

| ID nâng cấp | Loại nâng cấp | Cấp 1 | Cấp 2 |
| :--- | :--- | :--- | :--- |
| `oxygen` | Bình oxy | 200 $\to$ 45 s (2.700 tick) | 400 $\to$ 60 s (3.600 tick) |
| `hp` | Áo phao (thêm Máu) | 250 $\to$ 4 Máu | 500 $\to$ 5 Máu |

- Nâng cấp theo dữ liệu, mua cấp kế tiếp một lần mỗi cấp. Đủ đúng số tiền vẫn mua được.
- Trừ vào `money`, giữ nguyên `earned` và điểm số.
- Cấp vừa mua hiển thị ngay trên UI, nhưng **chỉ có hiệu lực từ Ngày kế tiếp**.
- Không đủ tiền hoặc đã đạt cấp tối đa $\to$ phát `buy_failed`, tiền và cấp giữ nguyên.
- Shop chờ phím `shop_done` hoặc tự động đóng sau 600 tick hoạt động.

---

### Menu, Pause và HUD
- **Hệ thống màn hình**:
  - `Menu chính`: Có nút Chơi và Thoát.
  - `DayIntro`: Hiện Ngày và danh sách món Má Tư yêu cầu (tự chuyển sau 4 s hoặc khi nhấn phím).
  - `EveningIntro`: Hiện số lượng nguyên liệu nhập kho và các món nấu được.
  - `DayResult`: Thống kê khách đã phục vụ / bỏ đi, tiền thu được, tiền boa và biến động uy tín.
  - `Summary`: Hiện tổng tiền, tổng điểm, uy tín cuối cùng và món bán chạy nhất.
- **Tạm dừng (Pause)**: Phím `Esc` hoặc `P`. Làm mờ nền, hiển thị Tiếp tục và Về menu (thêm Cài đặt nếu có mở rộng). Đóng băng toàn bộ đồng hồ và timer gameplay (kể cả trong Shop).
- **HUD Buổi sáng**: Máu, oxy (dưới 25% đổi màu/nhấp nháy), thời gian (đổi màu khi $\le 30$ s), độ sâu, giỏ phân loại, danh sách cần lấy và hồi chiêu bắt cá. Gợi ý hái/cập bến khi đến gần. Cảnh báo *“Thủy quái!”* kèm viền tím khi có quái lại gần và *“Hết hơi!”* khi cạn oxy.
- **HUD Buổi tối**: Đồng hồ ca, tiền ca, uy tín, trạng thái món và kiên nhẫn tại từng bàn (đổi màu khi $< 25\%$), tiến độ bếp / món chín, món đang cầm và kho khả dụng.
- **Chuẩn hiển thị**: Chữ không chân $\ge 18\text{ px}$ ở độ phân giải $1280 \times 720$. Headless một Ngày không pause ($\le 22.200$ tick) chạy $\le 20$ s. Chơi thường đạt $\ge 30\text{ FPS}$.

---

## 3. Mở rộng (Extensions)

> [!NOTE]
> Kỳ vọng tính cho cả buổi lab: Nhóm 4 người không bắt buộc, nhóm 5 người hoàn thành $\ge 1$ mục, nhóm 6 người hoàn thành $\ge 2$ mục. Hoàn thành lõi trước! Khai báo mã trong `extensions` tại gốc manifest.

| Mở rộng | Luật chi tiết |
| :--- | :--- |
| **Lao xua** (`weapon`) | • Phím `Q` (`attack`), cần mua cấp 1.<br>• Hồi 3 s (180 tick) từ lần dùng hợp lệ, kể cả không trúng.<br>• Cấp 1: Giá 300, bán kính 4 m, choáng 2 s.<br>• Cấp 2: Giá 600, bán kính 6 m, choáng 3 s.<br>• Duyệt mục tiêu theo id, đẩy mỗi con 3 m ra xa (chặn mép, trùng tâm dùng `+x`), choáng ghi đè recoil/choáng cũ.<br>• Đứng yên và không gây hit trong 120/180 bước (kể cả bước bị trúng Lao). Hết choáng về `patrol` tại vị trí sau đẩy. |
| **Vợt hút cá** (`net`) | • Cấp 1: Giá 250, bán kính 4.0 m, tối đa 2 đàn/lần.<br>• Cấp 2: Giá 500, bán kính 6.0 m, tối đa 3 đàn/lần.<br>• Từ cấp 1 duyệt theo id, đếm số đàn bắt thành công. Đàn thiếu chỗ phát `hold_full` và giữ lại, tiếp tục xét đàn kế tiếp.<br>• Có ít nhất một đàn bắt thành công mới đặt hồi chiêu. Cấp 0 dùng luật bắt cá gần nhất của lõi. |
| **Rắn Hổ Mây** (`snake`) | • Quái `M3` xuất hiện từ Ngày 1, tuần tra `[72, 14]` $\leftrightarrow$ `[76, 14]`, độ sâu $d \in [8, 20]$.<br>• Tốc độ: Patrol 1.0 m/s, Chase 3.5 m/s.<br>• Phát hiện khi $\le 8$ m, rời chase khi $> 16$ m hoặc người chơi lên $d < 8$.<br>• Áp dụng luật chạm / recoil chung và ngưỡng độ sâu của loài. |
| **Cháy món** (`burn`) | • Cấu hình `burn_s: 20`.<br>• Nếu `ready_ticks > 1200`: Bỏ món cháy, nguyên liệu mất, bếp trở về rảnh (`idle`) ngay.<br>• Tự động thử giữ lại nguyên liệu ngay cho đơn: Đủ thì `reserved`, thiếu thì chuyển `unfulfillable`, khách tiếp tục chờ đến hết kiên nhẫn. Đúng 1.200 tick vẫn bưng được. |
| **Chợ Chú Sáu** (`vendor`) | • Mua bán trong Shop: Bán cá lóc giá 20, cá linh 8, cá kèo 10; bông điên điển, bông súng, kèo nèo giá 5.<br>• Giá mua = $\lfloor\text{giá bán} \times 1.5\rfloor$, lượng hàng bán cho người chơi không giới hạn. Mỗi lệnh thực hiện 1 đơn vị.<br>• Tiền bán cộng vào `money` và `earned`. Hàng mua được nhập thẳng vào kho quán tối Ngày kế tiếp, tách riêng khỏi `gather_end.inventory`. |
| **Sổ tay & Cá Hô** (`ca_ho`) | • Một con `H1`, tốc độ 1.0 m/s. Chọn vị trí từ các điểm sinh chuẩn $d \ge 10$ theo seed.<br>• Bơi trong $x \in [4, 96]$, $d \in [10, 30]$, phản xạ mép như cá thường.<br>• Cạnh bắt hợp lệ trúng Cá Hô phát sự kiện `released` sau event bắt cá thường, không thêm hàng vào giỏ và không tự kích hoạt hồi chiêu.<br>• Phím `F` (`photo`) trong $\le 6$ m cộng 0.5 uy tín (tối đa 1 lần/Ngày). Sổ tay ghi lại 8 loài đã gặp. |
| **Settings & Âm thanh** | Âm lượng Master / Music / SFX được lưu trữ bền vững giữa các phiên mở game. |

---

## 4. Test Contract v1.1 — Thay đổi từ v1.0

### 4.1. CLI và Manifest

```bash
<headless_cmd> --mode gather|quan|day --seed <int> \
  [--scenario <file.json>] [--inputs <file.json>] \
  [--inventory <file.json>] [--inventory-out <file.json>] \
  [--days <N>] --ticks <N> --out <file.jsonl> [--snapshot-every <N>]
```

- `--days`: Chỉ dùng với mode `day`, số nguyên từ 1 đến 5 (mặc định 1).
- Mode `day` tự động bàn giao kho theo schema v1.0 (có thể truyền thẳng trong bộ nhớ).
- Cờ `--inventory` và `--inventory-out` vẫn dùng riêng cho hai mode độc lập `gather` và `quan`.
- Đặt `"contract_version": "1.1"` trong `game.contract.json`.

#### Các khóa bổ sung / cập nhật trong Manifest:
| Phạm vi | Khóa cấu hình |
| :--- | :--- |
| `gather` | • `fish_initial`: đổi thành số nguyên `8`.<br>• Bổ sung: `fish_speed`, `fish_turn_ticks`, `fish_max`, `fish_spawn_ticks`, `fish_spawn_clearance`, `fish_x`, `fish_depths`, `fish_spawn_x`, `fish_spawn_depths`, `fish_weights`.<br>• Các map theo loài và `fish_yield` có đủ 3 loài (thêm `ca_keo`).<br>• Thêm nút hái `N5`, `N6`. |
| `gather.monsters` | • `species.ca_sau`: `{patrol_speed, chase_speed, detect_radius, exit_radius, depths, hit_radius, recoil_ticks, recoil_dist}`.<br>• `spawns[]`: `{id, kind, pos, waypoints, from_day}`.<br>• Cấu hình chung: `invuln_ticks: 90`, `loss_ratio: 0.5`. |
| `quan`, `menu` | Thêm bếp `B2`, bàn `T2`–`T4` và 3 món mới (`canh_chua_ca_loc`, `ca_keo_nuong`, `lau_mam`). |
| `day_plan` | Mảng 5 object `{day, dishes, ingredients}`. Trong đó `dishes` và `ingredients` là map `id` $\to$ số nguyên dương. Tính `ingredients` bằng tổng công thức nhân số suất. |
| `shop` | `{max_ticks, upgrades}`.<br>• `upgrades.oxygen[]`: `{level, price, oxygen_max_s}`.<br>• `upgrades.hp[]`: `{level, price, hp_max}`. |
| **Mở rộng** | • `weapon`: `gather.weapon_cooldown_s`, `shop.upgrades.weapon[]` `{level, price, weapon_radius, stun_s}`.<br>• `net`: `shop.upgrades.net[]` `{level, price, catch_radius, max_schools}`.<br>• `snake`: `gather.monsters.species.ran` cùng schema loài, thêm `M3` vào `spawns`.<br>• `burn`: `quan.burn_s` hữu hạn.<br>• `vendor`: `shop.vendor` `{buy_multiplier, sell_prices}`.<br>• `ca_ho`: `gather.ca_ho` `{count, speed, depths, photo_radius, reputation_bonus, bonus_per_day}`. |

---

### 4.2. Inputs và Pause
- **Nút boolean mới**:
  - `pause`: Hoạt động ở cả ba mode.
  - `shop_done`: Dùng trong Shop để đóng sớm.
  - `attack` và `photo`: Dùng trong `gather` khi bật mở rộng tương ứng.
  - Chỉ tác động ở **cạnh lên**. Giữ nút qua đổi pha không tạo cạnh mới.
- **Trường `buy`**:
  - Chuỗi khác rỗng, chỉ thực thi tại frame khai báo.
  - Nhận giá trị: `"oxygen"`, `"hp"` hoặc các mở rộng `"weapon"`, `"net"`, `"buy:<kind>"`, `"sell:<kind>"`.
  - Shop phát `buy_failed` nếu gặp lệnh không hỗ trợ hoặc không đủ điều kiện.
  - Nút đúng kiểu nhưng sai pha hoặc mở rộng chưa bật sẽ bị bỏ qua.
- **Cơ chế Pause**:
  - Xét cạnh `pause` trước tiên.
  - Bước vào pause: Chỉ tăng tick ngoài, cập nhật chốt và phát sự kiện `paused`.
  - Khi đang pause: Bỏ qua toàn bộ cạnh hành động và lệnh `buy`. Các biến `sim_tick`, `phase_tick`, lịch và mọi timer đứng yên.
  - Cạnh lên tiếp theo của `pause`: Phát sự kiện `resumed`, tiếp tục chạy gameplay ngay trong bước đó.

---

### 4.3. Scenario

- Mode `day` nhận `gather` và `quan` làm mẫu khởi tạo mỗi Ngày.
- Khối `day`: `{money, earned, reputation, upgrades, day_plan}` dựng trạng thái xuyên Ngày (mặc định tiền và earned = 0, uy tín theo tuning, cấp là `{}` và kế hoạch theo preset). Yêu cầu $0 \le \text{money} \le \text{earned}$.
- `day.day_plan`: Ghi đè kế hoạch theo số Ngày.
- **Ràng buộc**:
  - Cấm khai `quan.stock` và `quan.reputation` khi chạy mode `day`. Dùng `gather.hold` để dựng hàng.
  - Kho, khách, bếp và món thuộc kế hoạch được kiểm tra trên kho thực lúc mở quán $\to$ mâu thuẫn trả về **mã lỗi 2**.
  - `gather.player`: Bổ sung `invuln_ticks` và `attack_cd_ticks` (nếu bật Lao).
  - `gather.fish[]`: Bổ sung `age_ticks` (mặc định 0 - số bước cá đã tham gia bơi). Cờ `random_fish: false` tắt cá mặc định, cá bơi và sinh cá.
  - `gather.monsters[]`: Danh sách quái `{id, kind, pos, waypoints, target_idx, state, state_ticks_left, recoil_dir}` (2 waypoint, `target_idx` 0 hoặc 1, `state` mặc định `patrol`, `recoil_dir` là vector đơn vị khi recoil, timer phải dương khi recoil/stunned).
  - Mở rộng: `gather.ca_ho` (`{id, pos, heading_deg, photographed}`), `quan.stoves[].ready_ticks`.

#### Ví dụ Scenario khởi đầu Ngày có sẵn tiền và kho:
```json
{
  "day": {"money": 200, "earned": 200},
  "gather": {
    "hold": ["ca_loc", "bong_sung", "bong_sung"],
    "random_fish": false
  }
}
```

---

### 4.4. Output JSONL

- Snapshot bổ sung: `state: "paused"`.
- Mode `gather` bổ sung trong snapshot: `monsters[]`, `player.invuln_ticks`, `player.attack_cd_ticks`, `ca_ho`.
- Mode `day`: Mọi snapshot đều có `day`, `day_plan`, `upgrades`, `active_upgrades` (cấp đang áp dụng). `phase` là `"gather"`, `"quan"` hoặc `"shop"`. Snapshot Shop có `stock` dư và `time_left_ticks` tới khi đóng.
- Snapshot đổi pha: Ghi pha mới với `phase_tick: 0`. Event kết thúc mang tên pha cũ.
- Vỏ event ở mode `day` có thêm trường `"day": <int>`.

| Tên Event (`name`) | Dữ liệu chi tiết (`data`) |
| :--- | :--- |
| `monster_hit` | `monster_id`, `hp`, `lost`, `pos` (vị trí người chơi, `lost` là mảng kind theo LIFO). |
| `fish_spawned` | `id`, `kind`, `pos` (khi sinh cá theo lịch). |
| `faint` | Bổ sung `cause: "monster"` nếu do va chạm quái, `lost` liệt kê phần giỏ còn lại, `hp: 0`. |
| `day_start`, `phase_start` | `{}`. |
| `day_plan` | `dishes`, `ingredients` của Ngày tương ứng. |
| `paused`, `resumed` | `{}`. |
| `bought` | `upgrade`, `level`, `price`, `money`. |
| `buy_failed` | `action`, `reason` (`funds` / `max_level` / `out_of_stock` / `unknown`). |
| `shop_end` | `reason` (`done` / `time`). |
| `attack`, `monster_stunned` *(Lao)* | `pos`, `monster_ids` (theo id) / `monster_id`, `pos`, `stun_ticks` sau đẩy. |
| `photo`, `released` *(Sổ tay)* | `id`, `reputation` sau khi cộng / `id`. |
| `dish_burnt` *(Cháy món)* | `stove_id`, `order_id`, `dish_id`, `order_status` sau xử lý. |
| `vendor_trade` *(Chợ)* | `action` (`buy`/`sell`), `kind`, `price`, `money`. |

#### Ví dụ Event `day_plan`:
```json
{"type": "event", "tick": 0, "phase": "gather", "day": 1, "name": "day_plan", "data": {"dishes": {"ca_loc_nuong_trui": 3, "goi_bong_sung": 3}, "ingredients": {"ca_loc": 3, "bong_sung": 6}}}
```

- Dòng `end` của mode `day` có thêm `days_completed` (số Shop đã đóng).
- Hoàn thành đủ số Ngày khai báo thì dòng end có `reason: "days_complete"`.

---

### 4.5. Thứ tự xử lý bổ sung

1. **Buổi sáng (Gather)**:
   - Đồng hồ, cooldown, giảm bất tử (`invuln_ticks`) và hồi nút $\to$
   - Bơi, oxy, ngạt thở $\to$
   - Kích hoạt Lao (nếu có), cập nhật quái theo id rồi xét tối đa một va chạm `monster_hit` $\to$
   - Tương tác (xét bến trước hái) $\to$
   - Bắt cá theo vị trí trước khi cá bơi, chụp ảnh (nếu có) $\to$
   - Xét hết giờ ca.
   - *Nếu ca còn giờ*: Cá bơi, sinh cá mới theo lịch, cập nhật Cá Hô (nếu bật).
   - *Quy tắc Máu về 0*: Xử lý `faint` rồi `gather_end(fainted)` ngay sau `choke` hoặc `monster_hit`, bỏ toàn bộ các bước còn lại. Tại cùng tick, ngạt đi trước hit quái rồi mới xét hết giờ. Cập bến luôn ưu tiên trước bắt cá và hết giờ nếu còn Máu.
2. **Buổi tối (Quán)**:
   - Giữ nguyên thứ tự v1.0. Nếu bật cháy món: Xét món chín/cháy theo id bếp trước di chuyển và tương tác.
   - Trong mode `day`: Lọc menu theo danh sách id món trong kế hoạch trước khi lọc món đủ nguyên liệu khả dụng.
3. **Chuyển đổi pha**:
   - $\text{day\_start} \to \text{day\_plan} \to \text{phase\_start(gather)}$.
   - Sau `gather_end`: Dựng quán và phát `phase_start(quan)` ngay trong cùng tick (kể cả khi bị ngất).
   - Sau `quan_end`: Dựng Shop và phát `phase_start(shop)` ngay trong cùng tick.
   - Pha mới chỉ bắt đầu chạy gameplay từ bước (tick) tiếp theo.
4. **Shop**:
   - Xử lý một lệnh `buy` trước khi xét cạnh `shop_done` (kể cả ở bước cuối).
   - Đóng bằng phím ở bước cuối: phát `shop_end(done)`.
   - Hết 600 tick: tự đóng và phát `shop_end(time)`.
   - Đóng Shop: Tăng `days_completed`, kết thúc lượt hoặc dựng Ngày kế tiếp ngay tại tick đó.
   - **Chỉ khi dựng Ngày mới mới sao chép cấp đã mua sang `active_upgrades`**.

---

## 5. Quy trình nhóm và lịch gợi ý (55 phút)

Nhóm tự chọn cách phối hợp và cùng commit vào fork chung bằng tài khoản GitHub của từng người. 
- **4 Lát làm song song**:
  1. *Lát 1*: Số liệu chuẩn và cá bơi / sinh cá.
  2. *Lát 2*: Cá Sấu Năm Chèo, Máu và ngất do quái.
  3. *Lát 3*: 2 bếp / 4 bàn, 6 món ăn và kế hoạch ngày (`day_plan`).
  4. *Lát 4*: Mode `day`, Shop, cơ chế Pause, hệ thống Menu và HUD.
- Khuyến khích dùng fixture cố định để người làm mode `day` tích hợp sớm với 2 buổi đã có. Ghi `Co-authored-by:` khi pair commit.

| Phút trong phase | Công việc trọng tâm |
| :---: | :--- |
| **0–5** | Lên lại kế hoạch. So số chuẩn với giả định cũ, chốt giao diện chuyển pha, chia việc và phân phụ thuộc theo AC-P2-xx. |
| **5–20** | Build và kiểm thử 4 lát, cập nhật hợp đồng v1.1 và cấu hình/dữ liệu chuẩn. Chuẩn bị ca smoke test. |
| **20** | **Mốc kiểm soát**: Chạy smoke tích hợp luồng `gather --inventory-out` $\to$ `quan --inventory`. Đối chiếu snapshot kho ở tick 0 và lưu vào `docs/proof/phase-2/integration.*`. Standup 2–3 phút, điều phối người hỗ trợ lát chậm. |
| **20–35** | Build tiếp, phối hợp giữa các lát và chốt hoàn thiện luồng mode `day`. |
| **35–45** | Chạy smoke `day --days 1`, chạy nhiều Ngày để kiểm tra cấp nâng cấp và chạy regression test P1 với số chuẩn. Lưu bằng chứng, hoàn thiện `docs/verification/phase-2.md` và chuẩn bị gắn tag. |
| **45–50** | Retro nhanh: Ghi nhận điều tốt, điều vướng và 1 hành động cải tiến vào `docs/retro.md`. |
| **50–55** | Dự phòng. Đẩy tag `phase-2` chậm nhất lúc **1:55**. |

> [!IMPORTANT]
> Ghi rõ lý do nếu test cũ cần cập nhật do luật mới. Trong `docs/verification/phase-2.md`, nối từng AC với bằng chứng thực tế trên commit bàn giao. Cập nhật `docs/clarify.md` và `docs/ai-usage-log.md`.

---

## Định nghĩa hoàn thành (DoD)

- [ ] `contract_version: "1.1"`, tuning chuẩn hóa, đủ 6 nguyên liệu và 6 món ăn theo dữ liệu. Cá bơi / sinh cá, Cá Sấu, Máu / ngất, 2 bếp / 4 bàn hoạt động chuẩn xác.
- [ ] Chơi trọn vẹn vòng ngày với Menu, Pause và HUD. Chế độ `--mode day` công bố đúng kế hoạch D1–D5, chốt Ngày khi Shop đóng và áp dụng đúng cấp oxy/máu từ Ngày kế tiếp.
- [ ] Smoke tích hợp có bằng chứng lưu trữ. Regression P1 đạt với số chuẩn (test thay đổi có ghi lý do). `docs/verification/phase-2.md` và bằng chứng khớp với commit gắn tag.
- [ ] Công việc của các lát được tích hợp đầy đủ trên nhánh chính của fork chung, có bằng chứng commit của từng thành viên. Đã cập nhật `docs/clarify.md`, `docs/ai-usage-log.md` và `docs/retro.md`.
- [ ] Nếu có làm phần mở rộng, `README.md` phải khai báo mục đã làm kèm bộ test / bằng chứng tương ứng.
- [ ] Đẩy tag `phase-2` trỏ tới commit bàn giao trên nhánh `main` chậm nhất lúc **1:55**.
