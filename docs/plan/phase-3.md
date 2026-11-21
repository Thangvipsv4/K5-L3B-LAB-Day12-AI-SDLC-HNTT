# Phase 3 — Phân tích tác động & kế hoạch tích hợp (chốt phút 0–7)

Ticket: [docs/phase3.md](../phase3.md) ("Mùa Nước Nổi", Test Contract v1.2).
Đây là **breaking change schema kho**: kho đếm `{kind: n}` chuyển thành kho cá thể `[{id, kind, fresh}]`.
Schema chi tiết nằm ở [docs/contracts/README.md](../contracts/README.md) mục 7. Nhóm 4 người **không làm mở rộng** (`current`, `reservations`).

---

## 1. Quyết định đã chốt

| # | Quyết định | Lý do |
|---|---|---|
| D1 | Cá thể có dạng `{"id": "I<n>", "kind": str, "fresh": float}`. Id cấp bằng `ids.new("I")` từ **IdAllocator chung** | `day.py` đã truyền một `self.ids` cho gather, quan và shop, nên id tăng xuyên pha và Ngày mà không cần thêm gì |
| D2 | **Bên trong sim, độ tươi lưu bằng đơn vị nguyên `u = fresh × 240`.** Gather trừ `2`/tick, quán trừ `1`/tick. Ươn khi `u < 7200`. Kẹp đáy ở `0` | Đúng gợi ý trong ticket: 0.5/s ÷ 60 × 240 = 2. Phép so ngưỡng 30 là phép so số nguyên, không lệch nhánh |
| D3 | Đổi `fresh ↔ u` **chỉ qua adapter** `chonoi/inventory.py`. Đọc: `u = Fraction(str(fresh)) × 240`, nếu cách số nguyên < 1e-6 thì làm tròn về số nguyên đó. Ghi: `fresh = float(u / 240)` | Đọc lại file thì `u` khớp đúng, ví dụ 30.004166666666666 trở lại đúng 7201 chứ không thành 7200.9999 |
| D4 | Thứ tự xuất: `hold` theo **thứ tự vào giỏ** (cuối mảng là mới nhất, phục vụ LIFO). `stock`, file kho, `gather_end.inventory` theo **id**. `cook_started.items` theo **kind rồi id**. `customers[].reserved` là mảng id, sắp **kind rồi id** | Ticket quy định file/stock "theo id" và `cook_started` "kind rồi id". Thứ tự của `reserved` ticket chưa nói, nên nhóm chọn giống `cook_started` (ghi ở clarify) |
| D5 | Bàn giao 2 tiến trình: `quan --inventory` phải `ids.reserve()` mọi id trong file | Để hàng mua ở Shop hay Ngày sau không cấp trùng id |
| D6 | **Hai schema song song trong lúc làm, chỉ bật v1.2 một lần** ở phút 25 (xem mục 3). `main` luôn chạy `contract_version: "1.1"` cho tới commit bật | Giữ `main` xanh: 32 test hiện tại vẫn pass trong khi các lát còn đang làm |

---

## 2. Bảng tác động (module → file → test bị ảnh hưởng → người nhận)

