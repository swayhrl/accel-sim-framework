#!/usr/bin/env python3
import unittest
from footprint_audit import N, footprint, k_tiles, point_contracts

class FootprintTests(unittest.TestCase):
    def test_mod8_tiles_and_metadata_halves(self):
        sets=[set(k_tiles(12288,8,z)) for z in range(8)]
        self.assertTrue(all(all(tile%8==z for tile in sets[z]) for z in range(8)))
        self.assertTrue(all(not (sets[i]&sets[j]) for i in range(8) for j in range(i+1,8)))
        groups=[{tile//4 for tile in values} for values in sets]
        self.assertTrue(all(groups[i]==groups[0] for i in range(4)))
        self.assertTrue(all(groups[i]==groups[4] for i in range(4,8)))
        self.assertTrue(groups[0].isdisjoint(groups[4]))

    def test_exact_gpt3_footprints(self):
        expected={2048:(52_297_728,7_274_496),2560:(65_372_160,9_093_120),3072:(78_446_592,10_911_744),4096:(104_595_456,14_548_992),12288:(313_786_368,43_646_976)}
        for k,(whole,split) in expected.items():
            self.assertEqual(footprint(k,N,1,0)["total_unique_bytes"],whole)
            self.assertTrue(all(footprint(k,N,8,z)["total_unique_bytes"]==split for z in range(8)))

    def test_old_qwen_full_footprint(self):
        self.assertEqual(footprint(3584,18944,1,0)["total_unique_bytes"],35_273_728)

    def test_threshold_legality(self):
        rows=point_contracts()
        self.assertEqual(len(rows),8)
        self.assertTrue(all(row["valid"] and row["empty_split_count"]==0 for row in rows))
        self.assertEqual({row["gemm_grid"] for row in rows if row["split_k_iters"]==8},{49152})
        self.assertEqual({row["gemm_grid"] for row in rows if row["split_k_iters"]==1},{6144})

if __name__=="__main__":unittest.main(verbosity=2)
