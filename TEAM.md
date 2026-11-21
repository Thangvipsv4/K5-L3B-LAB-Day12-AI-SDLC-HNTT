# TEAM

**Tên nhóm:** HNTT  **Số người:** 4  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Trương Văn Hải | `haihai868` | `sim/gather` | PO | Nam |
| Phạm Hà Nam | `phamhanam` | `sim/quan` | Integrator | Hải |
| Nguyễn Công Tú | `nguyencongtu4800` | `client/ui` | Scrum/Release | Thắng |
| Vũ Trọng Thắng | `Thangvipsv4` | `qa` | QA lead | Tú |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Phân công chi tiết

- **Hải — `sim/gather`:** lát 1 (oxy, `choke`, Máu/`faint`, `dive`/`surface`/`oxygen_empty`, giỏ LIFO) + lát 2 (hái nút `gather`/`hold_full`/`node_regrown`, bắt cá `fish_caught`/`catch_cd_ticks`) trong `chonoi/sim/gather.py`.
- **Nam — `sim/quan`:** lát 3 (khách theo lịch, giữ chỗ nguyên liệu, kiên nhẫn, `customer_left`, `no_dish`) + lát 4 (interact bếp/bàn `cook_started`/`dish_ready`/`served`/`paid`, uy tín, `quan_end`) trong `chonoi/sim/quan.py`.
- **Tú — `client/ui`:** HUD/đồ họa đọc `snapshot()` trong `chonoi/web/index.html`, `chonoi/live.py`; mục "Sáng tạo của nhóm" trong README + `CREDITS.md`.
- **Thắng — `qa`:** chạy smoke test + headless, `docs/verification/phase-n.md`, `docs/proof/`, `docs/ai-usage-log.md`, `docs/retro.md`; gắn tag `phase-1..4` + Release `v1.0.0`.

## Thỏa thuận làm việc nhóm

- Kênh liên lạc: Discord/Zalo nhóm HNTT
- Khi bất đồng về thiết kế: nói 2 phút, không xong thì Integrator (Nam) quyết và ghi lại lý do.
- Khi ai đó trễ hoặc vướng quá 10 phút: báo ngay trong kênh, người dự phòng nhận việc.
- Giờ standup giữa phase: 5 phút đầu mỗi phase (1:00, 1:55, 2:30).
- Cách đọc code của nhau: mỗi người đọc lát kế bên (Hải↔Nam, Tú↔Thắng).
- Cách làm việc với Git: push thẳng nhánh chính, nhánh chính luôn chạy được; Thắng gắn tag.
