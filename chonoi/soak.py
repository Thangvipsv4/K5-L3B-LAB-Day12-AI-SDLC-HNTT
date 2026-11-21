"""Deterministic multi-day soak runner for Test Contract v1.3."""

import argparse
import json
import math
import os
import sys
import tempfile
import time

from .contract import load_contract
from .errors import BadInput
from .ids import IdAllocator
from .inputs import InputState
from .rng import Streams
from .sim.day import DaySim


def _input(move=(0.0, 0.0), *, interact=False, buy=None, shop_done=False):
    edges = {name for name, active in (("interact", interact), ("shop_done", shop_done)) if active}
    return InputState(move, {}, edges, buy=buy)


class SoakBot:
    """Fixed-policy driver: serve the seeded fixture order, then close Shop."""

    def input_for(self, day):
        phase, sim = day.phase, day.sim
        if phase == "gather":
            return _input()
        if phase == "shop":
            buy = self._upgrade_to_buy(sim)
            return _input(buy=buy, shop_done=True)
        if phase != "quan":
            raise BadInput(f"phase soak khÃ´ng há»— trá»£: {phase}")

        if not sim.customers:
            return _input()
        customer = sim.customers[0]
        if customer["state"] == "eating":
            return _input()
        if sim.hand is not None:
            target = next(t["pos"] for t in sim.tables if t["id"] == customer["table_id"])
        else:
            stove = next((s for s in sim.stoves
                          if s.get("dish") and s["dish"].get("order_id") == customer["id"]), None)
            if stove is None:
                stove = next((s for s in sim.stoves if s["state"] == "idle"), None)
            if stove is None:
                return _input()
            target = stove["pos"]
            if stove["state"] == "cooking":
                return _input()

        move, in_range = self._navigate(sim, target)
        stopped = math.hypot(*sim.vel) <= 0.08
        return _input(move, interact=in_range and stopped)

    @staticmethod
    def _navigate(sim, target):
        dx, dz = target[0] - sim.pos[0], target[1] - sim.pos[1]
        distance = math.hypot(dx, dz)
        if distance <= 0.9:
            return (0.0, 0.0), True
        return (dx / distance, dz / distance), False

    @staticmethod
    def _upgrade_to_buy(shop):
        for name in ("oxygen", "hp"):
            levels = shop.t["upgrades"][name]
            current = shop.upgrades.get(name, 0)
            if current < len(levels) and shop.money >= levels[current]["price"]:
                return name
        return None


def _day_fixture(tuning, plan, day_number, state, ids):
    hold = []
    for kind, quantity in plan["ingredients"].items():
        for _ in range(quantity):
            hold.append({"id": ids.new("I"), "kind": kind, "fresh": 100.0})
    dish_id = sorted(plan["dishes"])[0]
    customer = {
        "id": ids.new("C"),
        "table_id": "T1",
        "dish_id": dish_id,
        "order_tick": 0,
        "state": "waiting",
        "patience_ticks_left": int(round(tuning["quan"]["patience_s"] * 60)),
        "eat_ticks_left": 0,
        "order_status": "reserved",
    }
    return {
        "day": {
            "money": state["money"],
            "earned": state["earned"],
            "reputation": state["reputation"],
            "upgrades": dict(state["upgrades"]),
            "day_plan": {"1": {"dishes": dict(plan["dishes"]),
                                 "ingredients": dict(plan["ingredients"])}},
        },
        "gather": {"hold": hold, "random_fish": False, "time_left_ticks": 1},
        "quan": {"random_customers": False, "time_left_ticks": 1800,
                 "customers": [customer]},
    }


def _atomic_json(path, payload):
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(prefix=".soak-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        os.replace(tmp_path, path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def run_soak(seed, days, out_path):
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 10:
        raise BadInput("--days phải là số nguyên trong [1, 10]")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise BadInput("--seed phải là số nguyên")

    contract = load_contract()
    tuning = contract["tuning"]
    plans = tuning["day_plan"]
    streams, ids = Streams(seed), IdAllocator()
    state = {"money": 0, "earned": 0,
             "reputation": tuning["quan"]["reputation_initial"], "upgrades": {}}
    results = []
    crashes = 0
    bot = SoakBot()
    started = time.perf_counter()

    for day_number in range(1, days + 1):
        try:
            plan_index = (day_number - 1) % 5
            fixture = _day_fixture(tuning, plans[plan_index], day_number, state, ids)
            sim = DaySim(tuning, fixture, streams, ids, days=1)
            steps = 0
            while not sim.done:
                sim.step(bot.input_for(sim))
                steps += 1
                if steps > 5000:
                    raise RuntimeError(f"day {day_number} exceeded 5000 deterministic ticks")
            if sim.reason != "days_complete" or sim.days_completed != 1:
                raise RuntimeError(f"day {day_number} ended unexpectedly: {sim.reason}")
            state = {"money": sim.money, "earned": sim.earned,
                     "reputation": sim.reputation, "upgrades": dict(sim.upgrades)}
            score = state["earned"] + tuning["score"]["reputation_multiplier"] * math.floor(state["reputation"])
            results.append({"day": day_number, "earned": state["earned"],
                            "reputation": state["reputation"], "score": score})
        except Exception as exc:
            crashes += 1
            sys.stderr.write(f"soak day {day_number} failed: {type(exc).__name__}: {exc}\n")
            break

    payload = {
        "days": days,
        "days_completed": len(results),
        "crashes": crashes,
        "results": results,
        "duration_s": round(time.perf_counter() - started, 6),
    }
    _atomic_json(out_path, payload)
    return payload


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"error: {message}\n")
        raise SystemExit(2)


def main(argv=None):
    parser = _Parser(prog="chonoi.soak")
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--days", required=True, type=int)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        result = run_soak(args.seed, args.days, args.out)
    except BadInput as exc:
        sys.stderr.write(f"invalid input: {exc}\n")
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if result["crashes"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
