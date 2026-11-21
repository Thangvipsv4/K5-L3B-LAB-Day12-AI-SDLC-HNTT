# PRD-0 — Quán Ăn Chợ Nổi (Phase 1)

> **Thông tin Phase 1**:
> - **Thời gian**: Day 12 · AI SDLC · Nhóm 4–6 người · 60 phút (0:00–1:00)
> - **Tiêu chuẩn**: Test Contract v1.0
> - **Mốc quan trọng**: Hạn đẩy tag `phase-1` lúc **1:00** (Phát hành: 08:02)

---

## 1. Chúng tôi muốn gì

**Quán Ăn Chợ Nổi** là game quản lý quán ăn mang bản sắc miền Tây Nam Bộ. Người chơi vào vai **Út Sen**, cô bé ở chợ nổi Rạch Sen. Khi Má Tư đau lưng, Út Sen lặn bắt cá và hái rau trên sông Chín Khúc vào buổi sáng. Tối đến, em nấu và phục vụ khách trên nhà bè của Má Tư. Những gì mang về quyết định quán có thể bán món nào.

### Tự do sáng tạo
- Ngoài yêu cầu của PRD và Test Contract, nhóm được tự do thêm nhân vật, loài cá hoặc cây, sinh vật mới, món ăn, khu vực, cơ chế nhỏ, sự kiện, câu chuyện, đồ họa, âm nhạc hoặc giao diện theo ý mình.
- **Giữ đúng luật lõi, số chuẩn và Test Contract**: Tắt phần tự thêm ở headless hoặc bảo đảm nó không đổi tick, sự kiện, tiền, uy tín và snapshot theo contract khi chạy test.
- Ghi ý tưởng đã làm vào mục *“Sáng tạo của nhóm”* trong `README.md`, kèm bằng chứng ngắn cho thấy lõi vẫn đúng.
- **Làm lõi đúng trước, sáng tạo sau**: Ưu tiên một ý tưởng gọn, chạy ổn và hoàn thiện. Điểm sáng tạo nằm ở hạng mục chất lượng sản phẩm, độ phức tạp không được cộng điểm.

---

## 2. Phạm vi Phase 1

### Lõi (mọi nhóm)
- **Buổi sáng (`gather`)**:
  - Bơi trong mặt cắt 2D của sông, theo chiều ngang và độ sâu `[x, d]`.
  - Út Sen tiêu oxy dưới nước, hồi oxy khi nổi lên và có 3 Máu, chỉ mất do ngạt.
  - Hái tại nút trên mặt nước (`interact`) và dùng nút bắt cá (`catch`) khi lặn.
  - Bản mặc định có 6 đàn cá đứng yên. Giỏ có sức chứa giới hạn.
  - Cập bến hoặc hết giờ thì bàn giao phần còn trong giỏ qua file kho.
  - Ngất thì kết thúc buổi sáng với kho rỗng.
- **Buổi tối (`quan`)**:
  - Quán có 1 bếp `B1`, 1 bàn `T1` và 3 món.
  - Khách chọn món nấu được với kho khả dụng và giữ chỗ nguyên liệu khi gọi.
  - Người chơi nấu → bưng → phục vụ trước khi khách hết kiên nhẫn.
  - Khách ăn xong trả tiền, có thể boa. Khách hết kiên nhẫn làm giảm uy tín.
- **Tích hợp & Điều khiển**:
  - Hai buổi chơi được riêng và nối nhau qua hai tiến trình headless dùng chung file kho.
  - Điều khiển gợi ý: `WASD` hoặc phím mũi tên để bơi/đi, `E` để tương tác (`interact`), `Space` để bắt cá (`catch`).
  - **HUD tối thiểu**:
    - *Buổi sáng*: thời gian, oxy, Máu, giỏ.
    - *Buổi tối*: kho khả dụng, món gọi, kiên nhẫn, trạng thái bếp, món trên tay, tiền và uy tín.

### Mở rộng
> [!NOTE]
> Kỳ vọng mở rộng tính cho cả buổi lab:
> - **Nhóm 4 người**: Không bắt buộc.
> - **Nhóm 5 người**: Hoàn thành ít nhất 1 mục.
> - **Nhóm 6 người**: Hoàn thành ít nhất 2 mục.

---

## 3. Cảm giác và phong cách
- **Bối cảnh & Visual**: Sông nước màu phù sa, bờ dừa nước, nhà sàn và ánh hồng buổi sớm. Tối có đèn dây vàng và khói bếp.
- **Tạo hình**: Út Sen mặc áo bà ba, buộc khăn rằn, đeo kính lặn tự chế và giỏ lưới.
- **Góc nhìn camera**:
  - Cảnh lặn: Mặt cắt nhìn ngang (side-view `[x, d]`).
  - Nhà bè: Góc nhìn từ trên xuống (top-down `[x, z]`).
  - Có thể bắt đầu bằng hình khối 2D.
- **Âm thanh & Văn hóa**: Giọng Nam Bộ trong thoại được khuyến khích. Tôn trọng văn hóa địa phương, dùng tài sản có quyền sử dụng và ghi nguồn trong `CREDITS.md`.

---

