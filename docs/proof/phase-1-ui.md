# Bằng chứng phase 1 — `client/ui` (Tú)

Ngày 2026-11-21 · commit `e19d24f`, `d435a93`.

## Đối chiếu HUD tối thiểu (docs/phase1.md mục HUD)
| Buổi | Yêu cầu | Trường snapshot | Có trên HUD |
|---|---|---|---|
| Sáng | thời gian | `time_left_ticks` | ✅ ⏱ góc trái |
| Sáng | oxy | `player.oxygen_ticks/oxygen_max_ticks`, `zero_oxy_ticks` | ✅ thanh Oxy + cảnh báo hết oxy |
| Sáng | Máu | `player.hp/hp_max` | ✅ ♥ |
| Sáng | giỏ | `hold`, `hold_capacity` | ✅ ô giỏ + "ĐẦY!" |
| Tối | kho khả dụng | `stock` − Σ`customers[].reserved` | ✅ "còn/tổng" |
| Tối | món gọi, kiên nhẫn | `customers[].dish_id/patience_ticks_left/order_status` | ✅ bảng Đơn gọi + thanh trên bàn |
| Tối | trạng thái bếp | `stoves[].state/cook_ticks_left` | ✅ màu + nhãn + giây |
| Tối | món trên tay | `hand.dish_id` | ✅ "Trên tay" góc phải |
| Tối | tiền, uy tín | `money`, `reputation` | ✅ |

## Kiểm
1. `node --check` phần `<script>` của `index.html`: OK.
2. Render với canvas giả + snapshot mẫu (ngạt, giỏ đầy 12/12, khách reserved/eating, bếp cooking, hand):
   ```
   gather toasts [ '💢 Ngạt nước! Máu còn 2', '🧺 Giỏ đầy! Cần 2 chỗ, còn 0', '🌿 Hái được bông súng ×1' ]
   quan toasts (after reset) [ '💰 Bàn T1 trả 72k (boa 12k)', '😠 Khách bàn T2 bỏ đi — uy tín 2.7' ]
   empty snapshot ok
   ```
3. `PYTHONUTF8=1 python -m chonoi.live --mode quan --port 8765` → `GET /state` trả snapshot, `GET /` trả HUD mới.
4. Smoke test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests` → **32 test, 31 pass, 1 fail** `test_team_check.test_template_is_rejected` (fail có sẵn trước thay đổi: test kỳ vọng TEAM.md còn là bản mẫu; nhóm đã điền). Báo Thắng (QA).

## Còn mở
- Kiểm lại trên trình duyệt khi lát 1–4 của Hải/Nam đã push (sự kiện thật, `reserved` thật).
- Xác nhận nghĩa `zero_oxy_ticks` với Hải để đếm ngược choke đúng.
