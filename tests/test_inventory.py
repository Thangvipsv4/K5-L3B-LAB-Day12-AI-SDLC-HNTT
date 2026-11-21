"""Unit coverage for the additive Phase 3 individual inventory adapter."""

import os
import unittest
from copy import deepcopy

from chonoi.contract import load_contract, validate_tuning
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inventory import (
    FRESH_U, SPOIL_U, decay_items, item_in, item_out, new_item, read_items,
    to_fresh, to_units, validate_item_list, write_items,
)
from chonoi.scenario import load_scenario
from helpers import Workdir, write_json


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ItemSchema(unittest.TestCase):
    def setUp(self):
        self.valid = [
            {"id": "I2", "kind": "ca_loc", "fresh": 97.5},
            {"id": "I1", "kind": "ca_linh", "fresh": 100},
        ]

    def test_round_trip_item_file_sorts_by_numeric_id(self):
        with Workdir() as w:
            path = w.path("items.json")
            write_items(path, self.valid)
            self.assertEqual(read_items(path), [self.valid[1], self.valid[0]])

    def test_reject_count_schema_unknown_kind_duplicate_id_and_bad_freshness(self):
        cases = (
            {"ca_loc": 2},
            [{"id": "I1", "kind": "unknown", "fresh": 100}],
            [{"id": "I1", "kind": "ca_loc", "fresh": 100},
             {"id": "I1", "kind": "ca_linh", "fresh": 99}],
            [{"id": "I1", "kind": "ca_loc", "fresh": 100.1}],
            [{"id": "I1", "kind": "ca_loc", "fresh": float("nan")}],
        )
        for data in cases:
            with self.subTest(data=data), self.assertRaises(BadInput):
                validate_item_list(data)

    def test_fraction_conversion_preserves_threshold_neighbor(self):
        self.assertEqual(to_units(30), SPOIL_U)
        self.assertEqual(to_units(30.004166666666666), SPOIL_U + 1)
        self.assertEqual(to_fresh(SPOIL_U + 1), 30.004166666666666)
        self.assertEqual(to_fresh(FRESH_U), 100.0)
        self.assertEqual(to_units(30.001), SPOIL_U)  # nearest internal 1/240 unit

    def test_internal_units_never_leak_in_public_shape(self):
        item = item_in(self.valid[0])
        self.assertEqual(set(item), {"id", "kind", "u"})
        self.assertEqual(item_out(item), self.valid[0])

    def test_ids_are_unique_across_allocator_phases_and_shop_items(self):
        ids = IdAllocator()
        initial = new_item("ca_loc", ids)
        ids.reserve(initial["id"])
        next_day = new_item("ca_linh", ids)
        shop_item = new_item("bong_sung", ids)
        self.assertEqual([initial["id"], next_day["id"], shop_item["id"]], ["I1", "I2", "I3"])

    def test_decay_clamps_and_emits_spoilage_once_in_id_order(self):
        items = [item_in({"id": "I2", "kind": "ca_loc", "fresh": 30}),
                 item_in({"id": "I1", "kind": "ca_linh", "fresh": 30})]
        first = decay_items(items, 1, "stock")
        self.assertEqual([event["item_id"] for event in first], ["I1", "I2"])
        self.assertEqual([event["location"] for event in first], ["stock", "stock"])
        self.assertEqual(decay_items(items, 1, "stock"), [])
        self.assertEqual(decay_items(items, FRESH_U, "hold"), [])
        self.assertEqual([item["u"] for item in items], [0, 0])


class V12Scenario(unittest.TestCase):
    def setUp(self):
        self.tuning = deepcopy(load_contract()["tuning"])
        self.tuning["freshness"] = {
            "initial": 100, "gather_decay_per_s": 0.5,
            "quan_decay_per_s": 0.25, "spoiled_below": 30,
        }

    def test_freshness_tuning_contract_values_and_validation(self):
        validate_tuning(self.tuning)
        invalid = deepcopy(self.tuning)
        invalid["freshness"]["spoiled_below"] = 31
        with self.assertRaises(BadInput):
            validate_tuning(invalid)

    def test_gather_scenario_accepts_individual_items(self):
        scenario = {"gather": {"hold": [
            {"id": "I1", "kind": "ca_loc", "fresh": 100}], "random_fish": False}}
        with Workdir() as w:
            path = write_json(w.path("scenario.json"), scenario)
            loaded = load_scenario(path, "gather", self.tuning)
        self.assertEqual(loaded["hold"][0]["id"], "I1")

    def test_quan_scenario_validates_item_stock_and_reserved_references(self):
        scenario = {"quan": {"stock": [
            {"id": "I1", "kind": "ca_loc", "fresh": 100}],
            "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                           "reserved": ["I1"]}]}}
        with Workdir() as w:
            path = write_json(w.path("scenario.json"), scenario)
            loaded = load_scenario(path, "quan", self.tuning)
        self.assertEqual(loaded["customers"][0]["reserved"], ["I1"])

    def test_quan_rejects_reserved_unknown_or_spoiled_item(self):
        for ident, freshness in (("missing", 100), ("I1", 29.9)):
            scenario = {"quan": {"stock": [{"id": "I1", "kind": "ca_loc", "fresh": 100}],
                                  "customers": [{"id": "C1", "table_id": "T1",
                                                 "dish_id": "ca_loc_nuong_trui",
                                                 "reserved": [ident]}]}}
            if freshness < 30:
                scenario["quan"]["stock"][0]["fresh"] = freshness
            with self.subTest(ident=ident, freshness=freshness), Workdir() as w:
                path = write_json(w.path("scenario.json"), scenario)
                with self.assertRaises(BadInput):
                    load_scenario(path, "quan", self.tuning)


if __name__ == "__main__":
    unittest.main()
