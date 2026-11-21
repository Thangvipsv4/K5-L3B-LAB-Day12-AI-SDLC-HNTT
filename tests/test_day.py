"""Unit and black-box integration coverage for Phase 2 day/shop/pause."""

import os
import unittest
from unittest.mock import patch

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.inputs import InputPlayer, InputState, LiveInputs, load_frames
from chonoi.runner import Session
from chonoi.sim.day import DaySim
from chonoi.sim.shop import ShopSim
from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "day_mode.json")


class State:
    def __init__(self, edges=(), move=(0.0, 0.0), buy=None):
        self._edges = set(edges)
        self.move = move
        self.buy = buy
        self.held = {}

    def pressed(self, name):
        return name in self._edges


class FakeGather:
    mode = "gather"
    phase = "gather"

    def __init__(self, tuning, scenario, streams, ids):
        self.phase_tick = 0
        self.time_left_ticks = 1
        self.done = False
        self.reason = None
        self.money = self.earned = 0
        self.reputation = tuning["quan"]["reputation_initial"]
        self._items = {kind: scenario.get("hold", []).count(kind)
                       for kind in set(scenario.get("hold", []))}

    def step(self, inp):
        self.phase_tick += 1
        self.time_left_ticks = 0
        self.done = True
        self.reason = "time"
        return [("gather_end", {"reason": "time"})]

    def inventory_items(self):
        return self._items

    def snapshot(self):
        return {"player": {}}


class FakeQuan:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        self.phase_tick = 0
        self.time_left_ticks = 1
        self.done = False
        self.reason = None
        self.money = self.earned = 0
        self.reputation = scenario["reputation"]
        self.stock = dict(inventory or {})

    def step(self, inp):
        self.phase_tick += 1
        self.time_left_ticks = 0
        self.money = self.earned = 60
        self.done = True
        self.reason = "time"
        return [("quan_end", {"reason": "time"})]

    def snapshot(self):
        return {"stock": dict(self.stock)}


class InputContract(unittest.TestCase):
    def test_v11_pause_shop_and_one_shot_buy(self):
        data = frames({"tick": 0, "pause": True},
                      {"tick": 1, "pause": False, "buy": "oxygen"},
                      {"tick": 2, "shop_done": True})
        with Workdir() as w:
            path = write_json(w.path("inputs.json"), data)
            player = InputPlayer(load_frames(path))
        self.assertTrue(player.advance(0).pressed("pause"))
        self.assertEqual(player.advance(1).buy, "oxygen")
        self.assertTrue(player.advance(2).pressed("shop_done"))

    def test_buy_must_be_nonempty_string(self):
        with Workdir() as w:
            path = write_json(w.path("inputs.json"), frames({"tick": 0, "buy": ""}))
            with self.assertRaises(BadInput):
                load_frames(path)

    def test_live_shop_action_is_delivered_once(self):
        inputs = LiveInputs()
        inputs.set_buy("hp")
        self.assertEqual(inputs.advance().buy, "hp")
        self.assertIsNone(inputs.advance().buy)