| Module | File / hàm cần đổi | Test bị ảnh hưởng | Người |
|---|---|---|---|
| **Contract + adapter** | `game.contract.json`: `contract_version: "1.2"` + khối `freshness` · `chonoi/contract.py`: kiểm `freshness` · `chonoi/inventory.py`: **thêm** `read_items(path)`, `write_items(path, items)`, `validate_item_list()`, `to_units()`/`to_fresh()`, `SPOIL_U`; `read_inventory` theo version (v1.2 gặp kho đếm thì mã 2) · `chonoi/scenario.py`: `gather.hold`, `quan.stock` thành mảng cá thể, `customers[].reserved` thành mảng id, id duy nhất toàn cục · `chonoi/headless.py`, `chonoi/live.py`: gọi `read_items` khi v1.2 · `chonoi/runner.py` `write_inventory_if_done` | `test_smoke_p1`: `test_inv_bad_schema_exit_2`, `test_inventory_and_scenario_stock_conflict`, `test_inventory_flags_mode_mismatch_exit_2`, `test_scenario_out_of_domain_exit_2` · **mới:** kho đếm cũ cho mã 2, id trùng, `fresh` ngoài [0,100], kind lạ | **Thắng** (phút 7–15, rồi chuyển QA) |
| **Lặn (`gather`)** | `chonoi/sim/gather.py`: `self.hold` thành list cá thể (cấp `I` khi hái/bắt, `u=24000`) · hao `-2` u/tick **ở đầu bước**, phát `spoiled{item_id, kind, location:"hold"}` theo id · `lost` của `monster_hit`/`faint` là cá thể theo LIFO · `inventory_items()` trả list theo id · `gather_end.data.inventory = {"items": [...]}` · snapshot `hold` · `hold_count` giữ nguyên | `test_smoke_p1`: `test_time_ends_gather_and_keeps_hold`, `test_inv_01_gather_writes_inventory_quan_reads_it`, `test_inv_01_not_written_when_tick_limit_first`, `test_con_03_*` có dùng `hold` · `test_python_starter_units` (dòng 65: `hold: ["ca_loc"]`) · **mới:** ngưỡng ươn tick 1 (mẫu trong ticket), LIFO cá thể | **Hải** |
| **Quán (`quan`)** | `chonoi/sim/quan.py`: `self.stock` thành list cá thể (nhận nguyên id + fresh, **cả hàng đã ươn**) · hao `-1` u/tick ở bước 2, **gồm cả hàng đang giữ chỗ**, phát `spoiled{location:"stock"}` theo id · `_available_stock` / giữ chỗ: lấy cá thể **chưa ươn, tươi nhất, hòa theo id** · đơn có cá thể vừa ươn: nhả hết và thử giữ lại **1 lần**, xét theo `order_tick` rồi id bàn; thiếu thì `unfulfillable` · `cook_started`: tiêu đúng các id, `base_price = floor(giá × avg(fresh)/100)`, `items` là cá thể sắp kind rồi id · boa tính trên giá đã chốt · snapshot `stock`, `customers[].reserved` | `test_smoke_p1`: `test_inv_01_*` (đọc `stock` tick 0), `test_inventory_and_scenario_stock_conflict` · `test_day` (fake QuanSim) · **mới:** giữ chỗ tươi nhất, ươn rồi giữ lại, chốt giá, phần giữ chỗ trỏ tới hàng đã ươn thì mã 2 | **Nam** (lát nặng nhất; ai xong trước thì vào hỗ trợ) |
| **Day + Shop** | `chonoi/sim/day.py:96`: bàn giao **list cá thể** cùng tick, không hao thêm (fainted thì `[]`) · Ngày ≥ 2: cấp id mới cho fixture `gather.hold` · `chonoi/sim/shop.py`: `stock` là list, không hao | `test_day` (`_FakeGather.inventory_items`, `ShopSim(stock={"ca_loc": 2})`), `tests/fixtures/day_mode.json` (`hold`) | **Thắng** |
| **HUD** | `chonoi/web/index.html`: đọc `hold`/`stock` dạng cá thể, hiện độ tươi (số, thanh, nhãn "ươn") trên giỏ, kho và đơn giữ chỗ · toast `spoiled` · `chonoi/live.py`: đọc kho v1.2 · `docs/contracts/snapshot.v12.sample.json` để làm song song | `test_live` (nếu đọc kho) | **Tú** |
| **Tài liệu + QA** | `CHANGELOG.md` (breaking change), `docs/verification/phase-3.md`, `docs/proof/phase-3/`, `docs/clarify.md`, `docs/ai-usage-log.md` | smoke bàn giao phút 20, regression P1–P2 | **Thắng** (QA) + mọi người |

**Điểm vào/ra chung (không ai được tự chế format khác):**
`GatherSim.inventory_items() -> list[item]` theo id · `QuanSim(..., inventory=list[item])` · `ShopSim(stock=list[item])` · mọi `item` là dict `{"id","kind","fresh"}` ở **biên** (file, snapshot, event). Bên trong sim có thể giữ thêm `"u"`, nhưng **không được xuất `u`** ra snapshot hay event.

---

## 3. Thứ tự tích hợp (giữ `main` xanh)

```
phút 0–7   chốt doc này + contracts mục 7                         (Tú)        → push main
phút 7–15  adapter CỘNG THÊM trong inventory.py/scenario.py        (Thắng)     → push main (không đổi hành vi v1.1)
phút 7–25  gather / quan / HUD làm trên nhánh p3/<tên>, dùng adapter (Hải, Nam, Tú)
phút 20    smoke bàn giao trên nhánh p3/integrate: fixture fresh:100 + interact tick 0
           → quan --inventory --ticks 0, so id/kind/fresh (fresh = 100 − 0.5/60 = 99.99166…)
phút 25    Thắng gộp p3/* → p3/integrate, đổi contract_version "1.2", sửa test cũ (ghi lý do)
           → chạy 32 test + test mới + smoke day → merge main
phút 32–35 CHANGELOG, verification, tag phase-3 (hạn 2:30)
```

- **Không ai đổi `contract_version` trên `main` trước phút 25.** Trên nhánh riêng, mỗi người đặt `"1.2"` cục bộ để chạy thử.
- Hai nhánh cùng sửa một file (ví dụ `scenario.py`) thì báo nhóm trước. Chủ file: `scenario.py`, `inventory.py` thuộc Thắng; `gather.py` thuộc Hải; `quan.py` thuộc Nam; `index.html`, `live.py` thuộc Tú.

## 4. Rủi ro

| Rủi ro | Cách giảm |
|---|---|
| Lệch nhánh tại ngưỡng 30 do float | Theo D2/D3: chỉ so số nguyên `u`; test mẫu `fresh:30` thì `spoiled` ở tick 1 |
| Nam quá tải (giữ chỗ, ươn, giữ lại, giá) | Phút 20 xem tiến độ. Tú xong HUD thì sang pair với Nam phần test giữ chỗ/giá |
| Test cũ đỏ hàng loạt khi bật v1.2 | Gộp bật version và sửa test vào **một** commit, ghi lý do từng test trong commit |
| Id trùng giữa file kho và hàng Shop | Theo D5: `reserve` id khi nạp kho |
