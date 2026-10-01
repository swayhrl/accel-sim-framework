#!/usr/bin/env python3
"""CPU-only identity, input, budget, readiness and holdout-gate tests."""
from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from holdout_access_gate import check_release


ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_EXECUTION_PREFLIGHT_174NEW_V1'
DESIGN=ROOT/'docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_DESIGN_174NEW_V1'


def data(name):
    return json.loads((PACK/name).read_bytes())


def table(name,root=PACK):
    with (root/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))


class PreflightTests(unittest.TestCase):
    def test_design_identity_roles_questions_budget(self):
        design=table('MEASUREMENT_POINT_PLAN.tsv',DESIGN)
        ready=table('POINT_EXECUTION_READINESS.tsv')
        self.assertEqual([x['point_id'] for x in design],[x['point_id'] for x in ready])
        self.assertEqual([(x['point_id'],x['scientific_role']) for x in design],
                         [(x['point_id'],x['scientific_role']) for x in ready])
        dec=data('EXECUTION_PREFLIGHT_DECISION.json')
        self.assertEqual(dec['design_commit'],'5f0335b5f991890348e60e1f23a546f393f86d8b')
        self.assertEqual(dec['primary_questions_preserved'],['DQ1','DQ2','DQ3','DQ4'])
        self.assertEqual(dec['analysis_subquestions'],['DQ4a','DQ4b'])
        self.assertEqual(dec['discovery_points_preserved'],['MP01','MP02','MP03','MP06'])
        self.assertEqual(dec['control_points_preserved'],['MP05'])
        self.assertEqual(dec['holdout_points_preserved'],['MP04','MP07','MP08'])
        self.assertEqual(sum(int(x['estimated_gpu_active_min']) for x in design),20)
        self.assertEqual(sum(int(x['estimated_gpu_active_min']) for x in design if x['point_id'] in dec['future_stage_A_points']),12)

    def test_model_pins_assets_and_awq_semantics(self):
        remote=data('REMOTE_MODEL_METADATA.json')['models']
        local=data('LOCAL_164_ASSET_AUDIT.json')['models']
        pins={x['model_key']:x for x in table('MODEL_IDENTITY_PINS.tsv')}
        self.assertEqual(set(pins),{'QWEN_BF16','QWEN_AWQ','OLMOE','GRANITE'})
        for key,m in remote.items():
            self.assertEqual(pins[key]['revision'],m['revision'])
            self.assertEqual(pins[key]['config_sha256'],m['small_files']['config.json']['sha256'])
            self.assertEqual(int(pins[key]['weight_total_bytes']),m['weight_total_bytes'])
        self.assertEqual(remote['QWEN_AWQ']['config']['quantization_config']['bits'],4)
        self.assertEqual(remote['QWEN_AWQ']['config']['quantization_config']['group_size'],128)
        self.assertTrue(remote['QWEN_AWQ']['config']['quantization_config']['zero_point'])
        self.assertEqual(remote['QWEN_AWQ']['config']['torch_dtype'],'float16')
        self.assertEqual(local['OLMOE']['status'],'ASSET_READY')
        self.assertTrue(local['OLMOE']['full_weight_hash_checked'])
        self.assertEqual(local['OLMOE']['verified_file_count'],11)
        self.assertEqual({k for k,v in local.items() if v['status']=='NEW_ASSET_REQUIRED'},
                         {'QWEN_BF16','QWEN_AWQ','GRANITE'})

    def test_source_text_bytes_and_holdout_input_mapping(self):
        freeze=data('INPUT_SOURCE_FREEZE.json')
        rows=table('INPUT_SOURCE_MANIFEST.tsv')
        self.assertEqual(len(rows),20)
        self.assertEqual(len(freeze['entries']),20)
        self.assertFalse(freeze['tokenizer_executed'])
        for row in rows:
            body=(PACK/row['relative_path']).read_bytes()
            self.assertEqual(len(body),int(row['byte_count']))
            self.assertEqual(hashlib.sha256(body).hexdigest(),row['utf8_sha256'])
            self.assertEqual(row['token_ids'],'NOT_GENERATED')
        self.assertEqual(len([r for r in rows if r['source_text_id'].startswith('TRAIN_A_')]),4)
        self.assertEqual(len([r for r in rows if r['source_text_id'].startswith('TRAIN_B_')]),15)
        self.assertEqual(freeze['pg19_excerpt_byte_end'],200000)
        seal=data('HOLDOUT_SEAL_MANIFEST.json')
        self.assertEqual(len(seal['holdout_points']['MP04']),16)
        self.assertEqual(seal['holdout_points']['MP04'][0]['source_text_id'],'TRAIN_A_DISCOVERY_00')
        self.assertEqual({x['source_text_id'] for x in seal['holdout_points']['MP04'][1:]},
                         {f'TRAIN_B_SEALED_{i:02}' for i in range(1,16)})

    def test_runtime_vram_and_fail_closed_readiness(self):
        run=data('RUNTIME_SOURCE_AUDIT.json')
        self.assertEqual(run['commit'],'ced6857afa0ea7b2e3f0846a62e1394e90f15607')
        self.assertEqual(run['installed_109_binary'],'UNKNOWN_NOT_AUDITED')
        self.assertEqual({r['runtime_status'] for r in table('RUNTIME_STRONG_BASELINE_PINS.tsv')},{'RUNTIME_UNQUALIFIED'})
        memory={r['point_id']:r for r in table('VRAM_FEASIBILITY.tsv')}
        self.assertEqual(memory['MP06']['classification'],'BORDERLINE')
        self.assertEqual(memory['MP04']['classification'],'LIKELY_FITS_16GB')
        self.assertEqual(memory['MP08']['classification'],'LIKELY_FITS_16GB')
        ready=table('POINT_EXECUTION_READINESS.tsv')
        self.assertEqual(sum(r['ready_for_tier0_contract']=='true' for r in ready),0)
        self.assertEqual(sum(r['readiness']=='NEW_ASSET_REQUIRED' for r in ready),7)
        self.assertEqual(sum(r['readiness']=='RUNTIME_UNQUALIFIED' for r in ready),1)
        self.assertFalse((PACK/'C16_MEASUREMENT_CAMPAIGN_TIER0_109_CONTRACT_V1.json').exists())
        dec=data('EXECUTION_PREFLIGHT_DECISION.json')
        self.assertEqual(dec['status'],'EXECUTION_PREFLIGHT_PARTIAL_REVIEW_REQUIRED')
        self.assertFalse(dec['execution_ready'])
        self.assertFalse(dec['new_experiment_authorized'])
        self.assertFalse(dec['tier0_109_draft_contract_generated'])

    def test_question_readiness_and_translation_unknown(self):
        rows={r['question_id']:r for r in table('QUESTION_EXECUTION_READINESS.tsv')}
        self.assertEqual(set(rows),{'DQ1','DQ2','DQ3','DQ4','DQ4a','DQ4b','SQ_TRANSLATION_AUTHORITY_ONLY'})
        self.assertTrue(all(r['readiness']=='CAMPAIGN_QUESTION_NOT_EXECUTION_READY' for r in rows.values()))
        self.assertEqual(data('EXECUTION_PREFLIGHT_DECISION.json')['point_ready_for_tier0_contract_count'],0)

    def test_holdout_gate_rejects_unprovisioned_then_checks_synthetic_receipt(self):
        manifest=data('HOLDOUT_SEAL_MANIFEST.json')
        with self.assertRaises(ValueError):check_release(manifest,b'{}',Path('.'))
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            receipt=dict(DQ_id='DQ4',phenomenon='synthetic',sign='POSITIVE',estimator='median',
                         materiality_threshold='synthetic threshold',STOP_rule='synthetic stop',
                         exact_holdout_points=['MP04','MP07','MP08'])
            raw=(json.dumps(receipt,sort_keys=True)+'\n').encode()
            sealed=dict(manifest,status='SEALED_OUTPUTS_READY',trusted_coordination_commit='a'*40,
                        authorized_freeze_receipt_sha256=hashlib.sha256(raw).hexdigest())
            outputs=[]
            for pid in ('MP04','MP07','MP08'):
                path=root/(pid+'.cms');path.write_bytes(('synthetic-'+pid).encode())
                outputs.append(dict(point_id=pid,relative_path=path.name,
                                    sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            sealed['encrypted_outputs']=outputs
            result=check_release(sealed,raw,root)
            self.assertEqual(result['ciphertext_count'],3)
            with self.assertRaises(ValueError):check_release(sealed,raw+b'changed',root)


if __name__=='__main__':
    unittest.main()
