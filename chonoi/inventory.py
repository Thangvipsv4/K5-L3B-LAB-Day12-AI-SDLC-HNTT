"""Inventory schemas and freshness conversions for Test Contract v1.1/v1.2.

The count-based helpers remain for v1.1 callers. New code should use the
individual-item helpers (``read_items`` / ``write_items``) at v1.2 boundaries.
Simulation adapters can keep freshness as integer ``u`` units internally.
"""

from fractions import Fraction
import json
import math
import os
import tempfile

from .errors import BadInput
from .ids import sort_by_id

KINDS = ("ca_loc", "ca_linh", "ca_keo", "bong_dien_dien", "bong_sung", "keo_neo")
KINDS_P1 = KINDS  # compatibility for current v1.1 modules
FRESH_SCALE = 240
FRESH_U = 100 * FRESH_SCALE
SPOIL_U = 30 * FRESH_SCALE
GATHER_DECAY_U_PER_TICK = 2
QUAN_DECAY_U_PER_TICK = 1


def to_units(fresh):
    """Convert public freshness to exact integer units (1/240 freshness point).

    Decimal JSON values are parsed through their string representation and
    rounded to the nearest 1/240 unit. This keeps the threshold comparison
    integer-based while retaining ordinary finite JSON freshness values.
    """
    if isinstance(fresh, bool) or not isinstance(fresh, (int, float)):
        raise BadInput("fresh phải là số hữu hạn trong [0, 100]")
    if not math.isfinite(fresh) or not 0 <= fresh <= 100:
        raise BadInput("fresh phải là số hữu hạn trong [0, 100]")
    scaled = Fraction(str(fresh)) * FRESH_SCALE
    # Values produced by the adapter are usually exactly representable. For
    # external JSON decimals between units, choose the nearest internal unit.
    return int(round(scaled))


def to_fresh(units):
    """Convert integer internal freshness units to a public float."""
    if isinstance(units, bool) or not isinstance(units, int) or not 0 <= units <= FRESH_U:
        raise BadInput("đơn vị fresh phải là số nguyên trong [0, 24000]")
    return float(Fraction(units, FRESH_SCALE))


def item_out(item):
    """Return the public schema, deliberately excluding private ``u``."""
    if not isinstance(item, dict):
        raise BadInput("item phải là object")
    if not isinstance(item.get("id"), str) or not item["id"]:
        raise BadInput("item.id phải là chuỗi không rỗng")
    if item.get("kind") not in KINDS:
        raise BadInput(f"nguyên liệu lạ: {item.get('kind')}")
    units = item.get("u") if "u" in item else to_units(item.get("fresh"))
    return {"id": item.get("id"), "kind": item.get("kind"), "fresh": to_fresh(units)}


def item_in(item):
    """Convert a public item into its private integer-freshness form."""
    public = validate_item(item)
    return {"id": public["id"], "kind": public["kind"], "u": to_units(public["fresh"])}


def new_item(kind, ids, initial=100):
    """Allocate a unique ingredient id and initialize its freshness."""
    if kind not in KINDS:
        raise BadInput(f"nguyên liệu lạ: {kind}")
    units = to_units(initial)
    return {"id": ids.new("I"), "kind": kind, "u": units}


def validate_item(item, kinds=KINDS):
    if not isinstance(item, dict) or set(item) != {"id", "kind", "fresh"}:
        raise BadInput("mỗi item phải có đúng các khóa id, kind, fresh")
    ident = item["id"]
    if not isinstance(ident, str) or not ident:
        raise BadInput("item.id phải là chuỗi không rỗng")
    if item["kind"] not in kinds:
        raise BadInput(f"nguyên liệu lạ: {item['kind']}")
    to_units(item["fresh"])
    return {"id": ident, "kind": item["kind"], "fresh": float(item["fresh"])}


def validate_item_list(items, kinds=KINDS):
    """Validate an individual-item array and reject legacy count objects."""
    if not isinstance(items, list):
        raise BadInput("items phải là mảng cá thể (không nhận kho đếm cũ)")
    result, seen = [], set()
    for raw in items:
        item = validate_item(raw, kinds)
        if item["id"] in seen:
            raise BadInput(f"id trùng: {item['id']}")
        seen.add(item["id"])
        result.append(item)
    return result


def read_items(path: str, kinds=KINDS):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được file kho {path}: {e}")
    if not isinstance(data, dict) or set(data) != {"items"}:
        raise BadInput("file kho chỉ được có khóa gốc 'items'")
    return validate_item_list(data["items"], kinds)


def write_items(path: str, items, kinds=KINDS):
    items = sort_by_id(validate_item_list(items, kinds))
    _atomic_write(path, {"items": items})


def _atomic_write(path, data):
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".inv-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def decay_items(items, amount, location):
    """Apply integer-unit decay in place and return threshold-crossing events.

    ``items`` use the private ``u`` representation. Event ordering follows id.
    ``amount`` is units per simulation tick; callers skip this function while
    paused and do not pass cooked dishes or shop stock.
    """
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise BadInput("mức hao fresh phải là số nguyên không âm")
    if location not in ("hold", "stock"):
        raise BadInput("location phải là hold hoặc stock")
    crossed = []
    for item in sort_by_id(items):
        before = item.get("u")
        if isinstance(before, bool) or not isinstance(before, int) or not 0 <= before <= FRESH_U:
            raise BadInput(f"freshness nội bộ không hợp lệ cho {item.get('id')}")
        item["u"] = max(0, before - amount)
        if before >= SPOIL_U and item["u"] < SPOIL_U:
            crossed.append({"item_id": item["id"], "kind": item["kind"], "location": location})
    return crossed


# ---- v1.1 count-based API; retained until gather/quan switch to v1.2. ----

def validate_items(items, kinds=KINDS_P1):
    if not isinstance(items, dict):
        raise BadInput("items phải là object")
    out = {}
    for k, v in items.items():
        if k not in kinds:
            raise BadInput(f"nguyên liệu lạ: {k}")
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise BadInput(f"số lượng không hợp lệ cho {k}: {v!r}")
        if v > 0:
            out[k] = v
    return out


def read_inventory(path: str, kinds=KINDS_P1) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được file kho {path}: {e}")
    if not isinstance(data, dict) or set(data.keys()) != {"items"}:
        raise BadInput("file kho chỉ được có khóa gốc 'items'")
    return validate_items(data["items"], kinds)


def hold_to_items(hold: list) -> dict:
    counts = {}
    for k in hold:
        counts[k] = counts.get(k, 0) + 1
    return {k: counts[k] for k in sorted(counts)}


def write_inventory(path: str, items: dict):
    items = {k: items[k] for k in sorted(items) if items[k] > 0}
    _atomic_write(path, {"items": items})
