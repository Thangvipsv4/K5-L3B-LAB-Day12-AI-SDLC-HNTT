"""Buổi sáng — Lặn & Hái (`gather`).

Mặt cắt dòng sông nhìn NGANG: vị trí `[x, d]` (x sang phải, `d` độ sâu hướng xuống, d = 0 là mặt nước).
`move = [x, d]`: thành phần thứ hai DƯƠNG = bơi xuống. Hướng mặt là góc từ +x, dương = xuống.

Phase 1: Bơi, oxy, ngạt, Máu, ngất xỉu, giỏ LIFO, hái nút mặt nước, bắt cá dưới nước, cập bến, xuất kho.
Phase 2: Đàn cá bơi theo độ sâu, sinh cá chu kỳ 360 tick, thủy quái Cá Sấu Năm Chèo (patrol, chase, recoil, hit).
"""

import math

from ..ids import id_key, sort_by_id
from ..inventory import hold_to_items
from .ramp import ramp_velocity

TICK = 60.0
AXES = ("x", "d")

DEFAULT_SPAWN_X = [15.0, 30.0, 45.0, 60.0, 75.0, 90.0]
DEFAULT_SPAWN_DEPTHS = {
    "ca_linh": [5.0, 10.0],
    "ca_loc": [10.0, 16.0],
    "ca_keo": [24.0, 27.0],
}


