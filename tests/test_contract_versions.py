"""Checks the archived Phase 3 v1.2 contract without changing runtime v1.3."""

import copy
import json
import os
import unittest

from chonoi.contract import load_contract


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V12_PATH = os.path.join(ROOT, "docs", "contracts", "game.contract.v1.2.json")
ACTIVE_PATH = os.path.join(ROOT, "game.contract.json")


class ContractVersionSnapshot(unittest.TestCase):
    def test_v12_snapshot_matches_phase2_tuning_plus_phase3_freshness(self):
        with open(V12_PATH, encoding="utf-8") as stream:
            v12 = json.load(stream)
        with open(ACTIVE_PATH, encoding="utf-8") as stream:
            active = json.load(stream)

        expected = copy.deepcopy(active)
        expected["contract_version"] = "1.2"
        expected.pop("bench_cmd", None)
        expected.pop("soak_cmd", None)
        self.assertEqual(v12, expected)
        self.assertEqual(v12["contract_version"], "1.2")
        self.assertEqual(v12["tuning"]["freshness"], {
            "initial": 100,
            "gather_decay_per_s": 0.5,
            "quan_decay_per_s": 0.25,
            "spoiled_below": 30,
        })
        load_contract(V12_PATH)

    def test_runtime_manifest_remains_v13(self):
        active = load_contract(ACTIVE_PATH)
        self.assertEqual(active["contract_version"], "1.3")
        self.assertEqual(active["soak_cmd"], "python3 -m chonoi.soak")


if __name__ == "__main__":
    unittest.main()
