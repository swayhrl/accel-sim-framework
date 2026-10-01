#!/usr/bin/env python3
"""Directed state/claim guards for the terminal handoff (CPU only)."""
import copy
import csv
import json
import unittest
from pathlib import Path

from problem_discovery_v2_terminal_validate import check_final_state


ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_V2_TERMINAL_SYNTHESIS_174NEW_V1'
HANDOFF=ROOT/'docs/vm_tlb/chatgpt_handoff/c16/C16_PROBLEM_DISCOVERY_V2_CURRENT_STATE.md'


class TerminalStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state=json.loads((PACK/'FINAL_PROJECT_STATE.json').read_text(encoding='utf-8'))
        cls.handoff=HANDOFF.read_text(encoding='utf-8')

    def test_accepted_state(self):
        check_final_state(self.state,self.handoff)

    def rejects(self,field,value):
        changed=copy.deepcopy(self.state)
        changed[field]=value
        with self.assertRaises(AssertionError):
            check_final_state(changed,self.handoff)

    def test_no_active_candidate(self):
        self.rejects('active_oracle_candidate_count',1)
        self.rejects('active_promotion_candidate_count',1)

    def test_translation_unknown(self):
        self.rejects('translation_time_headroom','KNOWN')

    def test_no_experiment(self):
        self.rejects('new_experiment_authorized',True)

    def test_deepseek_correction(self):
        changed=copy.deepcopy(self.state)
        changed['deepseek_revisit']['cross_warp_revisit_count']=1
        with self.assertRaises(AssertionError):check_final_state(changed,self.handoff)
        changed=copy.deepcopy(self.state)
        changed['deepseek_revisit']['exact_byte_redundancy_fraction']=0.0
        with self.assertRaises(AssertionError):check_final_state(changed,self.handoff)

    def test_old_interpretation_not_current_handoff(self):
        with self.assertRaises(AssertionError):
            check_final_state(self.state,self.handoff+'\ncross-warp shared weight line\n')

    def test_ledger_matches_verified_upstream_manifests(self):
        validation=json.loads((PACK/'AUTHORITY_VALIDATION.json').read_text(encoding='utf-8'))
        with (PACK/'C16_PROBLEM_DISCOVERY_V2_EVIDENCE_LEDGER.tsv').open(encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f,delimiter='\t'))
        mapping={'BASE_TERMINAL':'base_terminal','LITERATURE':'literature',
                 'CROSS_LINEAGE_DISCOVERY':'cross_lineage','TRANSLATION':'translation',
                 'NEAREST_NEIGHBOR':'nearest_neighbor','DEEPSEEK_ORACLE':'deepseek_oracle'}
        self.assertEqual(len(rows),len(mapping))
        for row in rows:
            pack=validation['packs'][mapping[row['authority_id']]]
            self.assertEqual(row['commit'],pack['commit'])
            self.assertEqual(row['tree'],pack['tree'])
            self.assertEqual(row['SHA256SUMS_sha256'],pack['sha256sums_sha256'])
            self.assertEqual(int(row['entries_verified']),pack['sha256sums_entries_verified'])


if __name__=='__main__':
    unittest.main()
