# Hợp đồng tích hợp — Nhóm HNTT · lịch sử v1.1–v1.3

Các mục Phase 2–3 dưới đây ghi lại quyết định lịch sử theo [docs/phase2.md](../phase2.md) và [docs/phase3.md](../phase3.md). Khi đổi hợp đồng thì báo cả nhóm và cập nhật tài liệu này. Nam (Integrator) giữ bản chuẩn.

- Manifest runtime hiện tại là [`game.contract.json`](../../game.contract.json), v1.3. Snapshot Phase 3 v1.2 được lưu riêng tại [`game.contract.v1.2.json`](game.contract.v1.2.json); file snapshot không thay thế manifest runtime.
- Snapshot v1.2 giữ nguyên tuning và CLI gốc v1.1/Phase 2, đồng thời thêm cấu hình freshness và schema kho cá thể theo Phase 3. Các mục dưới đây mô tả lịch sử thiết kế, không khẳng định bản runtime hiện đang ở v1.2.
- Validator [`chonoi/contract.py`](../../chonoi/contract.py) kiểm tra tuning Phase 2 và cấu hình freshness khi có mặt. Sai dữ liệu thì headless thoát với mã 2.

---

## 0. Ai sở hữu khóa nào trong `game.contract.json`

| Khóa | Chủ | Ghi chú |
|---|---|---|
| `tuning.gather.*` (trừ `monsters`) | Hải | Số chuẩn đã điền đủ: `fish_initial: 8`, các `fish_*`, nút `N5`/`N6` (`keo_neo`), `fish_yield.ca_keo: 2` |
| `tuning.gather.monsters` | Hải | `M1` từ Ngày 1, `M2` từ Ngày 3 (`from_day`) |
| `tuning.quan`, `tuning.menu`, `tuning.day_plan` | Nam | 2 bếp, 4 bàn, 6 món, kế hoạch D1–D5 |
| `tuning.shop`, `extensions` | Thắng | `extensions: []`: nhóm 4 người không bắt buộc làm mở rộng |

Muốn đổi khóa của người khác thì nhắn chủ khóa trước.

---

## 1. Schema file kho (không đổi so với v1.0, thêm 2 nguyên liệu)

    {"items": {"bong_sung": 2, "ca_keo": 2, "ca_loc": 1, "keo_neo": 1}}

- `items`: map `{<id_nguyên_liệu>: <số nguyên ≥ 0>}`. Ghi file thì bỏ mục bằng 0 và sắp key.
- **6 nguyên liệu hợp lệ** (`chonoi/inventory.py` `KINDS`): `ca_linh`, `ca_loc`, `ca_keo` (cá) và `bong_dien_dien`, `bong_sung`, `keo_neo` (nút hái).
- `gather --inventory-out`: ghi khi `gather_end` là `docked` hoặc `time`. Khi `fainted` thì ghi `{"items":{}}`.
- `quan --inventory`: nạp vào `QuanSim.stock`. Không dùng chung với `scenario.stock`.
- Mode `day` bàn giao kho **trong bộ nhớ** theo đúng schema này, không ghi file.

---

## 2. Giao diện chuyển pha (mode `day`) — **chốt để 4 lát làm song song**

### 2.1. Hàm dựng sim (đều tương thích ngược: mode `gather`/`quan` độc lập không phải truyền gì thêm)

```python
GatherSim(tuning, {**scenario_gather, "day": n}, streams, ids)            # Hải (đã có, đọc scenario.get("day", 1))
QuanSim(tuning, scenario, streams, ids, *, inventory=None,
        plan_dishes=None, reputation=None)                                # Nam
ShopSim(tuning, *, day, money, upgrades, stock)                           # Thắng (chonoi/sim/shop.py, mới)
DaySim(tuning, scenario, streams, ids, *, days=1)                         # Thắng (chonoi/sim/day.py, mới)
```

