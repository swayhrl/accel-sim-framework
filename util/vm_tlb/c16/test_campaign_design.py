#!/usr/bin/env python3
"""Directed schema, coverage, authority-boundary and budget checks."""
import csv
import json
import unittest
from pathlib import Path


ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_DESIGN_174NEW_V1'
HANDOFF=ROOT/'docs/vm_tlb/chatgpt_handoff/c16/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_DESIGN_V1.md'


def read(name):
    with (PACK/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))


class CampaignDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.points=read('MEASUREMENT_POINT_PLAN.tsv')
        cls.coverage=read('WORKLOAD_COVERAGE_MATRIX.tsv')
        cls.baselines=read('STRONG_SOFTWARE_BASELINES.tsv')
        cls.oracles=read('ORACLE_AND_STOP_RULES.tsv')
        cls.guards=read('CLOSED_DIRECTION_GUARD.tsv')
        cls.assets=read('ASSET_AND_RUNTIME_REQUIREMENTS.tsv')
        cls.tools=read('OBSERVABLE_TO_TOOL_MAP.tsv')
        cls.taxonomy=read('PROBLEM_COVERAGE_TAXONOMY.tsv')
        cls.decision=json.loads((PACK/'FINAL_DECISION.json').read_text(encoding='utf-8'))

    def test_eight_complete_points_and_whole_run_parent(self):
        self.assertEqual(len(self.points),8)
        self.assertEqual({p['point_id'] for p in self.points},{f'MP{i:02}' for i in range(1,9)})
        for p in self.points:
            self.assertTrue(all(p.values()),p['point_id'])
            self.assertEqual(p['model_revision'],'TO_BE_QUALIFIED')
            self.assertIn(p['asset_status'],{'ASSET_AVAILABLE','ASSET_MISSING','RUNTIME_UNQUALIFIED','MODEL_NOT_SELECTED'})
            self.assertTrue(p['local_scope'] and p['whole_run_parent'])
            self.assertIn(p['scientific_role'],{'discovery','control','holdout','stress','transition'})

    def test_coverage_and_presealed_holdouts(self):
        self.assertEqual({p['structure'] for p in self.points},{'dense','MoE'})
        self.assertEqual({p['phase'] for p in self.points},{'prefill','decode'})
        self.assertIn('W4_AWQ',{p['precision'] for p in self.points})
        self.assertGreaterEqual(len({p['candidate_model'] for p in self.points if p['structure']=='MoE'}),2)
        self.assertEqual({p['point_id'] for p in self.points if p['scientific_role']=='holdout'},set(self.decision['holdout_points']))
        self.assertEqual(set(self.decision['discovery_points']),{'MP01','MP02','MP03','MP06'})
        self.assertEqual(set(self.decision['control_points']),{'MP05'})
        self.assertEqual({p['batch_effective_M'].split(';')[0] for p in self.points if p['point_id'] in {'MP02','MP03','MP04'}},{'B1','B4','B16'})
        self.assertEqual(len(self.coverage),8)
        self.assertTrue(any(p['context_tokens']=='16384' for p in self.points))

    def test_budget_and_tiers(self):
        self.assertEqual(sum(int(p['estimated_gpu_active_min']) for p in self.points),20)
        self.assertEqual(self.decision['future_tier0_gpu_active_cap_min'],20)
        self.assertEqual(self.decision['future_tier1_gpu_active_cap_min'],30)
        self.assertLessEqual(self.decision['future_tier1_max_points'],3)
        self.assertFalse(self.decision['tier2_budget_authorized'])
        self.assertFalse(self.decision['tier3_simulator_mechanism_authorized'])
        self.assertFalse(self.decision['new_experiment_authorized'])

    def test_question_baseline_oracle_stop_joins(self):
        primary=set(self.decision['primary_question_ids'])
        self.assertEqual(primary,{'DQ1','DQ2','DQ3','DQ4'})
        baseline_ids={b['baseline_id'] for b in self.baselines}
        oracle_ids={o['oracle_id'] for o in self.oracles}
        stop_ids={o['stop_rule_id'] for o in self.oracles}
        question_ids={o['question_id'] for o in self.oracles}
        for p in self.points:
            self.assertIn(p['strong_baseline_id'],baseline_ids)
            self.assertTrue(set(p['question_ids'].split(';'))<=question_ids)
            self.assertTrue(set(p['stop_rule_id'].split(';'))<=stop_ids)
            self.assertTrue(set(p['oracle_id'].split(';'))<=oracle_ids|{'TRANSLATION_ORACLE_AUTHORITY_REQUIRED'})
        self.assertTrue(all(o['holdout'] and o['stop_condition'] and o['tier0_minimum'] for o in self.oracles))

    def test_closed_direction_and_unknown_guards(self):
        required={'selective_residency_M1F','cache_aware_splitK','dequant_result_cache','FFN_materialization',
                  'plain_gate_up_concurrency','plain_merged_gate_up_novelty','generic_Ada_W4_flat_GEMM',
                  'replacement_policy_predictor','DeepSeek_exact_reread','generic_translation_TLB_current_C16',
                  'generic_MoE_expert_locality'}
        self.assertEqual({g['closed_direction'] for g in self.guards},required)
        for g in self.guards:
            self.assertIn(g['OVERLAPS_CLOSED_DIRECTION'],{'YES','NO','PARTIAL'})
            if g['OVERLAPS_CLOSED_DIRECTION']=='YES':
                self.assertFalse(set(g['overlap_question'].split(';'))&set(self.decision['primary_question_ids']))
        self.assertEqual(self.decision['translation_timing'],'TRANSLATION_TIME_HEADROOM_UNKNOWN')
        self.assertEqual(self.decision['FP8'],'MODEL_NOT_SELECTED_RUNTIME_UNQUALIFIED')
        self.assertTrue(all(a['source_url'].startswith('https://') for a in self.assets))
        self.assertTrue(all(t['source_url'].startswith('https://') for t in self.tools))
        self.assertTrue(any(t['axis_id']=='TRANSLATION' for t in self.taxonomy))

    def test_handoff_preserves_predecessor_and_execution_lock(self):
        handoff=HANDOFF.read_text(encoding='utf-8')
        self.assertEqual(self.decision['predecessor_commit'],'9759c08f3bb6e9abd134591007a27ed5bf8c23b1')
        self.assertEqual(self.decision['predecessor_decision_preserved'],'NO_CURRENT_C16_ARCHITECTURE_PROBLEM_READY_FOR_PROMOTION')
        self.assertEqual([self.decision[k] for k in ('predecessor_qualified_literature_problem_count','predecessor_qualified_translation_problem_count','predecessor_qualified_cross_lineage_problem_count','predecessor_active_oracle_candidate_count','predecessor_active_promotion_candidate_count')],[0]*5)
        self.assertFalse(self.decision['execution_ready'])
        self.assertFalse(self.decision['gpu_used'])
        self.assertFalse(self.decision['models_downloaded'])
        self.assertIn('No 109 GPU',handoff)


if __name__=='__main__':
    unittest.main()
