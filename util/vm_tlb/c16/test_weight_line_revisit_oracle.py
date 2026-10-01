#!/usr/bin/env python3
"""CPU-only directed tests for revisit and scope accounting."""
import unittest

from weight_line_revisit_oracle import classify, line_row


def v(cta, warp, starts):
    return dict(cta=(cta,0,0),warp=warp,ordinal=0,starts=starts,sectors={a//32 for a in starts})


class RevisitTests(unittest.TestCase):
    def test_complementary_halves_are_not_sector_or_byte_duplicates(self):
        visits=[v(0,0,list(range(0,64,2))),v(0,1,list(range(64,128,2)))]
        row=line_row('TEST',7,0,visits)
        self.assertEqual(classify(visits),'DISJOINT_SECTOR_COMPLEMENT')
        self.assertEqual((row['sector_visit_count'],row['unique_sector_count'],row['duplicate_sector_visits']),(4,4,0))
        self.assertEqual((row['dynamic_byte_count'],row['unique_byte_count'],row['duplicate_byte_count']),(128,128,0))
        self.assertEqual((row['same_CTA_revisit'],row['cross_CTA_revisit']),(1,0))

    def test_exact_duplicate_cross_cta(self):
        starts=list(range(0,64,2))
        row=line_row('TEST',7,0,[v(0,0,starts),v(1,0,starts)])
        self.assertEqual(row['classification'],'EXACT_BYTE_REVISIT')
        self.assertEqual(row['cross_CTA_duplicate_sector_visits'],2)
        self.assertEqual(row['cross_CTA_duplicate_bytes'],64)
        self.assertEqual(row['same_CTA_duplicate_sector_visits'],0)

    def test_same_sector_different_bytes(self):
        row=line_row('TEST',7,0,[v(0,0,[0,2]),v(0,1,[4,6])])
        self.assertEqual(row['classification'],'SAME_SECTOR_REVISIT')
        self.assertEqual(row['duplicate_sector_visits'],1)
        self.assertEqual(row['duplicate_byte_count'],0)

    def test_same_cta_then_cross_cta_conservation(self):
        starts=[0,2]
        row=line_row('TEST',7,0,[v(0,0,starts),v(0,1,starts),v(1,0,starts)])
        self.assertEqual(row['classification'],'MIXED')
        self.assertEqual(row['duplicate_sector_visits'],2)
        self.assertEqual((row['same_CTA_duplicate_sector_visits'],row['cross_CTA_duplicate_sector_visits']),(1,1))
        self.assertEqual((row['same_CTA_duplicate_bytes'],row['cross_CTA_duplicate_bytes']),(4,4))

    def test_single_visit_not_called_revisit(self):
        row=line_row('TEST',7,0,[v(0,0,[0,2])])
        self.assertEqual(row['classification'],'UNKNOWN')
        self.assertEqual(row['duplicate_sector_visits'],0)


if __name__=='__main__':
    unittest.main()
