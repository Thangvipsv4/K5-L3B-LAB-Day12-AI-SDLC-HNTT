"""Đọc game.contract.json và kiểm dải hợp lệ của tuning (Test Contract v1.1, docs/phase2.md mục 4.1)."""

import json
import os

from .errors import BadInput

FISH_KINDS = ("ca_linh", "ca_loc", "ca_keo")
NODE_KINDS = ("bong_dien_dien", "bong_sung", "keo_neo")
INGREDIENTS = FISH_KINDS + NODE_KINDS

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game.contract.json")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _between(name, v, lo, hi):
    if not _num(v) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải trong [{lo}, {hi}], đang là {v!r}")


def load_contract(path=DEFAULT_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được {path}: {e}")
    validate_tuning(c.get("tuning"))
    return c


def _int_between(name, v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, int) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải là số nguyên trong [{lo}, {hi}], đang là {v!r}")


def _pos_in(name, pos, bounds, keys):
    if (not isinstance(pos, list) or len(pos) != 2 or not all(_num(c) for c in pos)):
        raise BadInput(f"tuning.{name} phải là [số, số]")
    for c, k in zip(pos, keys):
        lo, hi = bounds[k]
        if not (lo <= c <= hi):
            raise BadInput(f"tuning.{name} nằm ngoài vùng {k} ∈ [{lo}, {hi}]")


def _bounds(name, b, keys):
    if not isinstance(b, dict) or set(b) != set(keys):
        raise BadInput(f"tuning.{name}.bounds phải có đúng khóa {list(keys)}")
    for k in keys:
        v = b[k]
        if not (isinstance(v, list) and len(v) == 2 and all(_num(c) for c in v) and v[0] == 0 and v[1] > 0):
            raise BadInput(f"tuning.{name}.bounds.{k} phải là [0, số dương]")


def _validate_gather(g):
    """Dải hợp lệ P1 theo PRD mục 13.2."""
    _between("gather.duration_s", g.get("duration_s"), 60, 600)
    _bounds("gather", g.get("bounds"), ("x", "d"))
    b = g["bounds"]
    _between("gather.dock_radius", g.get("dock_radius"), 0.5, 5)
    _between("gather.interact_radius", g.get("interact_radius"), 0.5, 5)
    _between("gather.catch_radius", g.get("catch_radius"), 0.5, 5)
    _between("gather.swim_speed", g.get("swim_speed"), 1, 10)
    _between("gather.catch_cooldown_s", g.get("catch_cooldown_s"), 0, 10)
    _between("gather.oxygen_max_s", g.get("oxygen_max_s"), 10, 120)
    _int_between("gather.ramp_max_ticks", g.get("ramp_max_ticks"), 0, 6)
    _int_between("gather.hold_capacity", g.get("hold_capacity"), 4, 30)
    _int_between("gather.hp_max", g.get("hp_max"), 1, 99)
    _int_between("gather.oxygen_refill_per_tick", g.get("oxygen_refill_per_tick"), 1, 10_000)
    _int_between("gather.choke_interval_ticks", g.get("choke_interval_ticks"), 1, 10_000)
    _int_between("gather.node_yield", g.get("node_yield"), 1, 12)
    _between("gather.regrow_s", g.get("regrow_s"), 0.1, 600)
    _between("gather.surface_depth", g.get("surface_depth"), 0, 5)
    _pos_in("gather.dock_pos", g.get("dock_pos"), b, ("x", "d"))
    _pos_in("gather.start_pos", g.get("start_pos"), b, ("x", "d"))
    if not _num(g.get("start_heading_deg")):
        raise BadInput("tuning.gather.start_heading_deg phải là số")
    fy = g.get("fish_yield")
    if not isinstance(fy, dict) or set(fy) != set(FISH_KINDS):
        raise BadInput(f"tuning.gather.fish_yield phải có đúng {list(FISH_KINDS)}")
    for k, v in fy.items():
        _int_between(f"gather.fish_yield.{k}", v, 1, g["hold_capacity"])
    nodes = g.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise BadInput("tuning.gather.nodes phải là mảng không rỗng")
    seen, kinds = set(), set()
    for n in nodes:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or n["id"] in seen:
            raise BadInput("tuning.gather.nodes: mỗi nút cần id duy nhất")
        seen.add(n["id"])
        if n.get("kind") not in NODE_KINDS:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: kind phải thuộc {list(NODE_KINDS)}")
        kinds.add(n["kind"])
        _pos_in(f"gather.nodes.{n['id']}.pos", n.get("pos"), b, ("x", "d"))
        if n["pos"][1] != 0:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
    if kinds != set(NODE_KINDS):
        raise BadInput(f"tuning.gather.nodes phải có ít nhất một nút mỗi loại {list(NODE_KINDS)}")
    _validate_fish(g, b)
    _validate_monsters(g.get("monsters"), b)


def _species_map(name, m, check):
    if not isinstance(m, dict) or set(m) != set(FISH_KINDS):
        raise BadInput(f"tuning.gather.{name} phải có đúng các loài {list(FISH_KINDS)}")
    for k, v in m.items():
        check(f"gather.{name}.{k}", v)


def _range(name, v, lo=None, hi=None):
    if not (isinstance(v, list) and len(v) == 2 and all(_num(c) for c in v) and v[0] <= v[1]):
        raise BadInput(f"tuning.{name} phải là [min, max]")
    if lo is not None and not (lo <= v[0] and v[1] <= hi):
        raise BadInput(f"tuning.{name} phải nằm trong [{lo}, {hi}]")


def _validate_fish(g, b):
    """v1.1: fish_initial là SỐ đàn đầu ca; vị trí sinh lấy từ fish_spawn_x × fish_spawn_depths theo seed."""
    bx, bd = b["x"], b["d"]
    _int_between("gather.fish_max", g.get("fish_max"), 1, 100)
    _int_between("gather.fish_initial", g.get("fish_initial"), 0, g["fish_max"])
    _between("gather.fish_speed", g.get("fish_speed"), 0, 10)
    _int_between("gather.fish_turn_ticks", g.get("fish_turn_ticks"), 1, 100_000)
    _int_between("gather.fish_spawn_ticks", g.get("fish_spawn_ticks"), 1, 100_000)
    _between("gather.fish_spawn_clearance", g.get("fish_spawn_clearance"), 0, 100)
    _range("gather.fish_x", g.get("fish_x"), bx[0], bx[1])
    _species_map("fish_depths", g.get("fish_depths"), lambda n, v: _range(n, v, bd[0], bd[1]))
    xs = g.get("fish_spawn_x")
    if not (isinstance(xs, list) and xs and all(_num(x) and g["fish_x"][0] <= x <= g["fish_x"][1] for x in xs)):
        raise BadInput("tuning.gather.fish_spawn_x phải là mảng số trong fish_x")

    def depths_ok(n, v):
        k = n.rsplit(".", 1)[1]
        lo, hi = g["fish_depths"][k]
        if not (isinstance(v, list) and v and all(_num(d) and lo <= d <= hi for d in v)):
            raise BadInput(f"tuning.{n} phải là mảng độ sâu trong fish_depths.{k}")
    _species_map("fish_spawn_depths", g.get("fish_spawn_depths"), depths_ok)
    _species_map("fish_weights", g.get("fish_weights"), lambda n, v: _between(n, v, 0, 1_000_000))


def _validate_monsters(mo, b):
    if not isinstance(mo, dict):
        raise BadInput("tuning.gather.monsters phải là object {invuln_ticks, loss_ratio, species, spawns}")
    _int_between("gather.monsters.invuln_ticks", mo.get("invuln_ticks"), 0, 100_000)
    _between("gather.monsters.loss_ratio", mo.get("loss_ratio"), 0, 1)
    sp = mo.get("species")
    if not isinstance(sp, dict) or "ca_sau" not in sp:
        raise BadInput("tuning.gather.monsters.species phải có ca_sau")
    for kind, s in sp.items():
        n = f"gather.monsters.species.{kind}"
        if not isinstance(s, dict):
            raise BadInput(f"tuning.{n} phải là object")
        for key in ("patrol_speed", "chase_speed", "detect_radius", "exit_radius", "hit_radius", "recoil_dist"):
            _between(f"{n}.{key}", s.get(key), 0, 100)
        _int_between(f"{n}.recoil_ticks", s.get("recoil_ticks"), 1, 100_000)
        _range(f"{n}.depths", s.get("depths"), b["d"][0], b["d"][1])
    seen = set()
    for m in mo.get("spawns") or []:
        if not isinstance(m, dict) or not isinstance(m.get("id"), str) or m["id"] in seen:
            raise BadInput("tuning.gather.monsters.spawns: mỗi quái cần id duy nhất")
        seen.add(m["id"])
        if m.get("kind") not in sp:
            raise BadInput(f"tuning.gather.monsters.spawns.{m['id']}: kind phải thuộc species")
        _pos_in(f"gather.monsters.spawns.{m['id']}.pos", m.get("pos"), b, ("x", "d"))
        wps = m.get("waypoints")
        if not (isinstance(wps, list) and len(wps) == 2):
            raise BadInput(f"tuning.gather.monsters.spawns.{m['id']}.waypoints phải có đúng 2 điểm")
        for w in wps:
            _pos_in(f"gather.monsters.spawns.{m['id']}.waypoints", w, b, ("x", "d"))
        _int_between(f"gather.monsters.spawns.{m['id']}.from_day", m.get("from_day"), 1, 5)
    if not seen:
        raise BadInput("tuning.gather.monsters.spawns không được rỗng")


def _validate_day_plan(dp, menu):
    if not (isinstance(dp, list) and [d.get("day") if isinstance(d, dict) else None for d in dp] == [1, 2, 3, 4, 5]):
        raise BadInput("tuning.day_plan phải là mảng 5 object với day = 1..5")
    for d in dp:
        n = f"day_plan.{d['day']}"
        dishes, ing = d.get("dishes"), d.get("ingredients")
        if not isinstance(dishes, dict) or not dishes or not isinstance(ing, dict):
            raise BadInput(f"tuning.{n}: cần dishes và ingredients là map")
        want = {}
        for dish, cnt in dishes.items():
            if dish not in menu:
                raise BadInput(f"tuning.{n}.dishes: món lạ {dish}")
            _int_between(f"{n}.dishes.{dish}", cnt, 1, 100)
            for k, q in menu[dish]["recipe"].items():
                want[k] = want.get(k, 0) + q * cnt
        if ing != want:
            raise BadInput(f"tuning.{n}.ingredients phải bằng tổng công thức × số suất: {want}")


def _validate_shop(shop):
    if not isinstance(shop, dict):
        raise BadInput("tuning.shop phải là object {max_ticks, upgrades}")
    _int_between("shop.max_ticks", shop.get("max_ticks"), 1, 100_000)
    ups = shop.get("upgrades")
    if not isinstance(ups, dict):
        raise BadInput("tuning.shop.upgrades phải là object")
    for uid, field in (("oxygen", "oxygen_max_s"), ("hp", "hp_max")):
        levels = ups.get(uid)
        lv = [x.get("level") if isinstance(x, dict) else None for x in levels] if isinstance(levels, list) else None
        if not levels or lv != list(range(1, len(levels) + 1)):
            raise BadInput(f"tuning.shop.upgrades.{uid} phải là mảng level 1..n")
        for x in levels:
            _int_between(f"shop.upgrades.{uid}.{x['level']}.price", x.get("price"), 1, 1_000_000)
            _between(f"shop.upgrades.{uid}.{x['level']}.{field}", x.get(field), 1, 1000)


def validate_tuning(t):
    if not isinstance(t, dict):
        raise BadInput("thiếu khối tuning")
    g, q, menu = t.get("gather"), t.get("quan"), t.get("menu")
    if not isinstance(g, dict) or not isinstance(q, dict) or not isinstance(menu, dict):
        raise BadInput("tuning phải có gather, quan, menu")
    _validate_gather(g)
    # Quán: dải hợp lệ P1 (PRD mục 13.2)
    _between("quan.duration_s", q.get("duration_s"), 60, 600)
    _bounds("quan", q.get("bounds"), ("x", "z"))
    _between("quan.patience_s", q.get("patience_s"), 20, 180)
    _between("quan.walk_speed", q.get("walk_speed"), 1, 10)
    _between("quan.interact_radius", q.get("interact_radius"), 0.5, 5)
    _int_between("quan.ramp_max_ticks", q.get("ramp_max_ticks", 6), 0, 6)
    _between("quan.eat_s", q.get("eat_s"), 0.1, 600)
    _between("quan.customer_interval_s", q.get("customer_interval_s"), 0.1, 600)
    _int_between("quan.first_customer_tick", q.get("first_customer_tick"), 1, int(q["duration_s"] * 60) - 1)
    if not (_num(q.get("tip_rate")) and q["tip_rate"] > 0 and _num(q.get("left_reputation_delta"))
            and q["left_reputation_delta"] < 0):
        raise BadInput("tip_rate phải > 0 và left_reputation_delta phải < 0")
    ratio = q.get("tip_min_patience_ratio")
    if not (_num(ratio) and 0 < ratio <= 1):
        raise BadInput("quan.tip_min_patience_ratio phải thuộc (0, 1]")
    if not (_num(q.get("tip_reputation")) and q["tip_reputation"] > 0):
        raise BadInput("quan.tip_reputation phải > 0")
    if q.get("burn_s") is not None:
        raise BadInput("burn_s phải là null ở Phase 1")
    # TODO(nhóm): bổ sung kiểm các khóa còn lại nếu muốn chặt hơn (bếp/bàn, uy tín, ...).
    for dish_id, d in menu.items():
        price, cook = d.get("price"), d.get("cook_s")
        if isinstance(price, bool) or not isinstance(price, int) or price <= 0 or not _num(cook) or cook <= 0:
            raise BadInput(f"menu.{dish_id}: price (nguyên) và cook_s phải > 0")
        recipe = d.get("recipe")
        if not isinstance(recipe, dict) or not recipe or any(k not in INGREDIENTS for k in recipe):
            raise BadInput(f"menu.{dish_id}.recipe phải là map nguyên liệu hợp lệ {list(INGREDIENTS)}")
        for k, v in recipe.items():
            _int_between(f"menu.{dish_id}.recipe.{k}", v, 1, 100)
    _validate_day_plan(t.get("day_plan"), menu)
    _validate_shop(t.get("shop"))