## 4. Công nghệ và cách vào lab
- **Lựa chọn công nghệ**: Starter Python là một lựa chọn. Nhóm được chọn ngôn ngữ, engine và thư viện. Nếu đổi công nghệ, cập nhật `build_cmd`, `run_cmd` và `headless_cmd` để giữ đúng Test Contract. Smoke test chạy hộp đen qua `headless_cmd`.
- **Khởi tạo repository**:
  1. Trưởng nhóm fork `VinUni-AI20k/K5-L3B-LAB-Day12-AI-SDLC` về tài khoản của mình, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`.
  2. Mời các thành viên làm collaborator với quyền **Write** trong *Settings → Collaborators*.
  3. Để repo public cho giảng viên xem, không cần mời giảng viên.
  4. Điền `TEAM.md` trong fork chung và đặt `team_size` trong `game.contract.json` khớp số thành viên thực tế.
  5. Nhóm có thể bật GitHub Actions hoặc dùng ruleset nếu phù hợp với cách làm đã chọn.

---

## 5. Nguyên liệu và món

### Bảng nguyên liệu
| ID nguyên liệu | Tên |
| :--- | :--- |
| `ca_loc` | Cá lóc |
| `ca_linh` | Cá linh |
| `bong_dien_dien` | Bông điên điển |
| `bong_sung` | Bông súng |

### Bảng thực đơn món ăn
| ID món | Món | Công thức |
| :--- | :--- | :--- |
| `ca_loc_nuong_trui` | Cá lóc nướng trui | `ca_loc` ×1 |
| `goi_bong_sung` | Gỏi bông súng | `bong_sung` ×2 |
| `lau_ca_linh_dien_dien` | Lẩu cá linh bông điên điển | `ca_linh` ×3 + `bong_dien_dien` ×1 |

> [!TIP]
> Dùng preset mẫu hoặc chọn giá, thời gian nấu và các số cho phép ở mục A. Khai đúng các giá trị đang chạy trong `tuning`.

---

## 6. Cách làm việc nhóm
- Quy trình kỹ thuật do nhóm tự chọn: Có thể push thẳng, dùng nhánh và Pull Request (PR), pair/mob hoặc review trực tiếp. Cả nhóm phải chia việc, phối hợp và tích hợp giữa các module trong một fork chung.
- Mỗi người có commit gắn với tài khoản GitHub của mình, **tối thiểu 3 commit có nội dung** trong cả buổi lab; commit của người không có trong `TEAM.md` không được tính. Khi làm chung một commit, ghi `Co-authored-by:` cho người cùng làm.
- Nên dùng các thực hành phù hợp với nhóm, như CI/CD, PR có review và approval, bảo vệ nhánh, ruleset, issue/board, CODEOWNERS, ADR hoặc template. Ví dụ: nhóm có thể ghi hợp đồng ở `docs/contracts/` và nhờ hai người duyệt PR đổi schema. Các cách này đều tùy chọn, không bị trừ điểm nếu chọn cách khác. Thực hành hiệu quả được cộng ở hạng mục thực hành kỹ thuật.

### 6.1. Kickoff và planning trong 15 phút đầu
- Chia bốn lát ở mục 6.2 và ghi vào `TEAM.md` tên, GitHub handle, module chính và vai của từng người (có thể kiêm vai):
  - **PO**: Hỏi Anh Năm hàng xóm (trợ giảng AI ở tab Phase 1 của lab board; anh là khách hàng, trả lời ngắn các chỗ PRD chưa nói rõ) hoặc giảng viên.
  - **Integrator**: Điều phối tích hợp và gắn tag.
  - **QA lead**: Giữ bộ test và ma trận truy vết.
  - **Scrum / Release**: Theo dõi mốc bàn giao.
- Chốt thỏa thuận nhóm ngắn trong `TEAM.md`: Kênh liên lạc, giờ standup, cách biểu quyết khi bất đồng và việc cần làm khi có người trễ hoặc vướng (gợi ý: trao đổi trong 2 phút trước khi nhờ người đã thống nhất chốt, hoặc báo kênh nhóm khi vướng quá 10 phút để có người hỗ trợ).
- Chốt sớm hợp đồng file kho giữa `gather` và `quan` theo mục G. Ghi schema và một ví dụ kho hợp lệ trong `README.md` hoặc một file ở `docs/contracts/`.
- Chốt các sự kiện và giao diện giữa mô phỏng và UI, như `sim/*` – `client/ui` (trạng thái đọc được, lệnh gửi vào). Bắt đầu các lát song song sau khi thống nhất, dùng kho mẫu để làm quán.
- Quản lý backlog: Checklist, issue/board hoặc `docs/plan/phase-1.md` (ghi đầu việc, AC-P1-xx, người làm và phần phụ thuộc).

### 6.2. Bốn lát làm song song
| Lát | Phạm vi |
| :---: | :--- |
| **1** | Bơi, oxy, chặn biên, giỏ. |
| **2** | Hái, bắt cá, cập bến, ghi file kho. |
| **3** | Khách, giữ chỗ nguyên liệu, kiên nhẫn. |
| **4** | Bếp, bưng, phục vụ, tiền. |

> [!NOTE]
> - Nhóm 4 người có thể giao mỗi người một lát. Người thêm ở nhóm 5–6 có thể lo HUD, QA hoặc hỗ trợ lát đang chậm.
> - Gợi ý review chéo giữa các lát, đổi vai người lái và người dẫn đường khi pair/mob.
> - **Phút 20 của mỗi phase**: Nên rà lát đang vướng và điều người đã xong sang hỗ trợ.
> - **Standup** có thể gói trong 2–3 phút với ba ý: đã xong, sắp làm và đang vướng.

### 6.3. Kiểm chứng và ghi chép
- Mỗi phase chạy kiểm chứng trên commit bàn giao ở `main` và đẩy tag `phase-n` đúng hạn.
- Ghi `docs/verification/phase-n.md` theo cấu trúc: `AC` → `bằng chứng` → `kết quả đạt/chưa đạt`, kèm cách kiểm chứng.
- Ở Phase 1: Lưu kết quả thật trong `docs/proof/phase-1/` và dẫn từ `docs/verification/phase-1.md`.
- Chỗ nào PRD mơ hồ thì hỏi Anh Năm hàng xóm trên lab board trước; anh không trả lời được thì nhóm tự đặt giả định. Ghi câu hỏi, trả lời và quyết định trong `docs/clarify.md`.
- Cập nhật `docs/ai-usage-log.md` theo người và phase, kèm token/chi phí nếu đo được.
- Ghi retro trong `docs/retro.md` và phản tư của mỗi người trong `docs/members/<handle>.md`.
- Đánh giá cá nhân dựa trên bằng chứng trong repo chung (commit của từng người, phần mình làm, việc giúp người khác), phản tư cá nhân và đánh giá chéo. Số PR và lượt review không dùng để chấm cá nhân.

### 6.4. Lịch gợi ý (60 phút)
| Phút trong phase | Công việc |
| :---: | :--- |
| **0–15** | Vào fork, chia vai, ghi `TEAM.md`, chốt hợp đồng kho và bắt đầu các lát song song. |
| **15–45** | Build và phối hợp các lát. Rà hỗ trợ ở phút 20, thử xuất file kho thật trước phút 25, standup giữa phase. |
| **45–55** | Chạy smoke hai tiến trình và chơi thử trên `main`. Hoàn thiện ma trận truy vết và gắn tag. |
| **55–60** | Dự phòng. Đẩy tag `phase-1` chậm nhất **1:00**. |

---

## 7. Định nghĩa hoàn thành (DoD)
- [ ] Chơi được cả hai buổi, đúng phạm vi lõi. HUD đọc được trong lúc chơi.
- [ ] `game.contract.json` khớp bản chạy và đầy đủ Test Contract v1.0. Smoke hai tiến trình trên `main` cho thấy quán nhận đúng file kho.
- [ ] `README.md` ghi cách chạy từ clone sạch trong tối đa 3 lệnh trên macOS hoặc Linux, điều khiển, cách tính điểm và lệnh test.
- [ ] Test của nhóm chạy được bằng 1 lệnh.
- [ ] Fork chung có đủ collaborator và commit gắn với tài khoản GitHub của từng người.
- [ ] `TEAM.md` có danh sách và thỏa thuận nhóm. `team_size` khớp danh sách.
- [ ] Hợp đồng kho đã thống nhất, có schema và ví dụ hợp lệ trong `README.md` hoặc `docs/contracts/`.
- [ ] Có `docs/verification/phase-1.md` và bằng chứng chạy ở commit gắn tag. Đã cập nhật ghi chép tối thiểu ở mục 6.3.
- [ ] Nếu có phần tự sáng tạo, mục *“Sáng tạo của nhóm”* trong `README.md` có bằng chứng lõi vẫn đúng.
- [ ] Đẩy tag `phase-1` trỏ tới commit bàn giao trên `main` chậm nhất **1:00**.

---

# Test Contract v1.0 (Bắt buộc)

Headless chạy logic ở **60 tick/s**, độc lập với cửa sổ, GPU và tốc độ render.
- **Đơn vị vị trí**: Mét (m).
- **Hệ tọa độ `gather`**: `[x, d]` với `x` hướng đông, `d` tăng xuống dưới, hướng `0°` là `+x` và `90°` là chúc xuống.
- **Hệ tọa độ `quan`**: `[x, z]` với `z` hướng bắc.

---

## A. File `game.contract.json` ở gốc repo

Các khóa trong preset v1.0 dưới đây đều bắt buộc. Có thể dùng nguyên bộ số mẫu.
- `team`: Mã nhóm.
- `team_size`: Số thành viên thực tế.
- `headless_cmd`: Nhận các cờ ở mục B.
- `run_cmd`: Mở game.
- `build_cmd`: Chuẩn bị bản chạy.
- Quy đổi thời gian có hậu tố `_s` sang số tick nguyên ở 60 Hz (`ticks = s * 60`).
- Tiền lưu bằng số nguyên, đơn vị: nghìn đồng.

```json
{
  "contract_version": "1.0",
  "team": "cho-noi-01",
  "team_size": 4,
  "headless_cmd": "./game headless",
  "run_cmd": "./game",
  "build_cmd": "./build",
  "tuning": {
    "tick_hz": 60,
    "gather": {
      "duration_s": 180,
      "bounds": {"x":[0,100],"d":[0,30]},
      "dock_pos": [2,0],
      "dock_radius": 3,
      "start_pos": [2,0],
      "start_heading_deg": 0,
      "swim_speed": 4.0,
      "ramp_max_ticks": 6,
      "surface_depth": 0.5,
      "oxygen_max_s": 30,
      "oxygen_refill_per_tick": 6,
      "choke_interval_ticks": 60,
      "hp_max": 3,
      "hold_capacity": 12,
      "interact_radius": 2.0,
      "node_yield": 1,
      "regrow_s": 20,
      "catch_radius": 2.0,
      "catch_cooldown_s": 0.5,
      "fish_yield": {"ca_linh":3,"ca_loc":1},
      "nodes": [
        {"id":"N1","kind":"bong_dien_dien","pos":[12,0]},
        {"id":"N2","kind":"bong_dien_dien","pos":[28,0]},
        {"id":"N3","kind":"bong_sung","pos":[44,0]},
        {"id":"N4","kind":"bong_sung","pos":[60,0]}
      ],
      "fish_initial": [
        {"id":"F1","kind":"ca_linh","pos":[15,5],"heading_deg":0},
        {"id":"F2","kind":"ca_loc","pos":[30,10],"heading_deg":0},
        {"id":"F3","kind":"ca_linh","pos":[45,10],"heading_deg":0},
        {"id":"F4","kind":"ca_loc","pos":[60,16],"heading_deg":0},
        {"id":"F5","kind":"ca_linh","pos":[75,5],"heading_deg":0},
        {"id":"F6","kind":"ca_loc","pos":[90,16],"heading_deg":0}
      ]
    },
    "quan": {
      "duration_s": 180,
      "bounds": {"x":[0,16],"z":[0,10]},
      "start_pos": [8,5],
      "walk_speed": 4.0,
      "ramp_max_ticks": 6,
      "interact_radius": 1.5,
      "stoves": [{"id":"B1","pos":[2,8]}],
      "tables": [{"id":"T1","pos":[9,2]}],
      "first_customer_tick": 120,
      "customer_interval_s": 15,
      "patience_s": 60,
      "eat_s": 10,
      "burn_s": null,
      "carry_limit": 1,
      "tip_rate": 0.2,
      "tip_min_patience_ratio": 0.5,
      "tip_reputation": 0.2,
      "left_reputation_delta": -0.5,
      "reputation_initial": 3.0,
      "reputation_min": 0,
      "reputation_max": 5
    },
    "menu": {
      "ca_loc_nuong_trui": {"recipe":{"ca_loc":1},"cook_s":6,"price":60},
      "goi_bong_sung": {"recipe":{"bong_sung":2},"cook_s":4,"price":40},
      "lau_ca_linh_dien_dien": {"recipe":{"ca_linh":3,"bong_dien_dien":1},"cook_s":10,"price":120}
    },
    "score": {"reputation_multiplier": 100}
  }
}
```

### Dải giá trị hợp lệ
- **Thời lượng hai ca**: `60`–`600` s.
- **Sức chứa giỏ (`hold_capacity`)**: `4`–`30` ô.
- **Kiên nhẫn (`patience_s`)**: `20`–`180` s.
- **Bán kính tương tác**: Bến / hái / bắt / tương tác quán trong khoảng `0.5`–`5` m.
- **Tốc độ bơi / đi**: `1`–`10` m/s.
- **Hồi bắt (`catch_cooldown_s`)**: `0`–`10` s.
- **Oxy tối đa (`oxygen_max_s`)**: `10`–`120` s.
- **Giá**: Số nguyên dương.
- **Thời gian nấu / mọc lại / ăn / chu kỳ khách**: Số tick dương sau quy đổi.
- `first_customer_tick`: Nguyên dương và trước khi đóng ca.
- `ramp_max_ticks`: Khai trần `0`–`6` tick.
- `tip_rate > 0`, `tip_min_patience_ratio ∈ (0, 1]`, `tip_reputation > 0`, `left_reputation_delta < 0`.
- Thời lượng, khoang, oxy, kiên nhẫn đều hữu hạn.
- Các luật và giá trị còn lại lấy theo preset, trừ vị trí các nút và đàn cá có thể chọn trong miền hợp lệ.
- **Cố định**: ID và công thức 3 món, 4 loại nguyên liệu, 1 ô/nguyên liệu, 1 bếp `B1`, 1 bàn `T1`, ít nhất một nút mỗi loại cây, 6 đàn đứng yên có cả hai loài cá, `burn_s: null`. Nút mặc định đặt ở `d = 0`, đàn cá ở dưới nước.

---

## B. Tham số headless

```bash
<headless_cmd> --mode gather|quan --seed <int> \
  [--scenario <file.json>] [--inputs <file.json>] \
  [--inventory <file.json>] [--inventory-out <file.json>] \
  --ticks <N> --out <file.jsonl> [--snapshot-every <N>]
```

- **Tham số bắt buộc**: `--mode`, `--seed`, `--ticks`, `--out`.
- `seed`: Số nguyên có dấu biểu diễn chính xác trong JSON.
- `--ticks`: Số bước ngoài tối đa, nguyên không âm. Giá trị `0` chỉ dựng fixture.
- `--snapshot-every`: Số nguyên dương, mặc định `10`.
- `--inventory`: Chỉ dùng với `quan`.
- `--inventory-out`: Chỉ dùng với `gather`. Đầu ra dùng đường dẫn riêng, tách khỏi đầu vào.
- **Mã thoát (Exit code)**:
  - `0`: Khi kết thúc lượt hoặc chạm giới hạn bước.
  - `2`: Khi cờ/dữ liệu sai cú pháp, ngoài miền hoặc fixture mâu thuẫn.
  - `1`: Khi lỗi thực thi / ghi đầu ra.
- **Quy tắc**:
  - Chẩn đoán qua `stderr`.
  - Kiểm tra dữ liệu xác định được lúc khởi tạo trước khi ghi JSONL hoặc inventory.
  - Gameplay kết thúc thì dừng sớm, ghi snapshot cuối và dòng `end`.

---

## C. File inputs

```json
{
  "frames": [
    {"tick": 0, "move": [0, 1]},
    {"tick": 120, "move": [0, 0], "catch": true},
    {"tick": 121, "catch": false},
    {"tick": 180, "interact": true},
    {"tick": 181, "interact": false}
  ]
}
```

- `tick`: Nguyên không âm, tăng nghiêm ngặt (`tick[i] < tick[i+1]`).
- Trước frame đầu: Mặc định `move = [0, 0]` và các nút là `false`.
- Mỗi frame chỉ cập nhật trường có mặt (các trường khác giữ nguyên).
- Thiếu file inputs tương đương không điều khiển.
- `move`: Gồm hai số hữu hạn trong `[-1, 1]`, tự chuẩn hóa nếu độ dài vector `> 1`.
  - Trong `gather` (`[x, d]`): Thành phần thứ hai dương là lặn xuống (`+d`).
  - Trong `quan` (`[x, z]`): Thành phần thứ hai dương là đi về hướng bắc (`+z`).
- **Nút boolean `interact`**: Dùng để cập bến hoặc hái trong `gather`; dùng để nấu, bưng hoặc phục vụ trong `quan`.
- **Nút boolean `catch`**: Dùng để bắt cá trong `gather`.
- **Cơ chế kích hoạt**: Nút chỉ tác động ở **cạnh lên** (từ `false` sang `true`). Hành động đúng kiểu nhưng sai pha được bỏ qua.
- **Lỗi**: Tên trường sai hoặc chưa hỗ trợ, kiểu sai, tick lặp/giảm → trả về mã thoát `2`.

---

## D. File scenario (Dựng tình huống để test)

Gốc nhận khối trùng `mode`. Ví dụ đặt nút đúng mép bán kính hái của preset:

```json
{
  "gather": {
    "player": {"pos": [20, 0], "heading_deg": 0},
    "hold": ["ca_loc", "bong_sung"],
    "nodes": [{"id": "N1", "kind": "bong_dien_dien", "pos": [22, 0]}],
    "fish": [],
    "random_fish": false,
    "time_left_ticks": 120
  }
}
```

### Chi tiết các khối và trường dữ liệu

| Khối / Trường | Nội dung & Quy cách |
| :--- | :--- |
| `gather.player` | `pos`, `vel`, `heading_deg`, `oxygen_ticks`, `hp`, `zero_oxy_ticks`, `catch_cd_ticks`.<br>• Mặc định vị trí và hướng theo `tuning`, vận tốc `[0, 0]`, oxy và Máu đầy. |
| `gather.hold` | Mảng `kind` theo thứ tự nhặt (mới nhất ở cuối), mặc định rỗng `[]`. |
| `gather.nodes[]` | Danh sách nút hái `{id, kind, pos, regrow_ticks}` (`0` là ready). |
| `gather.fish[]` | Danh sách cá `{id, kind, pos, heading_deg}` (hướng mặc định `0°`). |
| `gather` | Cờ `random_fish`, `time_left_ticks`. |
| `quan.player` | `{pos, vel}`, mặc định vị trí theo `tuning` và `vel: [0, 0]`. |
| `quan.stock` / `hand` | `stock`: Giá trị `items` ở mục G, gồm cả phần giữ chỗ.<br>`hand`: Payload món `{order_id, dish_id, base_price}` hoặc `null` (mặc định `null`). |
| `quan.stoves[]` | Bếp `{id, pos, state, dish, cook_ticks_left, ready_ticks}`.<br>• `state`: `idle` (mặc định), `cooking` hoặc `ready`.<br>• `ready_ticks`: Tuổi món trên bếp, mặc định `0` khi `ready`. |
| `quan.tables[]` | Bàn `{id, pos}`, thông tin khách ngồi suy ra từ khách. |
| `quan.customers[]` | Danh sách khách `{id, table_id, dish_id, order_tick, state, patience_ticks_left, eat_ticks_left, order_status, reserved, base_price, tip}`.<br>• `reserved`: Map `kind` → số lượng. |
| `quan` | `time_left_ticks`, `random_customers`, `reputation`. Uy tín mặc định theo `tuning`. |

### Quy tắc nạp scenario
- `nodes`, `fish`, `customers` thay thế danh sách mặc định; khai `[]` là rỗng.
- `stoves`, `tables` cập nhật theo `id` hiện có.
- Id duy nhất trong mỗi mảng. Sắp id bằng khóa: `(tiền tố, hậu tố số hoặc −1, id gốc)`.
  - Tiền tố là phần trước dãy chữ số ASCII cuối id, hoặc toàn id nếu không có hậu tố.
  - Chuỗi so theo mã Unicode (`F2` đứng trước `F10`).
  - Id mới nối sau hậu tố lớn nhất của họ id tương ứng đã nạp hoặc phát trong lượt.
- Các cờ `random_*` mặc định `true`:
  - `random_fish: false`: Tắt cá mặc định, cá fixture đứng yên.
  - `random_customers: false`: Tắt khách tự sinh, vẫn dùng khách fixture.
- `time_left_ticks`: Mặc định theo `tuning`. Khi khai, dùng số nguyên dương không vượt thời lượng pha.
- `phase_tick` bắt đầu từ `0`; lịch khách tính theo `phase_tick` kể cả khi rút ngắn ca.
- Bộ đếm chưa kích hoạt mặc định là `0`.
- `vel` là vận tốc tự bơi/đi đã chặn mép.
- Ràng buộc: Oxy trong `[0, max]`, Máu trong `[1, max]`. `zero_oxy_ticks` trong `[0, 59]` và chỉ dương khi oxy bằng 0 và người chơi dưới nước.
- Payload món là `{order_id, dish_id, base_price}`, với `order_id` bằng id khách.
- Khách mặc định: `state: waiting`, `order_tick: 0`, kiên nhẫn đầy, `order_status: reserved`.
- Các trạng thái đơn: `reserved` / `assigned` / `unfulfillable` / `served`.
  - Thiếu `reserved` ở đơn `reserved` thì tự cấp theo công thức theo `order_tick` rồi `table_id`.
  - Đơn `assigned` có đúng một món ở bếp hoặc tay, phần giữ rỗng.
  - Bếp `cooking` có timer dương và món khớp đơn.
  - Khách `eating` phải là `served`, có timer ăn dương và khai `base_price`, `tip` đã chốt.
  - Đơn `unfulfillable` còn chờ, giữ chỗ rỗng và không có món.
- **Mã lỗi 2**: Cho trường sai/chưa hỗ trợ, khối sai mode, id trùng trong danh sách, id bếp/bàn cập nhật không tồn tại, tọa độ ngoài miền, liên kết thiếu, bộ đếm âm/mâu thuẫn, giỏ quá trần, khai cả `quan.stock` và `--inventory`, nguyên liệu/món ngoài phạm vi, khách trùng bàn, giữ khác công thức hoặc quá tồn, bếp và tay giữ cùng đơn hoặc món không khớp đơn. Tham chiếu id không tự tạo thực thể.

---

## E. Output JSONL

Mỗi dòng là một object JSON UTF-8.
- **Chụp snapshot**:
  - Ở tick `0` sau khi dựng fixture.
  - Ở bội số của `--snapshot-every`.
  - Ở tick dừng.
  - Mỗi tick tối đa một snapshot.
- Ghi `event` theo thứ tự xử lý rồi đến `snapshot`.
- Dòng `end` luôn nằm ở cuối cùng file.

### Cấu trúc Snapshot

| Pha | Trường snapshot |
| :--- | :--- |
| **Chung** | `type: "snapshot"`, `tick`, `sim_tick`, `mode`, `phase`, `phase_tick`, `state`, `time_left_ticks`, `money`, `earned`, `reputation`, `score`.<br>• `tick`: Số bước ngoài.<br>• `sim_tick`: Số bước gameplay toàn lượt.<br>• `state`: `"playing"` hoặc `"finished"`. |
| **`gather`** | `player` theo mục D, thêm `oxygen_max_ticks`, `hp_max`, `at_surface`.<br>`hold`, `hold_count`, `hold_capacity`, `nodes[]`, `fish[]`.<br>• Nút có `ready` bằng `(regrow_ticks == 0)`. |
| **`quan`** | `player`, `stock`, `hand`, `stoves[]`, `tables[]`, `customers[]` theo mục D.<br>• Bàn thêm `customer_id` (trống là `null`). Chỉ liệt kê khách còn ngồi. |

### Cấu trúc Event

Ví dụ event:
```json
{"type": "event", "tick": 1, "phase": "gather", "name": "gather", "data": {"node_id": "N1", "kind": "bong_dien_dien", "amount": 1}}
```

| Tên Event (`name`) | Dữ liệu chi tiết (`data`) |
| :--- | :--- |
| `gather` / `node_regrown` | `node_id`, `kind`, `amount` / `node_id`. |
| `hold_full` | `action` (`gather`/`catch`), `node_id` hoặc `fish_id` tương ứng, `required`, `free`. |
| `fish_caught` | `fish_id`, `kind`, `yield` (một event mỗi đàn lấy đủ yield). |
| `dive` / `surface` | `pos` sau di chuyển (chỉ khi đổi phía của biên mặt nước). |
| `oxygen_empty` / `choke` | `oxygen_ticks: 0` khi vừa chạm 0 / `hp` sau khi trừ. |
| `faint` | `cause: "choke"`, `lost`, `hp: 0`. |
| `gather_end` | `reason` (`time`/`docked`/`fainted`), `inventory` là object theo mục G. |
| `customer_arrived` / `no_dish` | `order_id`, `table_id`, `dish_id` / `{}` khi có bàn mà thiếu món. |
| `cook_started` / `dish_ready` / `dish_picked` | Mọi event có `stove_id`, `order_id`, `dish_id`. Riêng bắt đầu nấu có thêm `items`, `base_price`. |
| `served` | `order_id`, `table_id`, `dish_id`, `patience_ticks_left`, `base_price`, `tip`. |
| `paid` | `order_id`, `table_id`, `base_price`, `tip`, `amount`, `reason` (`finished_eating`/`closing`).<br>• `base_price` là tiền món trước boa. |
| `customer_left` | `order_id`, `table_id`, `reason` (`patience`/`closing`), `reputation`. |
| `quan_end` | `reason: "time"`, `money`, `earned`, `shift_earned`, `reputation`.<br>• `money` là số dư, `earned` là tổng thu cả lượt, `shift_earned` là thu trong ca. |

### Dòng End & Quy tắc tính điểm
- `items` và `lost` trong event là mảng `kind`. `lost` theo thứ tự bỏ: nhặt sau bỏ trước (LIFO).
- Dòng cuối cùng có định dạng:
  ```json
  {"type": "end", "ticks": 10800, "sim_tick": 10800, "mode": "quan", "state": "finished", "reason": "time", "money": 72, "earned": 72, "reputation": 3.2, "score": 372}
  ```
- **Lý do kết thúc (`reason`)**:
  - `gather`: `"time"`, `"docked"`, `"fainted"`.
  - `quan`: `"time"`.
  - Giới hạn bước: `"tick_limit"` khi gameplay chưa xong.
  - Kết thúc đúng bước cuối được cấp: Ưu tiên lý do gameplay.
- **Công thức tính điểm (`score`)**: Điểm ở mọi snapshot và end là:
  $$\text{score} = \text{earned} + 100 \times \lfloor\text{reputation}\rfloor$$
- **Độ chính xác và định dạng**:
  - Sắp mảng thực thể theo `id`, `hold` theo thứ tự nhặt và `cook_started.items` theo `kind`.
  - Xuất tọa độ đến 3 chữ số thập phân.
  - So bán kính và tính giá trước định dạng.
  - So chính xác: Tiền, điểm, id, số lượng, countdown và lý do.
  - Dung sai quan sát: Tọa độ `±0.1` m, uy tín `±0.01` và đo thời gian `±2` tick.
  - Deadline, lịch, cạnh, thứ tự và tick của event biên dùng giá trị chính xác.
- **Tính tất định (Determinism)**:
  - Cùng bản chạy, máy, seed, tham số và nội dung đầu vào phải cho JSONL và file kho giống nhau từng byte.
  - Tách RNG giao diện và đồng hồ thực khỏi mô phỏng.
  - Duyệt ứng viên theo thứ tự cố định, id món theo mã Unicode.
  - Chọn ngẫu nhiên nhất quán trong mỗi bản nộp.
  - Fixture muốn dựng nhánh cụ thể thì đặt dữ liệu và tắt phần ngẫu nhiên liên quan.

---

## F. Luật bắt buộc khi xử lý một bước

### Quy tắc bước chung
1. Bước $k$ đọc frame có `tick = k`, biến trạng thái $k$ thành $k+1$ và ghi event tại $k+1$.
2. Mỗi bước tăng `sim_tick` và `phase_tick` một đơn vị, dùng `phase_tick` sau tăng cho lịch.
3. Timer không âm. Cooldown $L$ đặt ở tick $t$ dùng lại từ $t+L$.
4. Thực thể sinh cuối bước tham gia tương tác/di chuyển từ bước sau.
5. **Vật lý & Di chuyển**:
   - Dùng khoảng cách Euclid trên mặt phẳng của pha, tính cả đúng mép bán kính.
   - Vận tốc hội tụ về $\text{speed} \times \text{move}$ trong tối đa `ramp_max_ticks`, rồi giữ đích.
   - Tích phân với $\Delta t = 1/60\text{ s}$.
   - Chặn từng thành phần ở biên chữ nhật và triệt thành phần vận tốc hướng ra ngoài.
   - Vận tốc snapshot là vận tốc tự điều khiển sau chặn mép.
   - Hướng mặt theo `move` khác 0 gần nhất, đứng yên giữ hướng cuối.
   - Nội thất quán không cản đường.

---

### Quy tắc chi tiết: Gather (Lặn & Hái)
1. **Thời gian**: Tăng đồng hồ, giảm timer ca, hồi bắt và hồi nút. Nút từ 1 về 0 phát `node_regrown` theo id và có thể hái ngay.
2. **Bơi & Oxy**:
   - Bơi, chặn biên, so đầu và cuối bước để phát `dive` hoặc `surface`.
   - Tính oxy theo $d$ cuối bước:
     - **Mặt nước** ($d \le 0.5$): Cộng 6 tick oxy, kẹp tối đa và reset ngạt (`zero_oxy_ticks = 0`).
     - **Dưới nước** ($d > 0.5$): Trừ 1 tick oxy, kẹp 0.
   - Phát `oxygen_empty` khi từ dương xuống 0.
   - Mỗi bước dưới nước kết thúc với oxy 0 (kể cả bước vừa chạm 0): Tăng `zero_oxy_ticks`.
   - Đủ 60 tick: Đặt lại đếm về 0, trừ 1 Máu (`hp`), phát `choke`.
   - Khi Máu về 0: Bỏ giỏ theo LIFO, phát `faint` rồi `gather_end` với `"fainted"` và kho rỗng, dừng bước.
   - *Lưu ý*: Chạm oxy 0 ở $t$ và ở dưới nước liên tục thì ngạt lần đầu ở $t+59$ nếu đếm ban đầu là 0. Nổi lên đúng bước đáng lẽ ngạt thì hồi oxy và không ngạt.
3. **Tương tác hái / cập bến (`interact`)**:
   - Ở cạnh `interact`: Xét bến trước bằng khoảng cách tới tâm trên `[x, d]`.
   - Trong bến: Kết thúc ngay với lý do `"docked"`.
   - Ngoài bến: Chỉ hái khi ở mặt nước ($d \le 0.5$). Chọn nút ready gần nhất trong bán kính, hòa theo id Unicode.
   - Đủ chỗ: Thêm 1 nguyên liệu, đặt `regrow_ticks = regrow_s * 60` và phát `gather`.
   - Thiếu chỗ: Phát `hold_full`, nút giữ nguyên.
4. **Bắt cá (`catch`)**:
   - Ở cạnh `catch`: Nếu hết hồi và đang dưới nước ($d > 0.5$), chọn đúng đàn gần nhất trong bán kính, hòa theo id.
   - Đủ chỗ: Thêm toàn bộ yield, xóa đàn, phát `fish_caught` và đặt hồi chiêu `catch_cooldown_s * 60`.
   - Thiếu chỗ: Phát `hold_full`, giữ đàn và cooldown, không thử đàn khác.
   - Không có đàn trong tầm: Không có sự kiện bắt hay hồi chiêu.
5. **Hết giờ ca**: Timer ca về 0 thì kết thúc `"time"` ở mọi độ sâu, giữ giỏ sau các hành động trên. Chốt kho ngay khi kết thúc và dừng xử lý. `interact` đúng mép bến ở bước cuối vẫn cho `"docked"` nếu còn Máu. Ngoài bến, hái hoặc bắt hợp lệ ở bước cuối vẫn vào kho.

---

### Quy tắc chi tiết: Quán (Phục vụ ăn uống)
1. **Thời gian**: Tăng đồng hồ, giảm timer ca, nấu, ăn và kiên nhẫn. Chỉ tăng `ready_ticks` cho món đã `ready` ở đầu bước.
2. **Trạng thái bếp**: Xét bếp theo id. Món nấu xong chuyển `ready` với `ready_ticks = 0`. Dùng `burn_s: null`.
3. **Di chuyển & Tương tác (`interact`)**:
   - Di chuyển rồi xét tối đa một `interact`, chọn theo thứ tự: `(khoảng cách, bếp trước bàn, id)`.
   - Nếu đối tượng được chọn không tương tác được: Bỏ lượt.
   - **Tương tác Bếp**:
     - *Bếp `idle`*: Lấy đơn `reserved` cũ nhất theo `order_tick` rồi id bàn, tiêu đúng nguyên liệu giữ, chốt giá và bắt đầu nấu (phát `cook_started`).
     - *Bếp `ready`*: Giao món cho tay trống và về `idle` (phát `dish_picked`).
   - **Tương tác Bàn**:
     - Bàn nhận đúng `order_id`: Khách ăn với timer đầy (phát `served`).
     - Chốt boa:
       $$\text{tip} = \lfloor\text{tiền món} \times \text{tip\_rate}\rfloor$$
       nếu tỷ lệ kiên nhẫn còn lại sau bước 1 đạt $\ge \text{tip\_min\_patience\_ratio}$; nếu thấp hơn thì boa = 0.
     - Phục vụ đúng tick kiên nhẫn về 0 hoặc hết ca vẫn hợp lệ.
4. **Khách ăn xong & Khách rời bàn**:
   - Theo id bàn: Khách ăn xong trả tiền (`paid`) rồi rời bàn ngay.
   - Nếu ca còn giờ: Khách `waiting` có kiên nhẫn về 0 rời bàn (`customer_left`) và uy tín đổi theo `left_reputation_delta`.
   - Khi hết ca: Khách còn ăn trả ngay (kể cả vừa được giao món), khách còn chờ rời với `"closing"` và không trừ uy tín. Dọn xong phát `quan_end`.
   - Khi khách rời: Nhả phần giữ thô, bỏ món của đơn đang nấu, ready hoặc trên tay. Nguyên liệu đã dùng không hoàn lại.
   - Thu tiền boa dương: Cộng `tip_reputation`, kẹp uy tín theo tuning.
5. **Sinh khách mới**:
   - Nếu còn giờ: Xét lượt khách theo `first_customer_tick`, rồi mỗi chu kỳ `customer_interval_s * 60` tick.
   - Không còn bàn: Bỏ lượt.
   - Có bàn: Lấy bàn trống có id nhỏ nhất. Chọn đều theo seed trong 3 món đủ nguyên liệu khả dụng (tồn vật lý trừ phần giữ).
   - Không có món đủ: Phát `no_dish`.
   - Có món đủ: Khách mới giữ đúng công thức ngay, `order_tick` bằng `phase_tick` hiện tại, kiên nhẫn đầy và bắt đầu giảm từ bước sau.

---

## G. File kho (Hợp đồng tích hợp Lặn & Hái → Mở Quán)

```json
{
  "items": {
    "bong_sung": 2,
    "ca_loc": 1
  }
}
```

- File chỉ có khóa `items`, object `kind` → số nguyên không âm.
- `kind` vắng tính 0; bên ghi bỏ khóa có lượng 0.
- Kho rỗng: `{"items": {}}`.
- Bên đọc từ chối sai schema, kind lạ và giá trị ngoài miền (trả về mã thoát `2`).
- Trần giỏ không áp lên kho quán.
- File chỉ chứa hàng trong giỏ khi có `gather_end`, và khớp object `inventory` trong event đó.
- `gather --inventory-out` ghi đúng một lần (ngất ghi rỗng).
- Chạm `--ticks` trước khi kết thúc buổi sáng thì không tạo hoặc ghi đè file.
- Ghi file tạm cùng thư mục rồi thay thế nguyên tử sau khi ghi thành công.
- Quán độc lập thiếu cả `--inventory` và `scenario.quan.stock` thì kho rỗng. Tiền và `earned` đầu lượt độc lập bằng 0. Uy tín theo tuning, trừ khi scenario quán có khai.

### Smoke test hộp đen tích hợp
Dùng preset ở mục A:
- Tạo `dock.json`:
  ```json
  {"gather": {"hold": ["ca_loc", "bong_sung", "bong_sung"]}}
  ```
- Tạo `dock-inputs.json`:
  ```json
  {"frames": [{"tick": 0, "interact": true}]}
  ```

Snapshot quán ở tick 0 phải có `stock: {"bong_sung": 2, "ca_loc": 1}`, đúng file tiến trình đầu ghi.

```bash
# Tiến trình 1: Gather kết thúc và xuất file kho catch.json
<headless_cmd> --mode gather --seed 42 --scenario dock.json --inputs dock-inputs.json --ticks 1 --out gather.jsonl --inventory-out catch.json

# Tiến trình 2: Quán nạp file catch.json
<headless_cmd> --mode quan --seed 42 --inventory catch.json --ticks 0 --out quan.jsonl
```
