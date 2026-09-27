#!/usr/bin/env python3
import hashlib
import unittest

from gpgpusim_host_acceleration_v1 import normalized_stdout, speedup


class HostAccelerationAnalysisTest(unittest.TestCase):
    def test_normalization_is_path_and_host_observation_only(self):
        left = [
            "Accel-Sim [build one]",
            "  *** GPGPU-Sim Simulator Version 4 [build one] ***",
            "-trace /remote/kernelslist.g # traces",
            "-enable_ptx_file_line_stats 1 # stat",
            "Header info loaded for kernel command : /remote/kernel-1.traceg.xz",
            "Processing kernel /remote/kernel-1.traceg.xz",
            "gpu_total_sim_rate=10",
            "gpgpu_simulation_time = 1 sec",
            "gpgpu_simulation_rate = 10",
            "gpgpu_silicon_slowdown = 20x",
            "L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT] = 7",
        ]
        right = [
            "Accel-Sim [build two]",
            "  *** GPGPU-Sim Simulator Version 4 [build two] ***",
            "-trace /dev/shm/kernelslist.g # traces",
            "-enable_ptx_file_line_stats 0 # stat",
            "Header info loaded for kernel command : /dev/shm/kernel-1.traceg.xz",
            "Processing kernel /dev/shm/kernel-1.traceg.xz",
            "gpu_total_sim_rate=99",
            "gpgpu_simulation_time = 9 sec",
            "gpgpu_simulation_rate = 99",
            "gpgpu_silicon_slowdown = 99x",
            "L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT] = 7",
        ]
        self.assertEqual(normalized_stdout(left), normalized_stdout(right))
        right[-1] = "L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT] = 8"
        self.assertNotEqual(
            hashlib.sha256(normalized_stdout(left)).hexdigest(),
            hashlib.sha256(normalized_stdout(right)).hexdigest(),
        )

    def test_speedup_sign(self):
        self.assertAlmostEqual(speedup(10.0, 9.0), 0.1)
        self.assertAlmostEqual(speedup(10.0, 11.0), -0.1)


if __name__ == "__main__":
    unittest.main()