| Tham số | Ý nghĩa | Ai đọc |
|---|---|---|
| `scenario["day"]` (gather) | Ngày hiện tại (1..5), do DaySim gắn vào khối scenario gather. GatherSim chỉ dựng quái có `from_day <= day`. Không có thì mặc định 1 (mode `gather` độc lập). | Thắng gắn, Hải đọc |
| `tuning` truyền vào GatherSim | DaySim truyền **bản sao** đã áp `active_upgrades`, tức `gather.oxygen_max_s` và `gather.hp_max` lấy theo cấp. GatherSim không cần biết Shop. | Thắng tạo, Hải dùng |
| `inventory` | `dict` items (đã qua `validate_items`), là kho bàn giao từ gather. | Nam |
| `plan_dishes` | Danh sách id món trong kế hoạch Ngày. Lọc menu theo danh sách này **trước** khi lọc món đủ nguyên liệu. `None` nghĩa là cả 6 món (độc lập). | Nam |
| `reputation` | Uy tín mang qua Ngày. `None` thì dùng `quan.reputation_initial`, hoặc `scenario.reputation` nếu chạy độc lập. | Nam |

Mỗi sim tiếp tục có `mode`, `phase`, `money`, `earned`, `reputation`, `time_left_ticks`, `done`, `reason`, `snapshot()`, `step(inp) -> [(name, data)]` như v1.0. Ngoài ra:
- `GatherSim.inventory_items() -> dict`: kho bàn giao (đã có).
- `QuanSim.shift_earned`, `QuanSim.money`, `QuanSim.earned`: tiền **của ca**, tính từ 0. DaySim cộng dồn vào `money` và `earned` của Ngày.

### 2.2. DaySim — trạng thái xuyên Ngày

`day`, `money`, `earned`, `reputation`, `upgrades` (cấp đã mua), `active_upgrades` (cấp đang áp dụng), `days_completed`, `phase ∈ {"gather","quan","shop"}`, `sim` (sim con đang chạy).

- `DaySim.step(inp)` trả `[(name, data, phase, day)]`. `Session` dùng `phase` và `day` của **từng event** để ghi vỏ event, vì event kết thúc mang tên pha cũ và `day_start` mang số Ngày mới.
- `DaySim.snapshot()` trả snapshot của sim con, rồi **ghi đè** `money`, `earned`, `reputation` bằng giá trị xuyên Ngày và thêm `day`, `day_plan`, `upgrades`, `active_upgrades`.

### 2.3. Thứ tự chuyển pha (theo phase2.md 4.5.3)

```
tick 0      : day_start{} → day_plan{dishes, ingredients} → phase_start{} (gather)
gather_end  : cùng tick → kho = gather.inventory_items() ({} nếu fainted)
              → QuanSim(..., inventory=kho, plan_dishes=list(plan.dishes), reputation=day.reputation)
              → phase_start{} (quan)
quan_end    : cùng tick → day.money/earned += shift; day.reputation = quan.reputation
              → ShopSim(stock = kho dư của quán) → phase_start{} (shop)
shop_end    : cùng tick → days_completed += 1
              → nếu đủ --days: end reason "days_complete"
              → ngược lại: day += 1, active_upgrades = copy(upgrades), hủy kho dư,
                           day_start → day_plan → phase_start (gather)
```

- Pha mới chỉ chạy gameplay **từ tick sau**. Snapshot đổi pha ghi pha mới với `phase_tick: 0`.
- Oxy và Máu hồi đầy theo `active_upgrades` mỗi Ngày, giỏ làm mới. `money`, `earned`, `reputation`, `upgrades` được giữ.

### 2.4. Shop

- `buy` (chuỗi) xử lý **trước** cạnh `shop_done` trong cùng bước. Hết `shop.max_ticks` (600) thì phát `shop_end{reason:"time"}`.
- Mua cấp kế tiếp: `money -= price`, `earned` giữ nguyên, phát `bought{upgrade, level, price, money}`.
- Không đủ tiền, đã cấp tối đa hoặc lệnh lạ thì phát `buy_failed{action, reason: funds|max_level|unknown}`.

---

## 3. Inputs v1.1 (Thắng thêm vào `chonoi/inputs.py` và `live.py`)

| Trường | Kiểu | Pha | Ghi chú |
|---|---|---|---|
| `move` | `[a, b]` | gather / quan | như v1.0 |
| `interact`, `catch` | bool | như v1.0 | cạnh lên |
| `pause` | bool | cả 3 | Xét **trước tiên**. Vào pause thì chỉ tăng `tick` ngoài và phát `paused`. Cạnh lên kế tiếp phát `resumed` rồi chạy tiếp ngay bước đó. |
| `shop_done` | bool | shop | cạnh lên |
| `buy` | chuỗi | shop | `"oxygen"` / `"hp"`, chỉ chạy ở frame khai báo |

