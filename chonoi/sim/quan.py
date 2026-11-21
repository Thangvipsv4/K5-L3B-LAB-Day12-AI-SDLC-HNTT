"""Buổi tối — Mở Quán (Phase 1, 2, 3: hỗ trợ cả schema đếm v1.1 và cá thể v1.2)."""

import math

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from ..inventory import (
    FRESH_SCALE,
    QUAN_DECAY_U_PER_TICK,
    SPOIL_U,
    decay_items,
    item_in,
    item_out,
    to_fresh,
    to_units,
)
from .ramp import ramp_velocity

TICK = 60.0


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None, day_plan=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.score_mult = tuning.get("score", {}).get("reputation_multiplier", 100)
        self.rng = streams
        self.ids = ids

        # Hỗ trợ day_plan dạng dict/list từ DaySim hoặc scenario
        raw_plan = day_plan if day_plan is not None else scenario.get("day_plan")
        if isinstance(raw_plan, dict) and "dishes" in raw_plan:
            raw_plan = raw_plan["dishes"]
        if isinstance(raw_plan, dict):
            allowed_keys = [k for k, cnt in raw_plan.items() if cnt > 0]
        elif isinstance(raw_plan, (list, tuple)):
            allowed_keys = list(raw_plan)
        elif raw_plan is None:
            allowed_keys = None
        else:
            raise BadInput("day_plan không hợp lệ")

        if allowed_keys is not None:
            bad = [d for d in allowed_keys if d not in self.menu]
            if bad:
                raise BadInput(f"day_plan chứa món không có trong menu: {bad}")
        self.day_plan = allowed_keys

        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0

        # Nhận diện v1.2 (mảng cá thể) vs v1.1 (dict đếm)
        raw_stock = inventory if inventory is not None else scenario.get("stock")
        self._v12 = isinstance(raw_stock, list) or ("freshness" in tuning)
        fresh_cfg = tuning.get("freshness", {})
        self.spoil_u = to_units(fresh_cfg.get("spoiled_below", 30)) if "spoiled_below" in fresh_cfg else SPOIL_U
        self.decay_u = (
            int(round(fresh_cfg["quan_decay_per_s"] * FRESH_SCALE / TICK))
            if "quan_decay_per_s" in fresh_cfg
            else QUAN_DECAY_U_PER_TICK
        )

        if self._v12:
            if raw_stock is None:
                raw_stock = []
            if not isinstance(raw_stock, list):
                raise BadInput("stock v1.2 phải là mảng cá thể")
            seen_ids = set()
            self.stock = []
            for raw in raw_stock:
                it = item_in(raw)
                if it["id"] in seen_ids:
                    raise BadInput(f"id cá thể trùng trong stock: {it['id']}")
                seen_ids.add(it["id"])
                ids.reserve(it["id"])
                self.stock.append(it)
            self.stock = sort_by_id(self.stock)
        else:
            self.stock = dict(raw_stock if raw_stock is not None else {})

        self.hand = scenario.get("hand")
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        self.phase_tick = 0

        if "random_customers" in scenario and not isinstance(scenario["random_customers"], bool):
            raise BadInput("random_customers phải là boolean")
        self.random_customers = scenario.get("random_customers", True)

        rep = scenario.get("reputation", t["reputation_initial"])
        if not _is_num(rep) or not (t["reputation_min"] <= rep <= t["reputation_max"]):
            raise BadInput(f"reputation phải nằm trong [{t['reputation_min']}, {t['reputation_max']}]")
        self.reputation = float(rep)

        self.stoves = [
            dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                 cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
            for s in self._merge(t["stoves"], scenario.get("stoves", []))
        ]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))

        self.customers = self._init_customers(scenario.get("customers", []))
        for e in self.customers:
            ids.reserve(e["id"])
        self._validate_kitchen_and_orders()

        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def _validate_dish_payload(self, payload, ctx):
        if not isinstance(payload, dict):
            raise BadInput(f"{ctx}: payload món phải là object")
        oid = payload.get("order_id")
        did = payload.get("dish_id")
        bp = payload.get("base_price")
        if not isinstance(oid, str) or not oid:
            raise BadInput(f"{ctx}: thiếu order_id hợp lệ")
        if did not in self.menu:
            raise BadInput(f"{ctx}: dish_id không hợp lệ ({did!r})")
        if not _is_int(bp) or bp <= 0:
            raise BadInput(f"{ctx}: base_price phải là số nguyên dương")

    def _pick_reserve_ids(self, dish_id, taken_ids):
        recipe = self.menu[dish_id]["recipe"]
        picked = []
        used = set(taken_ids)
        for kind in sorted(recipe):
            need = recipe[kind]
            cands = [
                it for it in self.stock
                if it["kind"] == kind and it["u"] >= self.spoil_u and it["id"] not in used
            ]
            cands.sort(key=lambda it: (-it["u"], id_key(it["id"])))
            if len(cands) < need:
                return None
            for it in cands[:need]:
                picked.append(it["id"])
                used.add(it["id"])
        return picked

    def _init_customers(self, raw_customers):
        patience_max = int(round(self.t["patience_s"] * TICK))
        eat_max = int(round(self.t["eat_s"] * TICK))
        out = []

        stock_by_id = {it["id"]: it for it in self.stock} if self._v12 else {}

        for raw in raw_customers:
            cid = raw["id"]
            did = raw.get("dish_id")
            if did not in self.menu:
                raise BadInput(f"customers.{cid}: dish_id không hợp lệ ({did!r})")

            state = raw.get("state", "waiting")
            if state not in ("waiting", "eating"):
                raise BadInput(f"customers.{cid}: state phải là waiting hoặc eating")

            order_tick = raw.get("order_tick", 0)
            if not _is_int(order_tick) or order_tick < 0:
                raise BadInput(f"customers.{cid}: order_tick phải là nguyên không âm")

            pat = raw.get("patience_ticks_left", patience_max)
            if not _is_int(pat) or not (0 <= pat <= patience_max):
                raise BadInput(f"customers.{cid}: patience_ticks_left phải trong [0, {patience_max}]")

            eat = raw.get("eat_ticks_left", 0)
            if not _is_int(eat) or eat < 0:
                raise BadInput(f"customers.{cid}: eat_ticks_left phải nguyên không âm")

            status = raw.get("order_status", "reserved")
            if status not in ("reserved", "assigned", "unfulfillable", "served"):
                raise BadInput(f"customers.{cid}: order_status không hợp lệ ({status!r})")

            recipe = self.menu[did]["recipe"]
            empty_res = [] if self._v12 else {}

            if state == "eating":
                if status != "served":
                    raise BadInput(f"customers.{cid}: khách eating phải có order_status='served'")
                if not (1 <= eat <= eat_max):
                    raise BadInput(f"customers.{cid}: khách eating cần eat_ticks_left trong [1, {eat_max}]")
                if "base_price" not in raw or not _is_int(raw["base_price"]) or raw["base_price"] <= 0:
                    raise BadInput(f"customers.{cid}: khách eating thiếu base_price hợp lệ")
                if "tip" not in raw or not _is_int(raw["tip"]) or raw["tip"] < 0:
                    raise BadInput(f"customers.{cid}: khách eating thiếu tip hợp lệ")
                if raw.get("reserved"):
                    raise BadInput(f"customers.{cid}: khách eating phải có reserved rỗng")
                reserved = empty_res
                base_price = raw["base_price"]
                tip = raw["tip"]
            else:
                if status == "served":
                    raise BadInput(f"customers.{cid}: khách waiting không thể có order_status='served'")
                if eat != 0:
                    raise BadInput(f"customers.{cid}: khách waiting phải có eat_ticks_left=0")
                base_price = raw.get("base_price", self.menu[did]["price"])
                if not _is_int(base_price) or base_price <= 0:
                    raise BadInput(f"customers.{cid}: base_price không hợp lệ")
                tip = raw.get("tip", 0)
                if not _is_int(tip) or tip < 0:
                    raise BadInput(f"customers.{cid}: tip không hợp lệ")

                if status == "reserved":
                    if "reserved" in raw:
                        res = raw["reserved"]
                        if self._v12:
                            if not isinstance(res, list) or any(not isinstance(i, str) for i in res):
                                raise BadInput(f"customers.{cid}: reserved v1.2 phải là mảng id cá thể")
                            if len(set(res)) != len(res):
                                raise BadInput(f"customers.{cid}: reserved có id trùng")
                            counts = {}
                            for iid in res:
                                it = stock_by_id.get(iid)
                                if it is None:
                                    raise BadInput(f"customers.{cid}: reserved trỏ id không có trong stock ({iid})")
                                if it["u"] < self.spoil_u:
                                    raise BadInput(f"customers.{cid}: reserved trỏ cá thể đã ươn ({iid})")
                                counts[it["kind"]] = counts.get(it["kind"], 0) + 1
                            if counts != recipe:
                                raise BadInput(f"customers.{cid}: giữ chỗ khác công thức món {did}")
                            reserved = list(res)
                        else:
                            if not isinstance(res, dict) or any(not _is_int(v) or v < 0 for v in res.values()):
                                raise BadInput(f"customers.{cid}: reserved không hợp lệ")
                            norm = {k: v for k, v in res.items() if v > 0}
                            if norm != recipe:
                                raise BadInput(f"customers.{cid}: giữ chỗ khác công thức món {did}")
                            reserved = dict(norm)
                    else:
                        reserved = None  # sẽ cấp theo thứ tự (order_tick, id bàn)
                else:
                    if raw.get("reserved"):
                        raise BadInput(f"customers.{cid}: đơn {status} phải có reserved rỗng")
                    reserved = empty_res

            out.append({
                "id": cid,
                "table_id": raw["table_id"],
                "dish_id": did,
                "order_tick": order_tick,
                "state": state,
                "patience_ticks_left": pat,
                "eat_ticks_left": eat,
                "order_status": status,
                "reserved": reserved,
                "base_price": base_price,
                "tip": tip,
            })

        if self._v12:
            taken = set()
            for c in out:
                if c["reserved"]:
                    for iid in c["reserved"]:
                        if iid in taken:
                            raise BadInput(f"cá thể '{iid}' bị giữ chỗ trùng bởi nhiều đơn")
                        taken.add(iid)
            for c in sorted(out, key=lambda x: (x["order_tick"], id_key(x["table_id"]))):
                if c["reserved"] is None:
                    picked = self._pick_reserve_ids(c["dish_id"], taken)
                    if picked is None:
                        raise BadInput(f"customers.{c['id']}: không đủ nguyên liệu tươi trong stock để giữ chỗ")
                    c["reserved"] = picked
                    taken.update(picked)
        else:
            used = {}
            for c in out:
                if c["reserved"]:
                    for k, v in c["reserved"].items():
                        used[k] = used.get(k, 0) + v
            for c in sorted(out, key=lambda x: (x["order_tick"], id_key(x["table_id"]))):
                if c["reserved"] is None:
                    c["reserved"] = dict(self.menu[c["dish_id"]]["recipe"])
                    for k, v in c["reserved"].items():
                        used[k] = used.get(k, 0) + v

            for k, qty in used.items():
                if qty > self.stock.get(k, 0):
                    raise BadInput(f"giữ chỗ nguyên liệu '{k}' ({qty}) vượt tồn kho ({self.stock.get(k, 0)})")

        return out

    def _validate_kitchen_and_orders(self):
        active_dishes = []
        for s in self.stoves:
            st = s["state"]
            if st not in ("idle", "cooking", "ready"):
                raise BadInput(f"stoves.{s['id']}: state không hợp lệ ({st!r})")
            ct = s["cook_ticks_left"]
            rt = s["ready_ticks"]
            if not _is_int(ct) or ct < 0 or not _is_int(rt) or rt < 0:
                raise BadInput(f"stoves.{s['id']}: bộ đếm bếp không hợp lệ")
            if st == "idle":
                if s["dish"] is not None or ct != 0 or rt != 0:
                    raise BadInput(f"stoves.{s['id']}: bếp idle không được có món/timer")
            elif st == "cooking":
                self._validate_dish_payload(s["dish"], f"stoves.{s['id']}.dish")
                cook_max = int(round(self.menu[s["dish"]["dish_id"]]["cook_s"] * TICK))
                if not (1 <= ct <= cook_max) or rt != 0:
                    raise BadInput(f"stoves.{s['id']}: bếp cooking có timer không hợp lệ")
                active_dishes.append((f"stoves.{s['id']}", s["dish"]))
            else:
                self._validate_dish_payload(s["dish"], f"stoves.{s['id']}.dish")
                if ct != 0:
                    raise BadInput(f"stoves.{s['id']}: bếp ready phải có cook_ticks_left=0")
                active_dishes.append((f"stoves.{s['id']}", s["dish"]))

        if self.hand is not None:
            self._validate_dish_payload(self.hand, "hand")
            active_dishes.append(("hand", self.hand))

        by_order = {}
        for src, payload in active_dishes:
            oid = payload["order_id"]
            if oid in by_order:
                raise BadInput(f"đơn {oid} xuất hiện trùng ở {by_order[oid]} và {src}")
            by_order[oid] = src

        cust_by_id = {c["id"]: c for c in self.customers}
        for oid, src in by_order.items():
            c = cust_by_id.get(oid)
            if c is None or c["order_status"] != "assigned":
                raise BadInput(f"{src}: món của đơn {oid} không thuộc khách ở trạng thái assigned")
            if self._payload_for(oid)["dish_id"] != c["dish_id"]:
                raise BadInput(f"{src}: món không khớp dish_id của khách {oid}")

        for c in self.customers:
            if c["order_status"] == "assigned" and c["id"] not in by_order:
                raise BadInput(f"customers.{c['id']}: đơn assigned phải có đúng một món ở bếp hoặc tay")

    def _payload_for(self, order_id):
        for s in self.stoves:
            if s["dish"] and s["dish"].get("order_id") == order_id:
                return s["dish"]
        if self.hand and self.hand.get("order_id") == order_id:
            return self.hand
        return None

    def _reserved_id_set(self):
        taken = set()
        for c in self.customers:
            for iid in c.get("reserved", []):
                taken.add(iid)
        return taken

    def _available_stock(self) -> dict:
        if self._v12:
            taken = self._reserved_id_set()
            avail = {}
            for it in self.stock:
                if it["u"] >= self.spoil_u and it["id"] not in taken:
                    avail[it["kind"]] = avail.get(it["kind"], 0) + 1
            return avail
        avail = {k: v for k, v in self.stock.items() if v > 0}
        for c in self.customers:
            for k, v in c.get("reserved", {}).items():
                avail[k] = avail.get(k, 0) - v
        return avail

    def _release_and_remove_customer(self, c):
        c["reserved"] = [] if self._v12 else {}
        oid = c["id"]
        for s in self.stoves:
            if s["dish"] and s["dish"].get("order_id") == oid:
                s["state"] = "idle"
                s["dish"] = None
                s["cook_ticks_left"] = 0
                s["ready_ticks"] = 0
        if self.hand and self.hand.get("order_id") == oid:
            self.hand = None
        self.customers = [x for x in self.customers if x["id"] != oid]

    def _add_reputation(self, delta):
        lo, hi = self.t["reputation_min"], self.t["reputation_max"]
        self.reputation = max(float(lo), min(float(hi), self.reputation + delta))

    def _reconcile_spoiled_reservations(self, spoiled_ids):
        if not spoiled_ids:
            return
        affected = [
            c for c in self.customers
            if c["order_status"] == "reserved" and any(iid in spoiled_ids for iid in c["reserved"])
        ]
        if not affected:
            return
        # 1. Nhả toàn bộ phần giữ của các đơn bị ảnh hưởng
        for c in affected:
            c["reserved"] = []
        # 2. Thử giữ lại 1 lần theo thứ tự (order_tick, id bàn)
        taken = self._reserved_id_set()
        for c in sorted(affected, key=lambda x: (x["order_tick"], id_key(x["table_id"]))):
            picked = self._pick_reserve_ids(c["dish_id"], taken)
            if picked is None:
                c["order_status"] = "unfulfillable"
            else:
                c["reserved"] = picked
                taken.update(picked)

    def _handle_interact(self, events):
        r = self.t["interact_radius"]
        candidates = []
        for s in self.stoves:
            dist = math.hypot(s["pos"][0] - self.pos[0], s["pos"][1] - self.pos[1])
            if dist <= r:
                candidates.append((dist, 0, id_key(s["id"]), "stove", s))
        for tb in self.tables:
            dist = math.hypot(tb["pos"][0] - self.pos[0], tb["pos"][1] - self.pos[1])
            if dist <= r:
                candidates.append((dist, 1, id_key(tb["id"]), "table", tb))
        if not candidates:
            return
        candidates.sort(key=lambda item: (item[0], item[1], item[2]))
        _, _, _, kind, obj = candidates[0]

        if kind == "stove":
            s = obj
            if s["state"] == "idle":
                waiting_reserved = [c for c in self.customers if c["order_status"] == "reserved"]
                if not waiting_reserved:
                    return
                waiting_reserved.sort(key=lambda c: (c["order_tick"], id_key(c["table_id"])))
                c = waiting_reserved[0]

                if self._v12:
                    res_ids = set(c["reserved"])
                    used_items = [it for it in self.stock if it["id"] in res_ids]
                    self.stock = [it for it in self.stock if it["id"] not in res_ids]
                    c["reserved"] = []
                    avg_fresh = sum(to_fresh(it["u"]) for it in used_items) / len(used_items)
                    base_price = math.floor(self.menu[c["dish_id"]]["price"] * (avg_fresh / 100.0))
                    items = [
                        it["id"]
                        for it in sorted(used_items, key=lambda it: (it["kind"], id_key(it["id"])))
                    ]
                else:
                    recipe = dict(c["reserved"])
                    for k, qty in recipe.items():
                        self.stock[k] = self.stock.get(k, 0) - qty
                    c["reserved"] = {}
                    base_price = self.menu[c["dish_id"]]["price"]
                    items = sorted(k for k, qty in recipe.items() for _ in range(qty))

                c["order_status"] = "assigned"
                c["base_price"] = base_price
                payload = {"order_id": c["id"], "dish_id": c["dish_id"], "base_price": base_price}
                s["state"] = "cooking"
                s["dish"] = payload
                s["cook_ticks_left"] = int(round(self.menu[c["dish_id"]]["cook_s"] * TICK))
                s["ready_ticks"] = 0
                events.append(("cook_started", {
                    "stove_id": s["id"],
                    "order_id": c["id"],
                    "dish_id": c["dish_id"],
                    "items": items,
                    "base_price": base_price,
                }))
            elif s["state"] == "ready" and self.hand is None:
                payload = s["dish"]
                self.hand = payload
                s["state"] = "idle"
                s["dish"] = None
                s["cook_ticks_left"] = 0
                s["ready_ticks"] = 0
                events.append(("dish_picked", {
                    "stove_id": s["id"],
                    "order_id": payload["order_id"],
                    "dish_id": payload["dish_id"],
                }))
        else:
            tb = obj
            if self.hand is None:
                return
            c = next((x for x in self.customers if x["table_id"] == tb["id"]), None)
            if c is None or c["state"] != "waiting" or self.hand["order_id"] != c["id"]:
                return
            payload = self.hand
            self.hand = None
            patience_max = int(round(self.t["patience_s"] * TICK))
            patience_ratio = c["patience_ticks_left"] / patience_max
            base_price = payload["base_price"]
            tip = (math.floor(base_price * self.t["tip_rate"])
                   if patience_ratio >= self.t["tip_min_patience_ratio"] else 0)
            c["state"] = "eating"
            c["order_status"] = "served"
            c["eat_ticks_left"] = int(round(self.t["eat_s"] * TICK))
            c["base_price"] = base_price
            c["tip"] = tip
            events.append(("served", {
                "order_id": c["id"],
                "table_id": tb["id"],
                "dish_id": c["dish_id"],
                "patience_ticks_left": c["patience_ticks_left"],
                "base_price": base_price,
                "tip": tip,
            }))

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        stock_out = (
            [item_out(it) for it in sort_by_id(self.stock)]
            if self._v12
            else {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0}
        )
        return {
            "player": {"pos": self.pos},
            "stock": stock_out,
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers),
            "earned": self.earned,
            "reputation": self.reputation,
            "day_plan": self.day_plan,
        }

    def step(self, inp):
        events = []

        # 1. Tăng đồng hồ, hao độ tươi kho (v1.2), giảm timer ca, nấu, ăn và kiên nhẫn
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)

        if self._v12 and self.stock:
            crossed = decay_items(self.stock, self.decay_u, "stock")
            if crossed:
                for ev in crossed:
                    events.append(("spoiled", ev))
                self._reconcile_spoiled_reservations({ev["item_id"] for ev in crossed})

        for s in self.stoves:  # đã sắp theo id
            if s["state"] == "ready":
                s["ready_ticks"] += 1
            elif s["state"] == "cooking":
                s["cook_ticks_left"] = max(0, s["cook_ticks_left"] - 1)
                if s["cook_ticks_left"] == 0:
                    s["state"] = "ready"
                    s["ready_ticks"] = 0
                    events.append(("dish_ready", {
                        "stove_id": s["id"],
                        "order_id": s["dish"]["order_id"],
                        "dish_id": s["dish"]["dish_id"],
                    }))

        for c in sort_by_id(self.customers, key=lambda x: x["table_id"]):
            if c["state"] == "waiting":
                c["patience_ticks_left"] = max(0, c["patience_ticks_left"] - 1)
            elif c["state"] == "eating":
                c["eat_ticks_left"] = max(0, c["eat_ticks_left"] - 1)

        # 2. Di chuyển
        self._move(inp)

        # 3. Tối đa MỘT interact theo (khoảng cách, bếp trước bàn, id)
        if inp.pressed("interact"):
            self._handle_interact(events)

        # 4. Theo id bàn: ăn xong trả tiền; hết giờ / hết kiên nhẫn rời bàn
        for c in sort_by_id(list(self.customers), key=lambda x: x["table_id"]):
            if c["state"] == "eating":
                if c["eat_ticks_left"] <= 0 or self.time_left_ticks <= 0:
                    pay_reason = "finished_eating" if c["eat_ticks_left"] <= 0 else "closing"
                    amount = c["base_price"] + c["tip"]
                    self.money += amount
                    self.earned += amount
                    self.shift_earned += amount
                    if c["tip"] > 0:
                        self._add_reputation(self.t["tip_reputation"])
                    self.customers = [x for x in self.customers if x["id"] != c["id"]]
                    events.append(("paid", {
                        "order_id": c["id"],
                        "table_id": c["table_id"],
                        "base_price": c["base_price"],
                        "tip": c["tip"],
                        "amount": amount,
                        "reason": pay_reason,
                    }))
                continue

            if self.time_left_ticks <= 0:
                self._release_and_remove_customer(c)
                events.append(("customer_left", {
                    "order_id": c["id"],
                    "table_id": c["table_id"],
                    "reason": "closing",
                    "reputation": self.reputation,
                }))
            elif c["patience_ticks_left"] <= 0:
                self._add_reputation(self.t["left_reputation_delta"])
                self._release_and_remove_customer(c)
                events.append(("customer_left", {
                    "order_id": c["id"],
                    "table_id": c["table_id"],
                    "reason": "patience",
                    "reputation": self.reputation,
                }))

        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            score = self.earned + self.score_mult * math.floor(self.reputation)
            events.append(("quan_end", {
                "reason": "time",
                "money": self.money,
                "earned": self.earned,
                "shift_earned": self.shift_earned,
                "reputation": self.reputation,
                "score": score,
            }))
            return events

        # 5. Khách mới theo lịch (chỉ khi còn giờ và bật random_customers)
        first_ct = self.t["first_customer_tick"]
        interval_ticks = int(round(self.t["customer_interval_s"] * TICK))
        if (self.random_customers and self.phase_tick >= first_ct
                and (self.phase_tick - first_ct) % interval_ticks == 0):
            occupied = {c["table_id"] for c in self.customers}
            free_tables = [tb for tb in self.tables if tb["id"] not in occupied]
            if free_tables:
                table = free_tables[0]
                avail = self._available_stock()
                allowed_dishes = self.day_plan if self.day_plan is not None else self.menu.keys()
                cookable = [
                    dish_id for dish_id in sorted(set(allowed_dishes))
                    if all(avail.get(k, 0) >= qty for k, qty in self.menu[dish_id]["recipe"].items())
                ]
                if not cookable:
                    events.append(("no_dish", {}))
                else:
                    dish_id = self.rng.get("customer_dish").choice(cookable)
                    cid = self.ids.new("C")
                    patience_max = int(round(self.t["patience_s"] * TICK))
                    if self._v12:
                        reserved = self._pick_reserve_ids(dish_id, self._reserved_id_set())
                    else:
                        reserved = dict(self.menu[dish_id]["recipe"])
                    cust = {
                        "id": cid,
                        "table_id": table["id"],
                        "dish_id": dish_id,
                        "order_tick": self.phase_tick,
                        "state": "waiting",
                        "patience_ticks_left": patience_max,
                        "eat_ticks_left": 0,
                        "order_status": "reserved",
                        "reserved": reserved,
                        "base_price": self.menu[dish_id]["price"],
                        "tip": 0,
                    }
                    self.customers.append(cust)
                    events.append(("customer_arrived", {
                        "order_id": cid,
                        "table_id": table["id"],
                        "dish_id": dish_id,
                    }))

        return events

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
