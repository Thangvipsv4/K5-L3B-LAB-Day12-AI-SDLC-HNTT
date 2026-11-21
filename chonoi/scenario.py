"""Nạp và kiểm scenario (Contract D). Trả về dict của đúng khối theo mode.

KHUNG: kiểm cú pháp, id trùng, bộ đếm âm, khoang vượt sức chứa, trường lạ.
TODO(nhóm): bổ sung kiểm mâu thuẫn mức luật mà nhóm cần (khách giữ chỗ quá kho, đơn assigned
phải có đúng một món, khách eating thiếu giá/tip...) — xem PRD-0 mục D và 'Mâu thuẫn -> mã 2'.
"""

import json

from .errors import BadInput
from .inventory import KINDS_P1, validate_item_list, validate_items

GATHER_KEYS = {"player", "hold", "nodes", "fish", "random_fish", "time_left_ticks"}
GATHER_PLAYER_KEYS = {"pos", "vel", "heading_deg", "hp", "oxygen_ticks", "zero_oxy_ticks",
                      "invuln_ticks", "catch_cd_ticks"}
NODE_KINDS = ("bong_dien_dien", "bong_sung", "keo_neo")  # v1.1
FISH_KINDS = ("ca_linh", "ca_loc", "ca_keo")  # v1.1
QUAN_PLAYER_KEYS = {"pos", "vel"}
QUAN_KEYS = {"player", "stock", "hand", "stoves", "tables", "customers", "random_customers",
             "reputation", "time_left_ticks"}
DAY_KEYS = {"money", "earned", "reputation", "upgrades", "day_plan"}


def _check_ids(name, arr):
    if not isinstance(arr, list):
        raise BadInput(f"{name} phải là mảng")
    seen = set()
    for e in arr:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
            raise BadInput(f"{name}: mỗi phần tử cần id (chuỗi khác rỗng)")
        if e["id"] in seen:
            raise BadInput(f"{name}: id trùng {e['id']}")
        seen.add(e["id"])


def load_scenario(path, mode: str, tuning: dict) -> dict:
    if path is None:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được scenario {path}: {e}")
    if not isinstance(data, dict) or not set(data) <= {"gather", "quan", "day"}:
        raise BadInput("scenario chỉ được có khối 'gather', 'quan' hoặc 'day'")
    expected = {"day", "gather", "quan"} if mode == "day" else {mode}
    if set(data) - expected:
        raise BadInput(f"khối sai mode: chạy --mode {mode} không nhận {sorted(set(data) - expected)}")
    if mode == "day":
        day = data.get("day", {})
        if not isinstance(day, dict):
            raise BadInput("khối day phải là object")
        extra = set(day) - DAY_KEYS
        if extra:
            raise BadInput(f"trường lạ/chưa hỗ trợ trong day: {sorted(extra)}")
        _validate_day(day, tuning)
        gather = data.get("gather", {})
        quan = data.get("quan", {})
        if not isinstance(gather, dict) or not isinstance(quan, dict):
            raise BadInput("khối gather và quan trong scenario day phải là object")
        extra = set(gather) - GATHER_KEYS
        if extra:
            raise BadInput(f"trường lạ/chưa hỗ trợ trong gather: {sorted(extra)}")
        extra = set(quan) - QUAN_KEYS
        if extra:
            raise BadInput(f"trường lạ/chưa hỗ trợ trong quan: {sorted(extra)}")
        if "stock" in quan or "reputation" in quan:
            raise BadInput("mode day không nhận quan.stock hoặc quan.reputation")
        _validate_gather(gather, tuning)
        _validate_quan(quan, tuning)
        for phase, block in (("gather", gather), ("quan", quan)):
            duration = int(round(tuning[phase]["duration_s"] * 60))
            if "time_left_ticks" in block and not (isinstance(block["time_left_ticks"], int)
                    and not isinstance(block["time_left_ticks"], bool)
                    and 1 <= block["time_left_ticks"] <= duration):
                raise BadInput(f"{phase}.time_left_ticks phải là số nguyên trong [1, {duration}]")
        return data
    block = data.get(mode, {})
    if not isinstance(block, dict):
        raise BadInput(f"khối {mode} phải là object")
    allowed = GATHER_KEYS if mode == "gather" else QUAN_KEYS
    extra = set(block) - allowed
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong {mode}: {sorted(extra)}")
    dur = int(round(tuning[mode]["duration_s"] * 60))
    if "time_left_ticks" in block:
        t = block["time_left_ticks"]
        if isinstance(t, bool) or not isinstance(t, int) or not (1 <= t <= dur):
            raise BadInput(f"time_left_ticks phải là số nguyên trong [1, {dur}]")
    if mode == "gather":
        _validate_gather(block, tuning)
    else:
        _validate_quan(block, tuning)
    return block