- Giữ nút qua lúc đổi pha không tạo cạnh mới. Nút đúng kiểu nhưng sai pha thì bị bỏ qua.
- Đang pause thì `sim_tick`, `phase_tick`, lịch khách và mọi timer đều **đứng yên**. Snapshot có `state: "paused"`.
- `live.py` nhận thêm `POST /input` với `{"pause": bool, "shop_done": bool, "buy": "oxygen"|"hp"}`.

---

## 4. Snapshot mà UI đọc (`GET /state`)

Nguyên tắc giữ nguyên: **UI chỉ đọc, trường chưa có thì bỏ qua.** Mẫu snapshot cho cả 3 pha nằm ở [`snapshot.day.sample.json`](snapshot.day.sample.json), để Tú dựng UI trong lúc sim chưa xong.

| Phạm vi | Trường mới ở v1.1 | Chủ |
|---|---|---|
| chung | `state: "playing" | "paused" | "finished"` | Thắng |
| `gather` | `monsters: [{id, kind, pos, state, target_idx, state_ticks_left}]`, `player.invuln_ticks`, `fish[].age_ticks` | Hải |
| `quan` | không đổi; `stoves` 2 phần tử, `tables` 4 phần tử | Nam |
| `shop` | `stock` (kho dư), `time_left_ticks` | Thắng |
| mode `day` | `day`, `day_plan {dishes, ingredients}`, `upgrades`, `active_upgrades`, `phase` | Thắng |

---

## 5. Sự kiện

Mỗi event có dạng `{"type":"event","tick","phase","name","data"}`. Ở mode `day` thì thêm `"day": <int>`.

### Đã có từ v1.0
`dive`, `surface`, `oxygen_empty`, `choke`, `faint`, `gather`, `hold_full`, `node_regrown`, `fish_caught`, `gather_end` · `customer_arrived`, `no_dish`, `customer_left`, `cook_started`, `dish_ready`, `dish_picked`, `served`, `paid`, `quan_end`.

### Thêm ở v1.1
| Event | `data` | Chủ |
|---|---|---|
| `fish_spawned` | `{id, kind, pos}` | Hải |
| `monster_hit` | `{monster_id, hp, lost: [kind… theo LIFO], pos}` | Hải |
| `faint` (mở rộng) | thêm `cause: "monster"`, `lost`, `hp: 0` | Hải |
| `day_start`, `phase_start` | `{}` | Thắng |
| `day_plan` | `{dishes, ingredients}` | Thắng |
| `paused`, `resumed` | `{}` | Thắng |
| `bought` | `{upgrade, level, price, money}` | Thắng |
| `buy_failed` | `{action, reason}` | Thắng |
| `shop_end` | `{reason: "done" | "time"}` | Thắng |

Dòng `end` của mode `day` có thêm `days_completed`. Nếu chạy đủ số Ngày thì `reason: "days_complete"`.

---

## 6. Trạng thái `main` lúc chốt (ghi lại để không ai bất ngờ)

- `game.contract.json` đã là v1.1 và validator đã chấp nhận. Test toàn repo 32/32 xanh.
- `gather.py` của Hải (commit `d158caf`) đã đọc đúng `fish_initial` = 8, `fish_*`, `monsters.spawns` và `from_day`.
  - Còn vài số viết cứng: `1.5` (`hit_radius`), `10.0` (độ sâu quái), `90` (`invuln_ticks`).
  - Nên đổi sang đọc `monsters.species.ca_sau.*` và `monsters.invuln_ticks` theo AGENTS.md.
- Test `test_gather_snapshot_has_gather_fields` đổi từ 6 sang `fish_initial` đàn, vì luật v1.1 đổi.
- `--mode day` và `--days` vẫn báo mã 2 cho tới khi Thắng làm `day.py`.
- `QuanSim` chưa có `plan_dishes`/`reputation` (Nam). Lớp `ShopSim`/`DaySim` chưa có (Thắng).

---

## 7. **v1.2 (Phase 3) — Kho cá thể và độ tươi** · chốt phút 0–7

Phân tích tác động, thứ tự tích hợp và người nhận: [docs/plan/phase-3.md](../plan/phase-3.md).
**`main` giữ v1.1 cho tới phút 25.** Thắng bật `"1.2"` trong một commit kèm sửa test.

