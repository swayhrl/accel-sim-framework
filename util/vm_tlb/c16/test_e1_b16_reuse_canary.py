#!/usr/bin/env python3
import importlib.util
from importlib.machinery import SourceFileLoader
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("e1_b16_reuse_canary.py")
SPEC = importlib.util.spec_from_loader(
    "e1_b16_reuse_canary", SourceFileLoader("e1_b16_reuse_canary", str(MODULE_PATH))
)
CANARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CANARY)


class B16ReuseCanaryTest(unittest.TestCase):
    def test_parse_output_and_diagnostics(self):
        text = """launching kernel name: kernel_a uid: 1 cuda_stream_id: 0
gpu_tot_sim_cycle = 10
gpu_tot_sim_insn = 20
gpu_tot_issued_cta = 2
oracle_elastic_l2\tinstance=0\tquota=4\toccupancy=1
oracle_elastic_l2_class_occupancy\tinstance=0\tclass_1=1\tclass_2=0
launching kernel name: kernel_b uid: 2 cuda_stream_id: 0
gpu_tot_sim_cycle = 15
gpu_tot_sim_insn = 25
gpu_tot_issued_cta = 3
GPGPU-Sim: *** exit detected ***
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "simulator.stdout"
            path.write_text(text, encoding="utf-8")
            parsed = CANARY.parse_simulator_output(path, True)
        self.assertTrue(parsed["terminal"])
        self.assertEqual([row["uid"] for row in parsed["launches"]], [1, 2])
        self.assertEqual(parsed["completed"][2]["gpu_tot_sim_cycle"], 15)
        self.assertEqual(parsed["diagnostics"][1][0]["occupancy"], 1)
        self.assertEqual(parsed["class_occupancy"][1][0]["class_1"], 1)

    def test_response_sign(self):
        result = CANARY.response(100, 90)
        self.assertEqual(result["R0_minus_M1_cycles"], 10)
        self.assertAlmostEqual(result["response_fraction"], 0.1)

    def test_malformed_diagnostic_fails_closed(self):
        with self.assertRaises(CANARY.ContractError):
            CANARY.parse_key_values("oracle_elastic_l2\tinstance=bad", "oracle_elastic_l2")


if __name__ == "__main__":
    unittest.main()
