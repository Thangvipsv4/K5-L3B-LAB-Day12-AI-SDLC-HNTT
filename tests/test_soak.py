"""Contract and black-box unit tests for deterministic Phase 4 soak runs."""

import json
import unittest
from copy import deepcopy
from unittest.mock import patch

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.soak import _day_fixture, run_soak
from chonoi.ids import IdAllocator
from helpers import Workdir, write_json


class SoakContractTests(unittest.TestCase):
    def test_v13_declares_soak_and_renderer_benchmark_commands(self):
        contract = load_contract()
        self.assertEqual(contract["contract_version"], "1.3")
        self.assertEqual(contract["soak_cmd"], "python3 -m chonoi.soak")
        self.assertEqual(contract["bench_cmd"], "python3 -m chonoi.bench")

    def test_v13_contract_requires_both_command_fields(self):
        contract = load_contract()
        with Workdir() as work:
            for missing in ("bench_cmd", "soak_cmd"):
                bad = deepcopy(contract)
                del bad[missing]
                with self.subTest(missing=missing):
                    with self.assertRaises(BadInput):
                        load_contract(write_json(work.path(f"missing-{missing}.json"), bad))
            bad = deepcopy(contract)
            bad["soak_cmd"] = " "
            with self.assertRaises(BadInput):
                load_contract(write_json(work.path("empty-soak.json"), bad))

    def test_rejects_days_outside_ten_day_contract(self):
        with Workdir() as work:
            for days in (0, 11, True):
                with self.subTest(days=days), self.assertRaises(BadInput):
                    run_soak(7, days, work.path("invalid.json"))


class SoakRunTests(unittest.TestCase):
    def run_result(self, seed, path):
        payload = run_soak(seed, 10, path)
        with open(path, encoding="utf-8") as stream:
            on_disk = json.load(stream)
        self.assertEqual(payload, on_disk)
        self.assertEqual(set(on_disk), {"days", "days_completed", "crashes", "results", "duration_s"})
        self.assertEqual(on_disk["days"], 10)
        self.assertEqual(on_disk["days_completed"], 10)
        self.assertEqual(on_disk["crashes"], 0)
        self.assertEqual(len(on_disk["results"]), 10)
        for day, result in enumerate(on_disk["results"], 1):
            self.assertEqual(set(result), {"day", "earned", "reputation", "score"})
            self.assertEqual(result["day"], day)
        return on_disk

    def test_ten_day_soak_completes_all_phases_and_carries_ledger(self):
        with Workdir() as work:
            states, item_ids, customer_ids = [], [], []
            original = _day_fixture

            def record(tuning, plan, day_number, state, ids):
                fixture = original(tuning, plan, day_number, state, ids)
                states.append(dict(state, upgrades=dict(state["upgrades"])))
                item_ids.extend(item["id"] for item in fixture["gather"]["hold"])
                customer_ids.append(fixture["quan"]["customers"][0]["id"])
                return fixture

            with patch("chonoi.soak._day_fixture", side_effect=record):
                result = self.run_result(7, work.path("soak.json"))

        self.assertEqual(len(set(item_ids)), len(item_ids))
        self.assertEqual(len(set(customer_ids)), 10)
        self.assertTrue(all(item_id.startswith("I") for item_id in item_ids))
        self.assertEqual(result["results"][5]["earned"] - result["results"][4]["earned"],
                         result["results"][0]["earned"])
        self.assertGreater(result["results"][-1]["earned"], result["results"][0]["earned"])
        self.assertGreaterEqual(result["results"][-1]["reputation"], result["results"][0]["reputation"])
        self.assertTrue(any(state["upgrades"] for state in states))

    def test_identical_seed_repeats_gameplay_results(self):
        with Workdir() as work:
            first = self.run_result(7, work.path("first.json"))
            second = self.run_result(7, work.path("second.json"))
        self.assertEqual(first["results"], second["results"])
        self.assertEqual(first["crashes"], second["crashes"])

    def test_day_plan_fixture_repeats_the_five_contract_days(self):
        contract = load_contract()
        plans = contract["tuning"]["day_plan"]
        allocator = IdAllocator()
        state = {"money": 0, "earned": 0, "reputation": 3, "upgrades": {}}
        observed = []
        for day_number in range(1, 11):
            plan = plans[(day_number - 1) % 5]
            fixture = _day_fixture(contract["tuning"], plan, day_number, state, allocator)
            observed.append(fixture["day"]["day_plan"]["1"])
        self.assertEqual(observed[:5], observed[5:])


if __name__ == "__main__":
    unittest.main()