### 7.1. Cá thể nguyên liệu

```json
{"items": [{"id": "I1", "kind": "ca_linh", "fresh": 100}, {"id": "I2", "kind": "ca_loc", "fresh": 97.5}]}
```

| Trường | Luật | Sai thì |
|---|---|---|
| `items` | khóa gốc duy nhất; mảng; rỗng là `{"items": []}` | mã 2 (kể cả file kho đếm `{"items": {...}}` cũ) |
| `id` | chuỗi khác rỗng, **duy nhất trên mọi nơi chứa** (giỏ, kho, món). Cấp `ids.new("I")` theo thứ tự vào giỏ, không cấp lại | mã 2 nếu trùng |
| `kind` | một trong 6 nguyên liệu (`inventory.KINDS`) | mã 2 |
| `fresh` | số thực hữu hạn trong [0, 100] | mã 2 |

Mẫu: [`inventory.v12.sample.json`](inventory.v12.sample.json).

### 7.2. Độ tươi — biểu diễn chung (bắt buộc dùng adapter)

- Bên trong sim dùng `u = fresh × 240` (số nguyên). `FRESH_U = 24000`, `SPOIL_U = 7200`.
- Hao mỗi tick: **gather `-2`** (ở đầu bước), **quán `-1`** (bước 2, gồm cả hàng đang giữ chỗ). Kẹp ở 0. Pause thì không hao. Món đã nấu không hao. Hàng ở Shop không hao.
- **Ươn** khi `u < SPOIL_U`. Sự kiện `spoiled` phát đúng một lần khi đi từ `≥ 7200` xuống `< 7200`. Nhiều cá thể cùng tick thì phát theo id.
- Hàng mới: `u = 24000`, bắt đầu hao **từ bước sau**.
- Adapter (`chonoi/inventory.py`, Thắng): `to_units(fresh)` (đọc chính xác, xem plan D3), `to_fresh(u)`, `item_out(it)` trả `{"id","kind","fresh"}` và **không bao giờ xuất `u`**.

### 7.3. Xuất ra (snapshot, event, file)

| Nơi | Dạng | Thứ tự |
|---|---|---|
| file kho, `gather_end.data.inventory.items` | mảng cá thể | theo id |
| snapshot gather `hold` | mảng cá thể (`hold_count` giữ nguyên) | thứ tự vào giỏ (cuối = mới nhất) |
| snapshot quán / Shop `stock` | mảng cá thể, **gồm cả hàng ươn** | theo id |
| `customers[].reserved` | mảng id, ví dụ `["I1","I3"]` | kind rồi id |
| `cook_started.data.items` | mảng cá thể đã tiêu | kind rồi id |
| `monster_hit.data.lost`, `faint.data.lost` | mảng cá thể | LIFO (mất trước đứng trước) |
| `spoiled` (mới) | `{"item_id","kind","location":"hold"|"stock"}` | theo id |

`cook_started.data.base_price` = `floor(giá niêm yết × trung bình fresh của các cá thể tiêu / 100)`. Boa = `floor(base_price × 0.2)` nếu đủ điều kiện.

### 7.4. Scenario v1.2

- `gather.hold`, `quan.stock` là mảng cá thể. `customers[].reserved` là mảng id, phải trỏ tới cá thể **chưa ươn** trong `stock`, đủ theo công thức, không trùng với đơn khác. Bỏ `reserved` thì sim tự cấp theo `order_tick` rồi id bàn.
- Mode `day`: Ngày 1 giữ id từ fixture `gather.hold`. Từ Ngày 2 cấp id mới theo thứ tự mảng, với `kind` và `fresh` ban đầu.
- Mâu thuẫn bất kỳ thì mã 2.

### 7.5. Giao diện giữa các lát (không đổi chữ ký hàm, chỉ đổi kiểu dữ liệu)

```python
GatherSim.inventory_items() -> list[dict]            # [{"id","kind","fresh"}] theo id   (Hải)
QuanSim(..., inventory=list[dict] | None)            # nhận nguyên cả hàng ươn; ids.reserve(id)  (Nam)
ShopSim(..., stock=list[dict])                       # không hao                          (Thắng)
DaySim: bàn giao list cùng tick; fainted -> []       #                                    (Thắng)
```

Snapshot mẫu cho HUD: [`snapshot.v12.sample.json`](snapshot.v12.sample.json).
