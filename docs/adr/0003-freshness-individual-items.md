# ADR-0003: Chuyển schema kho sang cá thể {id, kind, fresh} (v1.2)

## Bối cảnh
Phase 3 yêu cầu theo dõi độ tươi (`fresh`) từng cá thể nguyên liệu thay vì đếm số lượng (`{kind: count}`). Đây là breaking change ảnh hưởng toàn bộ luồng Gather -> Inventory -> Quan -> UI.

## Quyết định
1. **Schema kho v1.2**: `{"items": [{"id": "I1", "kind": "ca_loc", "fresh": 100}, ...]}`.
2. **Đơn vị nội bộ (tránh sai số float)**: Dùng `240` sub-units cho mỗi 1 điểm `fresh` (max `24000`, ngưỡng ươn `30 * 240 = 7200`). Gather trừ `2/tick` (`0.5/s`), Quán trừ `1/tick` (`0.25/s`).
3. **Bật v1.2 có kiểm soát**: Giữ adapter tương thích trong lúc chuyển, bật `contract_version: "1.2"` và cập nhật test cũ (`test_inv_01`) khi cả 2 đầu Gather & Quán sẵn sàng.

## Tác động
- `chonoi/inventory.py`, `chonoi/scenario.py`, `game.contract.json`: Thắng (Schema/adapter + QA).
- `chonoi/sim/gather.py`: Hải (giỏ `hold` cá thể, `spoiled`, `lost` LIFO).
- `chonoi/sim/quan.py`: Nam (`stock` cá thể, `reserved` theo id, nhả/giữ lại khi ươn, `base_price` theo `avg(fresh)`).
- `chonoi/web/index.html`: Tú (hiển thị độ tươi & hàng ươn trên HUD).
- `tests/test_smoke_p1.py`: Cập nhật `test_inv_01` từ schema đếm sang cá thể.
