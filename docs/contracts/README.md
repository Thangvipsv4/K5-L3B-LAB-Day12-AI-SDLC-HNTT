# Hợp đồng tích hợp — Nhóm HNTT

Đã thống nhất tại kickoff. Khi đổi hợp đồng: báo cả nhóm và cập nhật tài liệu này (Nam — Integrator giữ bản chuẩn).

---

## 1. Schema file kho (`--inventory-out` / `--inventory`)

- **Định dạng JSON** (khớp `docs/contracts/inventory.sample.json`):

      {"items":{"bong_sung":2,"ca_loc":1}}

- **Kiểu dữ liệu:** object có key `"items"` chứa map `{<id_nguyên_liệu>: <số_nguyên >= 0>}`.
- **Mã nguyên liệu hợp lệ** (theo `game.contract.json`):
  - Từ `gather.nodes`: `bong_dien_dien`, `bong_sung`
  - Từ `gather.fish_initial` / `fish_yield`: `ca_linh`, `ca_loc`
- **Quy ước đầu ra/đầu vào:**
  - `gather` (`--inventory-out`): xuất từ `GatherSim.inventory_items()` qua `hold_to_items(self.hold)` khi kết thúc (`docked` hoặc `time`). Nếu `fainted` → mất toàn bộ giỏ, kho rỗng `{"items":{}}`.
  - `quan` (`--inventory`): nạp vào `QuanSim.stock` (không dùng đồng thời `--inventory` và `scenario.stock`).

---

## 2. Giao diện giữa `sim/*` và `client/ui` (`chonoi/live.py`)

Nguyên tắc: UI chỉ đọc `GET /state`, tự bỏ qua trường chưa có để không vỡ khi sim đang phát triển.

- **Lệnh UI gửi vào:**
  - `POST /input`: `{"move": [a, b], "interact": bool, "catch": bool}` với `a, b ∈ [-1, 1]`.
    - Ở `gather`: `move = [x, d]` (`d > 0` là bơi xuống).
    - Ở `quan`: `move = [x, z]`.
  - `POST /restart`: chơi lại từ đầu cùng seed và scenario.
- **Trạng thái UI đọc (`GET /state` = `snapshot()` + metadata từ `live.py`):**
  - Chung từ `live.py`: `meta` (`tuning[mode]`), `events` (tối đa 40 sự kiện gần nhất), `finished` (bool), `reason` (`str | null`), `error` (`str | null`).
  - `gather` (`GatherSim.snapshot()`):
    - `player`: `pos`, `vel`, `heading_deg`, `oxygen_ticks`, `oxygen_max_ticks`, `hp`, `hp_max`, `zero_oxy_ticks`, `invuln_ticks`, `catch_cd_ticks`, `at_surface`
    - `hold`, `hold_count`, `hold_capacity`
    - `nodes`: `[{id, pos, kind, ready, regrow_ticks}]`
    - `fish`: `[{id, pos, kind, heading_deg}]`
  - `quan` (`QuanSim.snapshot()`):
    - `player`: `{pos}`
    - `stock`: `{<nguyên_liệu>: <số_lượng > 0>}`
    - `hand`: món đang cầm hoặc `null`
    - `stoves`: `[{id, pos, state, dish, cook_ticks_left, ready_ticks}]`
    - `tables`: `[{id, pos, customer_id}]`
    - `customers`: danh sách khách (sắp xếp theo `id`)

---

## 3. Danh sách sự kiện (`events`)

Mỗi phần tử trong luồng `events` có dạng `[tên_sự_kiện, data_dict]` (được `Session`/`LiveGame` ghi nhận từ `sim.step(inp)`). UI đọc để hiển thị thông báo/hiệu ứng; QA kiểm tra trong `out.jsonl`.

### Buổi sáng (`gather` — `GatherSim` phát)
| Sự kiện | Khi nào phát | `data` (đối chiếu PRD-0 & code hiện tại) |
|---|---|---|
| `dive` | Từ mặt nước xuống dưới nước (`d > surface_depth`) | `{"pos": [x, d]}` |
| `surface` | Từ dưới nước lên mặt nước (`d <= surface_depth`) | `{"pos": [x, d]}` |
| `oxygen_empty` | `oxygen_ticks` từ > 0 giảm xuống 0 | theo PRD-0 |
| `choke` | Đủ `choke_interval_ticks` khi ngạt (`-1` Máu) | theo PRD-0 |
| `faint` | Máu về 0 | theo PRD-0 |
| `gather` | Hái nút thành công ở mặt nước | theo PRD-0 |
| `hold_full` | Giỏ đạt `hold_capacity` khi hái/bắt | theo PRD-0 |
| `node_regrown` | Nút mọc lại xong (`regrow_ticks == 0`) | `{"node_id": str}` *(đã có sẵn)* |
| `fish_caught` | Bắt đàn cá thành công dưới nước | theo PRD-0 |
| `gather_end` | Kết thúc ca sáng (`docked` / `time` / `fainted`) | `reason`, kho/thống kê theo PRD-0 |

### Buổi tối (`quan` — `QuanSim` phát)
| Sự kiện | Khi nào phát | `data` (đối chiếu PRD-0 & code hiện tại) |
|---|---|---|
| `no_dish` | Khách đến nhưng không đủ nguyên liệu nấu món nào | theo PRD-0 mục F |
| `customer_left` | Khách hết kiên nhẫn bỏ đi | theo PRD-0 mục F |
| `cook_started` | Bắt đầu nấu tại bếp | theo PRD-0 mục F |
| `dish_ready` | Món nấu xong chuyển sang `ready` | theo PRD-0 mục F |
| `dish_picked` | Nhặt món từ bếp lên tay | theo PRD-0 mục F |
| `served` | Bưng món ra bàn cho khách | theo PRD-0 mục F |
| `paid` | Khách ăn xong trả tiền (kèm boa/uy tín nếu có) | theo PRD-0 mục F |
| `quan_end` | Hết giờ ca tối (`time`) | `{"reason": "time", "money", "earned", "shift_earned", "reputation"}` *(đã có sẵn)* |
