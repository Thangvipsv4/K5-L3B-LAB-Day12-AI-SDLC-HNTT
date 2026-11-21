"""Multi-day orchestrator for Contract v1.1; children own their phase rules."""

from copy import deepcopy

from ..errors import BadInput
from .gather import GatherSim
from .quan import QuanSim
from .shop import ShopSim


class DaySim:
    mode = "day"

    def __init__(self, tuning, scenario, streams, ids, *, days=1):
        if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 5:
            raise BadInput("--days phải là số nguyên từ 1 đến 5")
        self.tuning = tuning
        self.scenario = scenario
        self.streams = streams
        self.ids = ids
        self.days = days
        state = scenario.get("day", {})
        self.money = state.get("money", 0)
        self.earned = state.get("earned", 0)
        self.reputation = float(state.get("reputation", tuning["quan"]["reputation_initial"]))
        self.upgrades = dict(state.get("upgrades", {}))
        self.active_upgrades = dict(self.upgrades)
        self.plan_overrides = state.get("day_plan", {})
        if isinstance(self.plan_overrides, list):
            self.plan_overrides = {str(plan["day"]): plan for plan in self.plan_overrides}
        self.day = 1
        self.days_completed = 0
        self.done = False
        self.reason = None
        self.initial_events = []
        self.plan = self._get_plan()
        self._start_day(self.initial_events)

    @property
    def phase(self):
        return self.sim.phase

    @property
    def phase_tick(self):
        return self.sim.phase_tick

    @property
    def time_left_ticks(self):
        return self.sim.time_left_ticks

    def _get_plan(self):
        plan = self.plan_overrides.get(str(self.day), self.plan_overrides.get(self.day))
        if plan is None:
            plan = next(p for p in self.tuning["day_plan"] if p["day"] == self.day)
        return {"dishes": deepcopy(plan["dishes"]), "ingredients": deepcopy(plan["ingredients"])}

    def _tuning_for_day(self):
        tuned = deepcopy(self.tuning)
        for name, field in (("oxygen", "oxygen_max_s"), ("hp", "hp_max")):
            level = self.active_upgrades.get(name, 0)
            if level:
                tuned["gather"][field] = tuned["shop"]["upgrades"][name][level - 1][field]
        return tuned

    def _start_day(self, events):
        self.plan = self._get_plan()
        gather_scenario = deepcopy(self.scenario.get("gather", {}))
        gather_scenario["day"] = self.day
        tuning = self._tuning_for_day()
        self.sim = GatherSim(tuning, gather_scenario, self.streams, self.ids)
        events.extend((("day_start", {}, "gather", self.day),
                       ("day_plan", {"dishes": deepcopy(self.plan["dishes"]),
                                      "ingredients": deepcopy(self.plan["ingredients"])}, "gather", self.day),
                       ("phase_start", {}, "gather", self.day)))

    def snapshot(self):
        snap = self.sim.snapshot()
        snap.update({"day": self.day, "day_plan": deepcopy(self.plan),
                     "upgrades": dict(self.upgrades), "active_upgrades": dict(self.active_upgrades),
                     "days_completed": self.days_completed, "money": self.money,
                     "earned": self.earned, "reputation": self.reputation})
        return snap

    def step(self, inp):
        if self.done:
            return []
        phase, day = self.phase, self.day
        events = []
        child_events = self.sim.step(inp)
        events.extend((name, data, phase, day) for name, data in child_events)
        if phase == "shop":
            self.money = self.sim.money
            self.upgrades = dict(self.sim.upgrades)

        if phase == "gather" and self.sim.done:
            stock = {} if self.sim.reason == "fainted" else self.sim.inventory_items()
            self._start_quan(stock, events)
        elif phase == "quan" and self.sim.done:
            self.money += self.sim.money
            self.earned += self.sim.earned
            self.reputation = self.sim.reputation
            self.sim = ShopSim(self.tuning, day=self.day, money=self.money,
                               upgrades=self.upgrades, stock=self.sim.stock)
            events.append(("phase_start", {}, "shop", self.day))
        elif phase == "shop" and self.sim.done:
            self.money = self.sim.money
            self.upgrades = dict(self.sim.upgrades)
            self.days_completed += 1
            if self.days_completed >= self.days:
                self.done = True
                self.reason = "days_complete"
            else:
                self.day += 1
                self.active_upgrades = dict(self.upgrades)
                self._start_day(events)
        return events

    def _start_quan(self, stock, events):
        plan_ids = set(self.plan["dishes"])
        tuning = deepcopy(self.tuning)
        tuning["menu"] = {key: value for key, value in tuning["menu"].items() if key in plan_ids}
        quan_scenario = deepcopy(self.scenario.get("quan", {}))
        quan_scenario["reputation"] = self.reputation
        self.sim = QuanSim(tuning, quan_scenario, self.streams, self.ids, inventory=stock)
        events.append(("phase_start", {}, "quan", self.day))