class GatherSim:
    mode = "gather"
    phase = "gather"

    def __init__(self, tuning, scenario, streams, ids):
        t = tuning["gather"]
        self.t = t
        self.scenario = scenario
        self.rng = streams
        self.ids = ids
        self.phase_tick = 0
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        self.heading = float(p.get("heading_deg", t["start_heading_deg"]))
        self.oxygen_max = int(round(t["oxygen_max_s"] * TICK))
        self.oxygen_ticks = p.get("oxygen_ticks", self.oxygen_max)
        self.hp = p.get("hp", t["hp_max"])
        self.zero_oxy_ticks = p.get("zero_oxy_ticks", 0)
        self.invuln_ticks = p.get("invuln_ticks", 0)
        self.catch_cd_ticks = p.get("catch_cd_ticks", 0)
        self.attack_cd_ticks = p.get("attack_cd_ticks", 0)
        self.hold = list(scenario.get("hold", []))  # thứ tự nhặt, cuối mảng là mới nhất
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))

        # Nút hái
        src_nodes = scenario["nodes"] if "nodes" in scenario else t["nodes"]
        self.nodes = [{"id": n["id"], "kind": n["kind"], "pos": [float(c) for c in n["pos"]],
                       "regrow_ticks": n.get("regrow_ticks", 0)} for n in src_nodes]

        # Đàn cá
        if "fish" in scenario:
            src_fish = scenario["fish"]
        elif scenario.get("random_fish", True):
            raw_initial = t["fish_initial"]
            if isinstance(raw_initial, list):
                src_fish = raw_initial
            else:
                # Phase 2: fish_initial là số nguyên 8
                count = int(raw_initial)
                sp_x = t.get("fish_spawn_x", DEFAULT_SPAWN_X)
                sp_d = t.get("fish_spawn_depths", DEFAULT_SPAWN_DEPTHS)
                all_pts = []
                for sp, d_list in sp_d.items():
                    for x in sp_x:
                        for d in d_list:
                            all_pts.append((sp, [float(x), float(d)]))
                chosen_pts = self.rng.get("fish_spawn").sample(all_pts, min(count, len(all_pts)))
                src_fish = []
                for sp, pt in chosen_pts:
                    f_id = ids.new("F")
                    h_deg = self.rng.get("fish_spawn").uniform(0.0, 360.0)
                    src_fish.append({"id": f_id, "kind": sp, "pos": pt, "heading_deg": h_deg})
        else:
            src_fish = []

        self.fish = [{"id": f["id"], "kind": f["kind"], "pos": [float(c) for c in f["pos"]],
                      "heading_deg": float(f.get("heading_deg", 0)),
                      "age_ticks": int(f.get("age_ticks", 0))} for f in src_fish]

        # Quái vật Cá Sấu (Phase 2)
        if "monsters" in scenario:
            src_monsters = scenario["monsters"]
        elif "monsters" in t:
            day = scenario.get("day", 1)
            src_monsters = [s for s in t["monsters"].get("spawns", []) if s.get("from_day", 1) <= day]
        else:
            src_monsters = []

        self.monsters = []
        for m in src_monsters:
            wps = [list(c) for c in m.get("waypoints", [[60.0, 24.0], [64.0, 24.0]])]
            pos = list(m.get("pos", wps[0]))
            t_idx = m.get("target_idx", 1)
            state = m.get("state", "patrol")
            state_ticks = m.get("state_ticks_left", 0)
            recoil_dir = list(m["recoil_dir"]) if m.get("recoil_dir") else None
            self.monsters.append({
                "id": m["id"],
                "kind": m.get("kind", "ca_sau"),
                "pos": [float(pos[0]), float(pos[1])],
                "waypoints": wps,
                "target_idx": t_idx,
                "state": state,
                "state_ticks_left": state_ticks,
                "recoil_dir": recoil_dir
            })

        for coll in (self.nodes, self.fish, self.monsters):
            for e in coll:
                ids.reserve(e["id"])

        self.ca_ho = scenario.get("ca_ho", None)
        self.money = 0
        self.earned = 0
        self.reputation = tuning["quan"]["reputation_initial"]
        self.done = False
        self.reason = None

    # --- giao diện cho runner -------------------------------------------------
    def inventory_items(self) -> dict:
        return hold_to_items(self.hold)

    def snapshot(self) -> dict:
        p_snap = {
            "pos": list(self.pos), "vel": list(self.vel), "heading_deg": self.heading,
            "oxygen_ticks": self.oxygen_ticks, "oxygen_max_ticks": self.oxygen_max,
            "hp": self.hp, "hp_max": self.t["hp_max"], "zero_oxy_ticks": self.zero_oxy_ticks,
            "invuln_ticks": self.invuln_ticks, "catch_cd_ticks": self.catch_cd_ticks,
            "at_surface": self._at_surface()
        }
        if "attack_cd_ticks" in self.scenario.get("player", {}):
            p_snap["attack_cd_ticks"] = self.attack_cd_ticks

        snap = {
            "player": p_snap,
            "hold": list(self.hold), "hold_count": len(self.hold),
            "hold_capacity": self.t["hold_capacity"],
            "nodes": [{"id": n["id"], "pos": list(n["pos"]), "kind": n["kind"],
                       "ready": n["regrow_ticks"] == 0, "regrow_ticks": n["regrow_ticks"]}
                      for n in sort_by_id(self.nodes)],
            "fish": [{"id": f["id"], "pos": list(f["pos"]), "kind": f["kind"], "heading_deg": f["heading_deg"],
                      "age_ticks": f.get("age_ticks", 0)}
                     for f in sort_by_id(self.fish)],
        }
        if "monsters" in self.scenario or "monsters" in self.t or len(self.monsters) > 0:
            snap["monsters"] = [
                {"id": m["id"], "kind": m["kind"], "pos": list(m["pos"]),
                 "state": m["state"], "target_idx": m["target_idx"],
                 "state_ticks_left": m["state_ticks_left"]}
                for m in sort_by_id(self.monsters)
            ]
        if self.ca_ho is not None:
            snap["ca_ho"] = dict(self.ca_ho)
        return snap

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        if self.done:
            return []
        events = []

        # 1. đồng hồ, cooldown, giảm bất tử, hồi nút
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self.invuln_ticks = max(0, self.invuln_ticks - 1)
        self.catch_cd_ticks = max(0, self.catch_cd_ticks - 1)
        self.attack_cd_ticks = max(0, self.attack_cd_ticks - 1)
        for n in sort_by_id(self.nodes):
            if n["regrow_ticks"] > 0:
                n["regrow_ticks"] -= 1
                if n["regrow_ticks"] == 0:
                    events.append(("node_regrown", {"node_id": n["id"]}))

        # 2. bơi người chơi + chặn mép, dive / surface, oxy & ngạt
        was_surface = self._at_surface()
        self._move(inp)
        now_surface = self._at_surface()

        if was_surface and not now_surface:
            events.append(("dive", {"pos": list(self.pos)}))
        elif not was_surface and now_surface:
            events.append(("surface", {"pos": list(self.pos)}))

        if now_surface:
            refill = self.t.get("oxygen_refill_per_tick", 6)
            self.oxygen_ticks = min(self.oxygen_max, self.oxygen_ticks + refill)
            self.zero_oxy_ticks = 0
        else:
            had_oxy = self.oxygen_ticks > 0
            self.oxygen_ticks = max(0, self.oxygen_ticks - 1)
            if had_oxy and self.oxygen_ticks == 0:
                events.append(("oxygen_empty", {"oxygen_ticks": 0}))
            if self.oxygen_ticks == 0:
                self.zero_oxy_ticks += 1
                choke_interval = self.t.get("choke_interval_ticks", 60)
                if self.zero_oxy_ticks >= choke_interval:
                    self.zero_oxy_ticks = 0
                    self.hp -= 1
                    events.append(("choke", {"hp": self.hp}))
                    if self.hp <= 0:
                        self.hp = 0
                        lost = list(reversed(self.hold))
                        self.hold = []
                        events.append(("faint", {"cause": "choke", "lost": lost, "hp": 0}))
                        self._finish("fainted", events)
                        return events

        # 3. Quái vật di chuyển & xét va chạm (Phase 2)
        if self._step_monsters(events):
            return events

        # 4. interact: bến trước, rồi hái
        if inp.pressed("interact"):
            if self._in_dock():
                self._finish("docked", events)
                return events
            if now_surface:
                radius = self.t["interact_radius"]
                candidates = [n for n in self.nodes if n["regrow_ticks"] == 0 and math.dist(self.pos, n["pos"]) <= radius]
                if candidates:
                    target = min(candidates, key=lambda n: (math.dist(self.pos, n["pos"]), id_key(n["id"])))
                    node_yield = self.t.get("node_yield", 1)
                    free = self.t["hold_capacity"] - len(self.hold)
                    if free >= node_yield:
                        self.hold.extend([target["kind"]] * node_yield)
                        target["regrow_ticks"] = int(round(self.t["regrow_s"] * TICK))
                        events.append(("gather", {"node_id": target["id"], "kind": target["kind"], "amount": node_yield}))
                    else:
                        events.append(("hold_full", {"action": "gather", "node_id": target["id"], "required": node_yield, "free": free}))

        # 5. bắt cá (theo vị trí cá TRƯỚC KHI bơi)
        if inp.pressed("catch"):
            if self.catch_cd_ticks == 0 and not now_surface:
                radius = self.t["catch_radius"]
                candidates = [f for f in self.fish if math.dist(self.pos, f["pos"]) <= radius]
                if candidates:
                    target = min(candidates, key=lambda f: (math.dist(self.pos, f["pos"]), id_key(f["id"])))
                    fish_yield_map = dict(self.t.get("fish_yield", {"ca_linh": 3, "ca_loc": 1}))
                    fish_yield_map.setdefault("ca_keo", 2)
                    fish_yield = fish_yield_map.get(target["kind"], 1)
                    free = self.t["hold_capacity"] - len(self.hold)
                    if free >= fish_yield:
                        self.hold.extend([target["kind"]] * fish_yield)
                        self.fish.remove(target)
                        events.append(("fish_caught", {"fish_id": target["id"], "kind": target["kind"], "yield": fish_yield}))
                        self.catch_cd_ticks = int(round(self.t["catch_cooldown_s"] * TICK))
                    else:
                        events.append(("hold_full", {"action": "catch", "fish_id": target["id"], "required": fish_yield, "free": free}))

        # 6. hết giờ
        if self.time_left_ticks <= 0:
            self._finish("time", events)
            return events

        # 7. Nếu còn giờ: cá bơi & sinh cá mới theo lịch (Phase 2)
        if self.scenario.get("random_fish", True) and ("fish_speed" in self.t or "fish_spawn_ticks" in self.t):
            self._swim_fish()
            self._spawn_fish_if_scheduled(events)

        return events

    # --- quái vật Cá Sấu (Phase 2) --------------------------------------------
    def _step_monsters(self, events) -> bool:
        """Cập nhật quái và xét hit. Trả về True nếu người chơi bị ngất (faint)."""
        if not self.monsters:
            return False

        mo_cfg = self.t.get("monsters", {})
        species_dict = mo_cfg.get("species", {})

        # 1. Quái di chuyển theo trạng thái
        for m in sort_by_id(self.monsters):
            spec = species_dict.get(m["kind"], {})
            p_speed = spec.get("patrol_speed", 1.0)
            c_speed = spec.get("chase_speed", 3.0)
            det_r = spec.get("detect_radius", 10.0)
            exit_r = spec.get("exit_radius", 16.0)
            d_min, d_max = spec.get("depths", [10.0, 30.0])
            r_dist = spec.get("recoil_dist", 2.0)
            r_ticks = spec.get("recoil_ticks", 60)

            if m["state"] == "recoil":
                r_dir = m["recoil_dir"] or [1.0, 0.0]
                m["pos"][0] += r_dir[0] * (r_dist / r_ticks)
                m["pos"][1] += r_dir[1] * (r_dist / r_ticks)
                m["pos"][0] = max(0.0, min(100.0, m["pos"][0]))
                m["pos"][1] = max(d_min, min(d_max, m["pos"][1]))
                m["state_ticks_left"] -= 1
                if m["state_ticks_left"] <= 0:
                    m["state"] = "patrol"
                    m["state_ticks_left"] = 0
                    m["recoil_dir"] = None

            elif m["state"] == "chase":
                dist_p = math.dist(m["pos"], self.pos)
                if dist_p > exit_r or self.pos[1] < d_min:
                    m["state"] = "patrol"
                else:
                    if dist_p > 0:
                        ux = (self.pos[0] - m["pos"][0]) / dist_p
                        ud = (self.pos[1] - m["pos"][1]) / dist_p
                        m["pos"][0] += ux * (c_speed / TICK)
                        m["pos"][1] += ud * (c_speed / TICK)
                        m["pos"][0] = max(0.0, min(100.0, m["pos"][0]))
                        m["pos"][1] = max(d_min, min(d_max, m["pos"][1]))

            if m["state"] == "patrol":
                if self.pos[1] >= d_min and math.dist(m["pos"], self.pos) <= det_r:
                    m["state"] = "chase"
                    dist_p = math.dist(m["pos"], self.pos)
                    if dist_p > 0:
                        ux = (self.pos[0] - m["pos"][0]) / dist_p
                        ud = (self.pos[1] - m["pos"][1]) / dist_p
                        m["pos"][0] += ux * (c_speed / TICK)
                        m["pos"][1] += ud * (c_speed / TICK)
                        m["pos"][0] = max(0.0, min(100.0, m["pos"][0]))
                        m["pos"][1] = max(d_min, min(d_max, m["pos"][1]))
                else:
                    target_wp = m["waypoints"][m["target_idx"]]
                    dist_wp = math.dist(m["pos"], target_wp)
                    step_dist = p_speed / TICK
                    if dist_wp <= step_dist:
                        m["pos"] = list(target_wp)
                        m["target_idx"] = 1 - m["target_idx"]
                    else:
                        ux = (target_wp[0] - m["pos"][0]) / dist_wp
                        ud = (target_wp[1] - m["pos"][1]) / dist_wp
                        m["pos"][0] += ux * step_dist
                        m["pos"][1] += ud * step_dist
                    m["pos"][0] = max(0.0, min(100.0, m["pos"][0]))
                    m["pos"][1] = max(d_min, min(d_max, m["pos"][1]))

        # 2. Xét va chạm (chỉ khi hết bất tử và người chơi ở d >= 10)
        hit_radius = 1.5
        first_spec = next(iter(species_dict.values()), {}) if species_dict else {}
        hit_radius = first_spec.get("hit_radius", 1.5)
        spec_d_min = first_spec.get("depths", [10.0, 30.0])[0]

        if self.invuln_ticks == 0 and self.pos[1] >= spec_d_min:
            candidates = [m for m in self.monsters if m["state"] != "recoil" and m["state"] != "stunned" and math.dist(self.pos, m["pos"]) <= hit_radius]
            if candidates:
                target_m = min(candidates, key=lambda m: (math.dist(self.pos, m["pos"]), id_key(m["id"])))
                t_spec = species_dict.get(target_m["kind"], {})
                self.hp -= 1
                loss_ratio = mo_cfg.get("loss_ratio", 0.5)
                lost_count = math.floor(len(self.hold) * loss_ratio)
                lost = []
                for _ in range(lost_count):
                    lost.append(self.hold.pop())
                self.invuln_ticks = mo_cfg.get("invuln_ticks", 90)
                events.append(("monster_hit", {"monster_id": target_m["id"], "hp": self.hp, "lost": lost, "pos": list(self.pos)}))

                # Đặt recoil cho quái gây hit
                dist_m = math.dist(target_m["pos"], self.pos)
                if dist_m == 0:
                    r_dir = [1.0, 0.0]
                else:
                    r_dir = [(target_m["pos"][0] - self.pos[0]) / dist_m, (target_m["pos"][1] - self.pos[1]) / dist_m]
                target_m["state"] = "recoil"
                target_m["state_ticks_left"] = t_spec.get("recoil_ticks", 60)
                target_m["recoil_dir"] = r_dir

                if self.hp <= 0:
                    self.hp = 0
                    faint_lost = list(reversed(self.hold))
                    self.hold = []
                    events.append(("faint", {"cause": "monster", "lost": faint_lost, "hp": 0}))
                    self._finish("fainted", events)
                    return True
        return False

    # --- cá bơi & sinh cá (Phase 2) -------------------------------------------
    def _swim_fish(self):
        f_speed = float(self.t.get("fish_speed", 1.5))
        x_min, x_max = self.t.get("fish_x", [4.0, 96.0])
        depths_map = self.t.get("fish_depths", {"ca_linh": [3.0, 12.0], "ca_loc": [8.0, 20.0], "ca_keo": [22.0, 28.0]})
        turn_interval = int(self.t.get("fish_turn_ticks", 120))

        for f in self.fish:
            if f["age_ticks"] > 0 and f["age_ticks"] % turn_interval == 0:
                f["heading_deg"] = self.rng.get("fish_turn").uniform(0.0, 360.0)

            rad = math.radians(f["heading_deg"])
            vx = f_speed * math.cos(rad)
            vd = f_speed * math.sin(rad)
            new_x = f["pos"][0] + vx / TICK
            new_d = f["pos"][1] + vd / TICK

            d_min, d_max = depths_map.get(f["kind"], [0.0, 30.0])

            if new_x < x_min:
                new_x = x_min + (x_min - new_x)
                vx = -vx
            elif new_x > x_max:
                new_x = x_max - (new_x - x_max)
                vx = -vx

            if new_d < d_min:
                new_d = d_min + (d_min - new_d)
                vd = -vd
            elif new_d > d_max:
                new_d = d_max - (new_d - d_max)
                vd = -vd

            f["pos"] = [new_x, new_d]
            f["heading_deg"] = math.degrees(math.atan2(vd, vx)) % 360.0
            f["age_ticks"] += 1

    def _spawn_fish_if_scheduled(self, events):
        spawn_ticks = int(self.t.get("fish_spawn_ticks", 360))
        if self.phase_tick <= 0 or self.phase_tick % spawn_ticks != 0:
            return

        max_fish = int(self.t.get("fish_max", 12))
        if len(self.fish) >= max_fish:
            return

        sp_x = self.t.get("fish_spawn_x", DEFAULT_SPAWN_X)
        sp_d = self.t.get("fish_spawn_depths", DEFAULT_SPAWN_DEPTHS)
        clearance = float(self.t.get("fish_spawn_clearance", 1.0))

        # Tìm các điểm sinh hợp lệ cách mọi đàn đang sống > clearance
        valid_by_species = {}
        for sp, d_list in sp_d.items():
            valid_pts = []
            for x in sp_x:
                for d in d_list:
                    pt = [float(x), float(d)]
                    if all(math.dist(pt, f["pos"]) > clearance for f in self.fish):
                        valid_pts.append(pt)
            if valid_pts:
                valid_by_species[sp] = valid_pts

        if not valid_by_species:
            return

        # Chọn loài theo trọng số
        weights_map = self.t.get("fish_weights", {"ca_linh": 40, "ca_loc": 30, "ca_keo": 30})
        avail_species = list(valid_by_species.keys())
        raw_weights = [weights_map.get(sp, 30) for sp in avail_species]
        total_w = sum(raw_weights)
        norm_weights = [w / total_w for w in raw_weights]

        chosen_sp = self.rng.get("fish_spawn").choices(avail_species, weights=norm_weights, k=1)[0]
        chosen_pt = self.rng.get("fish_spawn").choice(valid_by_species[chosen_sp])
        init_heading = self.rng.get("fish_spawn").uniform(0.0, 360.0)
        new_id = self.ids.new("F")

        new_fish = {
            "id": new_id,
            "kind": chosen_sp,
            "pos": list(chosen_pt),
            "heading_deg": init_heading,
            "age_ticks": 0
        }
        self.fish.append(new_fish)
        events.append(("fish_spawned", {"id": new_id, "kind": chosen_sp, "pos": list(chosen_pt)}))

    # --- tiện ích ---------------------------------------------------------------
    def _at_surface(self) -> bool:
        return self.pos[1] <= self.t["surface_depth"]

    def _in_dock(self) -> bool:
        return math.dist(self.pos, self.t["dock_pos"]) <= self.t["dock_radius"]

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        events.append(("gather_end", {"reason": reason, "inventory": {"items": self.inventory_items()}}))

    def _move(self, inp):
        speed = self.t["swim_speed"]
        mx, md = inp.move
        self.vel = ramp_velocity(self, (mx * speed, md * speed), int(self.t["ramp_max_ticks"]))
        if (mx, md) != (0.0, 0.0):
            self.heading = math.degrees(math.atan2(md, mx)) % 360
        b = self.t["bounds"]
        for i, axis in enumerate(AXES):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i] = lo
                self.vel[i] = max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i] = hi
                self.vel[i] = min(0.0, self.vel[i])
