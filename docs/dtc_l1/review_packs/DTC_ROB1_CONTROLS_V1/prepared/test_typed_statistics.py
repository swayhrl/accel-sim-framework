"""PREPARED_NOT_TESTED; coordinator authority/role admission required."""
import copy
import unittest
from typed_statistics import summarize, UNAVAILABLE


def record():
    return {"qualified_terminal": True,
            "snapshot": "LAST_COMPLETE_CUMULATIVE_ALL_64_SMS",
            "bindings": {"source_commit": "1" * 40, "stdout_sha256": "2" * 64,
                         "qualification_receipt_sha256": "3" * 64},
            "ad_enabled": True,
            "service": {"retired": 2, "fully_ready_to_complete_sum": 12,
                        "ready_to_collect_sum": 4, "collection_cycles": 6,
                        "wb_wait": 2},
            "ad": {"retired": 2, "admitted_returns_to_retire_sum": 20,
                   "broadcasts": 2, "span_sum": 3,
                   "first_notify_cycle_sum": 10, "last_notify_cycle_sum": 13,
                   "fanout_histogram": [0, 1] + [0] * 30 + [1]}}


class StatisticsTests(unittest.TestCase):
    def test_on_typed_and_capped_fanout(self):
        result = summarize(record())
        self.assertEqual(result["admitted_returns_to_retire_mean"],
                         {"numerator": 10, "denominator": 1})
        self.assertEqual(result["fanout_histogram"]["last_bin"], ">=32")

    def test_off_absence_and_zero_denominator(self):
        value = record(); value["ad_enabled"] = False; value.pop("ad")
        value["service"]["retired"] = 0
        result = summarize(value)
        self.assertEqual(result["admitted_returns_to_retire_mean"], UNAVAILABLE)
        self.assertEqual(result["means"]["collection_cycles"],
                         "UNDEFINED_ZERO_DENOMINATOR")
        value["service"].pop("wb_wait")
        self.assertEqual(summarize(value)["means"]["wb_wait"], UNAVAILABLE)

    def test_invalid_populations_snapshots_and_nonintegers_fail(self):
        for change in (lambda r: r.update(qualified_terminal=False),
                       lambda r: r.update(snapshot="PER_KERNEL_CUMULATIVE"),
                       lambda r: r["ad"].update(broadcasts=3),
                       lambda r: r["ad"].update(retired=3),
                       lambda r: r["ad"].update(last_notify_cycle_sum=14),
                       lambda r: r["service"].update(wb_wait=True),
                       lambda r: r["service"].update(collection_cycles=7),
                       lambda r: r["bindings"].update(source_commit="HEAD")):
            value = copy.deepcopy(record()); change(value)
            with self.assertRaises(ValueError): summarize(value)


if __name__ == "__main__": unittest.main()
