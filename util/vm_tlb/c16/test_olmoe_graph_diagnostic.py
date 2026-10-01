#!/usr/bin/env python3
"""Directed and accepted-raw CPU tests; no GPU/model execution."""
import csv
import json
import unittest
from pathlib import Path

from olmoe_graph_correctness_diagnostic import classify_event,analyze,ATOL,RTOL


ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'docs/vm_tlb/review_packs/C16_OLMOE_GRAPH_OFF_ON_CORRECTNESS_DIAGNOSTIC_174NEW_V1'
RAW=Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/c16_stagea_runtime_qualification_canary_v1/C16R_stagea-runtime-qualification-canary-v1_20261001T154021Z')


def rows(name):
    with (PACK/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))


class DiagnosticTests(unittest.TestCase):
    def test_synthetic_event_classes(self):
        self.assertEqual(classify_event([1,2,3],[2,1,3]),('ORDER_ONLY_SWAP',2,3,3,1.0))
        self.assertEqual(classify_event([1,2,3],[1,2,4]),('EXPERT_SET_SUBSTITUTION',1,2,4,0.5))
        self.assertEqual(classify_event([1,2,3],[1,2])[0],'STRUCTURE_SHIFT')
        self.assertEqual(classify_event([1,2,3],[1,2,3])[0],'EXACT_MATCH')

    def test_raw_structure_and_4761_conservation(self):
        off=json.loads((RAW/'OLMOE_off.json').read_bytes())
        on=json.loads((RAW/'OLMOE_on.json').read_bytes())
        result,steps,events,log=analyze(off,on)
        self.assertEqual(result['raw_nested_shape'],{'graph_off':[543,16,8],'graph_on':[543,16,8]})
        self.assertEqual(result['routing_event_count'],8688)
        self.assertEqual(result['positional_mismatch_count'],4761)
        self.assertEqual((result['order_only_swap_events'],result['expert_set_substitution_events']),(1599,616))
        self.assertEqual(result['structure_shift_events'],0)
        self.assertEqual(result['positional_mismatches_by_event_class']['ORDER_ONLY_SWAP'],3690)
        self.assertEqual(result['positional_mismatches_by_event_class']['EXPERT_SET_SUBSTITUTION'],1071)
        self.assertEqual(result['set_substitution_intersection_histogram'],{'6':1,'7':615})
        self.assertEqual(len(steps),32)
        self.assertEqual(len(events),8688)
        self.assertEqual(len(log),32)
        self.assertEqual((steps[0]['positional_mismatch_count'],steps[0]['expert_set_substitution_events']),(4559,590))
        self.assertEqual(result['first_divergence_by_event_class']['EXPERT_SET_SUBSTITUTION'],(3,6,7))

    def test_logprob_frozen_gate_and_no_v2(self):
        decisions=json.loads((PACK/'FINAL_DECISION.json').read_bytes())
        log=rows('LOGPROB_DELTA_BY_STEP.tsv')
        self.assertEqual([r['decode_output_step'] for r in log if r['exceeds_original_tolerance']=='true'],
                         ['D1','D4','D6','D23','D29'])
        self.assertEqual(float(log[0]['abs_delta']),0.008175641298294067)
        self.assertEqual(float(log[23]['abs_delta']),0.10254716873168945)
        self.assertEqual((float(log[0]['original_atol']),float(log[0]['original_rtol'])),(ATOL,RTOL))
        self.assertEqual(decisions['status'],'OLMOE_GRAPH_MODE_EXPERT_SET_DIVERGENCE')
        self.assertTrue(decisions['original_failure_preserved'])
        self.assertFalse(decisions['v2_canary_draft_generated'])
        self.assertFalse(decisions['new_gpu_execution_authorized'])
        by_step={r['decode_output_step']:r for r in rows('ROUTING_MISMATCH_BY_STEP.tsv')}
        self.assertEqual(int(by_step['D29']['positional_mismatch_count']),0)


if __name__=='__main__':unittest.main()