def _validate_day(block, tuning):
    money, earned = block.get("money", 0), block.get("earned", 0)
    for name, value in (("money", money), ("earned", earned)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise BadInput(f"day.{name} phải là số nguyên không âm")
    if money > earned:
        raise BadInput("day.money không được lớn hơn day.earned")
    reputation = block.get("reputation", tuning["quan"]["reputation_initial"])
    lo, hi = tuning["quan"]["reputation_min"], tuning["quan"]["reputation_max"]
    if isinstance(reputation, bool) or not isinstance(reputation, (int, float)) or not lo <= reputation <= hi:
        raise BadInput(f"day.reputation phải nằm trong [{lo}, {hi}]")
    upgrades = block.get("upgrades", {})
    if not isinstance(upgrades, dict) or set(upgrades) - {"oxygen", "hp"}:
        raise BadInput("day.upgrades chỉ nhận oxygen và hp")
    for key in ("oxygen", "hp"):
        level = upgrades.get(key, 0)
        max_level = len(tuning["shop"]["upgrades"][key])
        if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= max_level:
            raise BadInput(f"day.upgrades.{key} phải thuộc [0, {max_level}]")
    plans = block.get("day_plan", {})
    if isinstance(plans, list):
        normalized = {}
        for plan in plans:
            if not isinstance(plan, dict) or "day" not in plan:
                raise BadInput("day.day_plan dạng mảng cần day, dishes và ingredients")
            key = str(plan["day"])
            if key in normalized:
                raise BadInput(f"day.day_plan có ngày lặp: {key}")
            normalized[key] = {k: v for k, v in plan.items() if k != "day"}
        plans = normalized
    if not isinstance(plans, dict):
        raise BadInput("day.day_plan phải là object hoặc mảng kế hoạch theo ngày")
    defaults = {str(p["day"]): p for p in tuning["day_plan"]}
    menu = tuning["menu"]
    for day, plan in plans.items():
        if str(day) not in defaults or not isinstance(plan, dict) or set(plan) != {"dishes", "ingredients"}:
            raise BadInput(f"day.day_plan.{day} không hợp lệ")
        dishes, ingredients = plan["dishes"], plan["ingredients"]
        if not isinstance(dishes, dict) or not dishes or not isinstance(ingredients, dict):
            raise BadInput(f"day.day_plan.{day} cần dishes và ingredients hợp lệ")
        expected = {}
        for dish, count in dishes.items():
            if dish not in menu or isinstance(count, bool) or not isinstance(count, int) or count <= 0:
                raise BadInput(f"day.day_plan.{day}.dishes không hợp lệ")
            for kind, quantity in menu[dish]["recipe"].items():
                expected[kind] = expected.get(kind, 0) + quantity * count
        if ingredients != expected:
            raise BadInput(f"day.day_plan.{day}.ingredients không khớp công thức")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _nonneg_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise BadInput(f"{name} phải là số nguyên không âm")


def _pos(name, pos, bounds, axes=("x", "d")):
    if not (isinstance(pos, list) and len(pos) == 2 and all(_num(c) for c in pos)):
        raise BadInput(f"{name} phải là [{axes[0]}, {axes[1]}]")
    for c, axis in zip(pos, axes):
        lo, hi = bounds[axis]
        if not (lo <= c <= hi):
            raise BadInput(f"{name} nằm ngoài vùng nước ({axis} ∈ [{lo}, {hi}])")


def _validate_gather(b, tuning):
    g = tuning["gather"]
    bounds = g["bounds"]
    for arr in ("nodes", "fish"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "random_fish" in b and not isinstance(b["random_fish"], bool):
        raise BadInput("random_fish phải là boolean")
    if "hold" in b:
        h = b["hold"]
        if _has_freshness_contract(tuning):
            validate_item_list(h)
        elif not isinstance(h, list) or any(k not in KINDS_P1 for k in h):
            raise BadInput("hold phải là mảng id nguyên liệu hợp lệ")
        if len(h) > g["hold_capacity"]:
            raise BadInput("hold vượt sức chứa")
    p = b.get("player", {})
    if not isinstance(p, dict):
        raise BadInput("player phải là object")
    extra = set(p) - GATHER_PLAYER_KEYS
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong gather.player: {sorted(extra)}")
    if "pos" in p:
        _pos("player.pos", p["pos"], bounds)
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, d]")
    if "heading_deg" in p and not _num(p["heading_deg"]):
        raise BadInput("player.heading_deg phải là số")
    for key in ("invuln_ticks", "catch_cd_ticks", "zero_oxy_ticks", "oxygen_ticks", "hp"):
        if key in p:
            _nonneg_int(f"player.{key}", p[key])
    omax = int(round(g["oxygen_max_s"] * 60))
    if "oxygen_ticks" in p and p["oxygen_ticks"] > omax:
        raise BadInput("player.oxygen_ticks vượt oxy tối đa")
    if "hp" in p and not (1 <= p["hp"] <= g["hp_max"]):
        raise BadInput("player.hp phải trong [1, hp_max]")
    if "zero_oxy_ticks" in p:
        pos = p.get("pos", g["start_pos"])
        oxy = p.get("oxygen_ticks", omax)
        if p["zero_oxy_ticks"] > 59:
            raise BadInput("player.zero_oxy_ticks phải trong [0, 59]")
        if p["zero_oxy_ticks"] > 0 and not (oxy == 0 and pos[1] > g["surface_depth"]):
            raise BadInput("player.zero_oxy_ticks > 0 chỉ khi oxy = 0 và đang dưới nước")
    for n in b.get("nodes", []):
        if n.get("kind") not in NODE_KINDS:
            raise BadInput(f"nodes.{n['id']}: kind phải là một trong {NODE_KINDS}")
        _pos(f"nodes.{n['id']}.pos", n.get("pos"), bounds)
        if n["pos"][1] != 0:
            raise BadInput(f"nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
        if "regrow_ticks" in n:
            _nonneg_int(f"nodes.{n['id']}.regrow_ticks", n["regrow_ticks"])
    for f in b.get("fish", []):
        if f.get("kind") not in FISH_KINDS:
            raise BadInput(f"fish.{f['id']}: kind phải là một trong {FISH_KINDS}")
        _pos(f"fish.{f['id']}.pos", f.get("pos"), bounds)
        if f["pos"][1] <= g["surface_depth"]:
            raise BadInput(f"fish.{f['id']}: đàn cá phải ở dưới nước")
        if "heading_deg" in f and not _num(f["heading_deg"]):
            raise BadInput(f"fish.{f['id']}.heading_deg phải là số")


def _validate_quan(b, tuning):
    for arr in ("stoves", "tables", "customers"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "stock" in b:
        if _has_freshness_contract(tuning):
            validate_item_list(b["stock"])
        else:
            validate_items(b["stock"])
    p = b.get("player", {})
    if not isinstance(p, dict) or set(p) - QUAN_PLAYER_KEYS:
        raise BadInput("quan.player chỉ có pos và vel")
    qb = tuning["quan"]["bounds"]
    if "pos" in p:
        _pos("player.pos", p["pos"], qb, axes=("x", "z"))
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, z]")
    table_ids = [c.get("table_id") for c in b.get("customers", [])]
    known = {t["id"] for t in tuning["quan"]["tables"]} | {t.get("id") for t in b.get("tables", [])}
    if _has_freshness_contract(tuning):
        stock = b.get("stock", [])
        by_id = {item["id"]: item for item in stock}
        reserved_all = set()
        for c in b.get("customers", []):
            if "reserved" not in c:
                continue
            reserved = c["reserved"]
            if not isinstance(reserved, list) or any(not isinstance(i, str) or not i for i in reserved):
                raise BadInput(f"customers.{c.get('id')}.reserved phải là mảng id")
            if len(reserved) != len(set(reserved)):
                raise BadInput(f"customers.{c.get('id')}.reserved có id trùng")
            status = c.get("order_status", "reserved")
            if status != "reserved" and reserved:
                raise BadInput(f"customers.{c.get('id')}: chỉ đơn reserved mới được giữ nguyên liệu")
            if status == "reserved" and reserved:
                missing = [ident for ident in reserved if ident not in by_id]
                if missing:
                    raise BadInput(f"customers.{c.get('id')}.reserved trỏ tới id không có trong stock: {missing}")
                if any(by_id[ident]["fresh"] < 30 for ident in reserved):
                    raise BadInput(f"customers.{c.get('id')}.reserved chứa nguyên liệu đã ươn")
                if reserved_all.intersection(reserved):
                    raise BadInput("một cá thể không thể được giữ cho nhiều đơn")
                reserved_all.update(reserved)
                dish_id = c.get("dish_id")
                if dish_id in tuning["menu"]:
                    need = tuning["menu"][dish_id]["recipe"]
                    got = {}
                    for ident in reserved:
                        kind = by_id[ident]["kind"]
                        got[kind] = got.get(kind, 0) + 1
                    if got != need:
                        raise BadInput(f"customers.{c.get('id')}.reserved không khớp công thức món")
    for c in b.get("customers", []):
        if not isinstance(c.get("table_id"), str) or c["table_id"] not in known:
            raise BadInput(f"customers.{c['id']}: table_id phải là bàn có thật")
    if len(table_ids) != len(set(table_ids)):
        raise BadInput("hai khách cùng bàn")


def _has_freshness_contract(tuning):
    """Keep the checked-in v1.1 scenario contract working during integration."""
    return "freshness" in tuning
