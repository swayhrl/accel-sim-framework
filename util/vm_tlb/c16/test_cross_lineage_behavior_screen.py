#!/usr/bin/env python3
"""Directed CPU tests for the C16WARP1 behavior-screen definitions."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path


SOURCE=Path(__file__).with_name('cross_lineage_behavior_screen.py')
SPEC=importlib.util.spec_from_file_location('cross_lineage_behavior_screen',SOURCE)
MODULE=importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
REPO=SOURCE.parents[3]
PACK=REPO/MODULE.OUT


class ScreenTests(unittest.TestCase):
    def test_within_shard_weight_line_revisit_and_input_broadcast(self):
        with tempfile.TemporaryDirectory() as name:
            base=Path(name)
            context=base/'context.json'
            context.write_text(json.dumps({'weight':{'ptr':'0x1000','bytes':256},'input':{'ptr':'0x2000','bytes':256}}))
            full=(1<<32)-1
            weight=[0x1000+2*i for i in range(32)]
            input_addrs=[0x2000+2*(i//2) for i in range(32)]
            trace=(MODULE.HEADER.pack(b'C16WARP1',7,0,3,0,3)
                   +MODULE.RECORD.pack(7,full,0,0,0,0,*weight)
                   +MODULE.RECORD.pack(7,full,0,0,0,1,*weight)
                   +MODULE.RECORD.pack(7,full,0,0,0,2,*input_addrs))
            path=base/'trace.bin';path.write_bytes(trace)
            item=dict(static=7,trace=path,context=context,trace_sha=hashlib.sha256(trace).hexdigest(),context_sha=hashlib.sha256(context.read_bytes()).hexdigest(),declared=3,status='EXECUTED_SHARD')
            row,roles=MODULE.parse_shard(item)
            self.assertEqual((row['warp_records'],row['active_lane_events']), (3,96))
            self.assertEqual((row['WEIGHT_unique_lines'],row['WEIGHT_cross_warp_shared_lines']), (1,1))
            self.assertEqual((roles['INPUT']['lanes'],roles['INPUT']['distinct_starts'],roles['INPUT']['sectors']), (32,16,1))
            self.assertEqual(roles['WEIGHT']['sectors'],4)

    def test_concentration_definitions(self):
        even=MODULE.concentration([1,1,1,1])
        skew=MODULE.concentration([4,0,0,0])
        self.assertEqual(even['gini'],0)
        self.assertEqual(even['normalized_entropy'],1)
        self.assertAlmostEqual(skew['gini'],.75)
        self.assertEqual(skew['top1'],1)

    def test_published_authority_and_candidate_bounds(self):
        result=json.loads((PACK/'FINAL_DECISION.json').read_text())
        self.assertEqual(result['decision'],'CROSS_LINEAGE_ANOMALY_QUALIFIED_FOR_ORACLE_SCREEN')
        self.assertEqual(result['qualified_candidates'],['DEEPSEEK_WEIGHT_LINE_REVISIT'])
        self.assertEqual(result['independent_lineage_holdout'],'NO_INDEPENDENT_LINEAGE_HOLDOUT')
        self.assertFalse(result['new_experiment_authorized'])
        self.assertEqual(result['weight_revisit']['DEEPSEEK']['logical_weight_lane_bytes_per_weight_byte'],2)
        self.assertEqual(result['weight_revisit']['OLMOE']['warp_visits_per_unique_line_within_shard'],1)
        with (PACK/'RAW_SHARD_INDEX.tsv').open(newline='') as handle:
            rows=list(csv.DictReader(handle,delimiter='\t'))
        self.assertEqual(len(rows),729)
        for line in (PACK/'SHA256SUMS').read_text().splitlines():
            sha,filename=line.split('  ',1)
            self.assertEqual(hashlib.sha256((PACK/filename).read_bytes()).hexdigest(),sha)


if __name__=='__main__':unittest.main()