class ShopRules(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def test_buy_success_funds_max_and_unknown(self):
        shop = ShopSim(self.tuning, day=1, money=200, upgrades={}, stock={"ca_loc": 2})
        ev = shop.step(State(buy="oxygen"))
        self.assertEqual(ev[0], ("bought", {"upgrade": "oxygen", "level": 1, "price": 200, "money": 0}))
        self.assertEqual(shop.stock, {"ca_loc": 2})
        self.assertEqual(shop.step(State(buy="oxygen"))[0][1]["reason"], "funds")
        shop.money = 500
        shop.upgrades["oxygen"] = 2
        self.assertEqual(shop.step(State(buy="oxygen"))[0][1]["reason"], "max_level")
        self.assertEqual(shop.step(State(buy="laser"))[0][1]["reason"], "unknown")

    def test_hp_upgrade_purchase(self):
        shop = ShopSim(self.tuning, day=1, money=250, upgrades={}, stock={})
        self.assertEqual(shop.step(State(buy="hp"))[0],
                         ("bought", {"upgrade": "hp", "level": 1, "price": 250, "money": 0}))

    def test_individual_stock_keeps_id_and_freshness(self):
        original = [{"id": "I7", "kind": "ca_loc", "fresh": 98.5}]
        shop = ShopSim(self.tuning, day=1, money=0, upgrades={}, stock=original)
        self.assertEqual(shop.snapshot()["stock"], original)
        shop.step(State(edges={"shop_done"}))
        self.assertEqual(shop.stock[0]["id"], "I7")
        self.assertEqual(shop.snapshot()["stock"][0]["fresh"], 98.5)

    def test_shop_expires_after_exactly_600_active_ticks(self):
        shop = ShopSim(self.tuning, day=1, money=0, upgrades={}, stock={})
        for _ in range(599):
            self.assertEqual(shop.step(State()), [])
        self.assertEqual(shop.time_left_ticks, 1)
        self.assertEqual(shop.step(State()), [("shop_end", {"reason": "time"})])
        self.assertEqual(shop.phase_tick, 600)


class PauseRules(unittest.TestCase):
    def test_pause_freezes_and_resume_continues_phase_timer(self):
        tuning = load_contract()["tuning"]
        sess = Session("gather", tuning, {"time_left_ticks": 3}, seed=4)
        self.assertEqual([r["name"] for r in sess.step(State(edges={"pause"}))], ["paused"])
        paused = sess.snapshot()
        self.assertEqual((paused["state"], paused["tick"], paused["sim_tick"],
                          paused["phase_tick"], paused["time_left_ticks"]), ("paused", 1, 0, 0, 3))
        self.assertEqual(sess.step(State()), [])
        self.assertEqual(sess.snapshot()["time_left_ticks"], 3)
        self.assertEqual([r["name"] for r in sess.step(State(edges={"pause"}))], ["resumed"])
        resumed = sess.snapshot()
        self.assertEqual((resumed["state"], resumed["tick"], resumed["sim_tick"],
                          resumed["phase_tick"], resumed["time_left_ticks"]), ("playing", 3, 1, 1, 2))


class DayOrchestration(unittest.TestCase):
    def test_day_count_is_limited_to_one_through_five(self):
        with Workdir() as w:
            for count in ("0", "6"):
                self.assertEqual(run_headless("--mode", "day", "--days", count, "--seed", "1",
                                              "--ticks", "0", "--out", w.path(f"{count}.jsonl"))[0], 2)

    def test_orchestrator_uses_child_protocol_and_applies_upgrade_next_day(self):
        tuning = load_contract()["tuning"]
        scenario = {"day": {"money": 200, "earned": 200},
                    "gather": {"hold": ["ca_loc"], "random_fish": False}, "quan": {}}
        with patch("chonoi.sim.day.GatherSim", FakeGather), patch("chonoi.sim.day.QuanSim", FakeQuan):
            sim = DaySim(tuning, scenario, None, None, days=2)
            self.assertEqual([ev[0] for ev in sim.initial_events], ["day_start", "day_plan", "phase_start"])
            sim.step(State())
            self.assertEqual(sim.phase, "quan")
            sim.step(State())
            self.assertEqual(sim.phase, "shop")
            bought = sim.step(State(buy="oxygen"))
            self.assertEqual(bought[0][0], "bought")
            self.assertEqual((sim.snapshot()["upgrades"]["oxygen"],
                              sim.snapshot()["active_upgrades"].get("oxygen", 0)), (1, 0))
            sim.step(State(edges={"shop_done"}))
            self.assertEqual((sim.day, sim.days_completed, sim.active_upgrades["oxygen"]), (2, 1, 1))
            sim.step(State())
            sim.step(State())
            sim.step(State(edges={"shop_done"}))
            self.assertTrue(sim.done)
            self.assertEqual((sim.reason, sim.days_completed), ("days_complete", 2))

    def test_headless_fixture_hands_off_stock_and_runs_two_days(self):
        with Workdir() as w:
            inputs = write_json(w.path("inputs.json"), frames(
                {"tick": 2, "pause": True},
                {"tick": 3, "pause": False},
                {"tick": 4, "pause": True},
                {"tick": 5, "buy": "oxygen"},
                {"tick": 6, "shop_done": True},
                {"tick": 7, "shop_done": False},
                {"tick": 10, "shop_done": True},
            ))
            out = w.path("day.jsonl")
            code, err = run_headless("--mode", "day", "--days", "2", "--seed", "17",
                                     "--ticks", "12", "--scenario", FIXTURE,
                                     "--inputs", inputs, "--snapshot-every", "1", "--out", out)
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
        self.assertEqual([e["day"] for e in events(rows, "day_start")], [1, 2])
        self.assertEqual(len(events(rows, "bought")), 1)
        self.assertEqual([e["name"] for e in events(rows) if e["name"] in ("paused", "resumed")],
                         ["paused", "resumed"])
        paused_shop = [s for s in snapshots(rows) if s["phase"] == "shop" and s["state"] == "paused"]
        self.assertTrue(paused_shop)
        self.assertEqual(paused_shop[0]["time_left_ticks"], 600)
        self.assertEqual(events(rows, "bought")[0]["data"]["upgrade"], "oxygen")
        day2 = [s for s in snapshots(rows) if s.get("day") == 2 and s["phase"] == "gather"]
        self.assertTrue(day2)
        self.assertEqual(day2[0]["active_upgrades"]["oxygen"], 1)
        self.assertEqual(day2[0]["player"]["oxygen_max_ticks"], 2700)
        self.assertEqual(rows[-1]["reason"], "days_complete")
        self.assertEqual(rows[-1]["days_completed"], 2)


if __name__ == "__main__":
    unittest.main()
