"""Phase 2 Shop phase, independent from the gather and restaurant simulations."""


class ShopSim:
    mode = "shop"
    phase = "shop"

    def __init__(self, tuning, *, day, money, upgrades, stock):
        self.t = tuning["shop"]
        self.day = day
        self.money = money
        self.upgrades = dict(upgrades)
        self.stock = dict(stock)
        self.time_left_ticks = self.t["max_ticks"]
        self.phase_tick = 0
        self.done = False
        self.reason = None

    def snapshot(self):
        return {"stock": dict(self.stock)}

    def step(self, inp):
        if self.done:
            return []
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        events = []
        action = getattr(inp, "buy", None)
        if action is not None:
            levels = self.t["upgrades"].get(action)
            if levels is None:
                events.append(("buy_failed", {"action": action, "reason": "unknown"}))
            else:
                current = self.upgrades.get(action, 0)
                if current >= len(levels):
                    events.append(("buy_failed", {"action": action, "reason": "max_level"}))
                else:
                    upgrade = levels[current]
                    if self.money < upgrade["price"]:
                        events.append(("buy_failed", {"action": action, "reason": "funds"}))
                    else:
                        self.money -= upgrade["price"]
                        self.upgrades[action] = current + 1
                        events.append(("bought", {"upgrade": action, "level": current + 1,
                                                   "price": upgrade["price"], "money": self.money}))
        if getattr(inp, "pressed", lambda _name: False)("shop_done"):
            self._finish("done", events)
        elif self.time_left_ticks <= 0:
            self._finish("time", events)
        return events

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        events.append(("shop_end", {"reason": reason}))
