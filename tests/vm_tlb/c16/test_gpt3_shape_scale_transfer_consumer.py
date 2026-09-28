import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[3] / "util/vm_tlb/c16/gpt3_shape_scale_transfer_consumer.py"
SPEC = importlib.util.spec_from_file_location("consumer", SCRIPT)
consumer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(consumer)


class ConsumerTests(unittest.TestCase):
    def test_gpt3_expand_static_math(self):
        row = consumer.gpt3_static(consumer.GPT3["EXPAND_M256"])
        self.assertEqual(row["parameter_count"], 603_979_776)
        self.assertEqual(row["qweight_bytes"], 301_989_888)
        self.assertEqual(row["split1_gemm_grid"], 6144)
        self.assertEqual(row["split8_gemm_grid"], 49152)
        self.assertEqual(row["split8_scratch_bytes"], 201_326_592)

    def test_gpt3_contract_static_math(self):
        row = consumer.gpt3_static(consumer.GPT3["CONTRACT_M1"])
        self.assertEqual(row["dense_fp16_bytes"], 1_207_959_552)
        self.assertEqual(row["qzeros_bytes"], 2_359_296)
        self.assertEqual(row["scales_bytes"], 9_437_184)
        self.assertEqual(row["split1_gemm_grid"], 96)
        self.assertEqual(row["split8_reduction_grid"], 24)


if __name__ == "__main__":
    unittest.main()
