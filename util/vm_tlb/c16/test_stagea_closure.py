#!/usr/bin/env python3
"""CPU-only tests for fixed Stage A assets, inputs and holdout non-execution."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1'
PRE=ROOT/'docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_EXECUTION_PREFLIGHT_174NEW_V1'
DESIGN=ROOT/'docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_DESIGN_174NEW_V1'
DURABLE=Path('/root/share/mnt164/huangrulin/c16_ai_workload/assets/models')


def data(path):return json.loads(path.read_bytes())


def table(path):
    with path.open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class StageAClosureTests(unittest.TestCase):
    def test_asset_revisions_inventory_and_awq_semantics(self):
        meta=data(PRE/'REMOTE_MODEL_METADATA.json')['models']
        bf=data(PACK/'QWEN_BF16_ASSET_RECEIPT.json')
        awq=data(PACK/'QWEN_AWQ_ASSET_RECEIPT.json')
        ol=data(PACK/'OLMOE_ASSET_REVERIFY.json')
        for key,receipt in (('QWEN_BF16',bf),('QWEN_AWQ',awq)):
            self.assertEqual(receipt['status'],'PASS')
            self.assertEqual(receipt['repository'],meta[key]['repository'])
            self.assertEqual(receipt['revision'],meta[key]['revision'])
            self.assertEqual(receipt['weight_total_bytes'],meta[key]['weight_total_bytes'])
            self.assertEqual({x['path'] for x in receipt['files']},set(meta[key]['all_sibling_paths']))
            self.assertTrue(Path(receipt['durable_root']).is_dir())
            self.assertTrue(all((Path(receipt['durable_root'])/x['path']).stat().st_size==x['size_bytes'] for x in receipt['files']))
        self.assertEqual(bf['safetensors_index_status'],'PINNED_SAFETENSORS_INDEX_EXACT')
        self.assertEqual(awq['safetensors_index_status'],'SINGLE_FILE_HEADER_INDEX_NO_SEPARATE_INDEX')
        self.assertEqual(awq['quantization_config']['bits'],4)
        self.assertEqual(awq['quantization_config']['group_size'],128)
        self.assertTrue(awq['quantization_config']['zero_point'])
        self.assertTrue(awq['no_requantization'])
        for role in ('qweight','qzeros','scales'):
            self.assertGreater(awq['awq_tensor_metadata'][role]['tensor_count'],0)
        self.assertEqual(ol['status'],'PASS')
        self.assertEqual(ol['asset']['verified_file_count'],11)
        self.assertEqual(ol['asset']['weight_total_bytes'],13838721960)
        self.assertFalse((DURABLE/'granite-3.1-1b-a400m-instruct').exists())

    def test_stagea_roles_and_holdout_nonexecution(self):
        rows=table(PACK/'STAGEA_ASSET_MANIFEST.tsv')
        self.assertEqual(len(rows),8)
        design={x['point_id']:x for x in table(DESIGN/'MEASUREMENT_POINT_PLAN.tsv')}
        self.assertEqual([(r['point_id'],r['scientific_role']) for r in rows],
                         [(pid,design[pid]['scientific_role']) for pid in design])
        self.assertEqual({r['point_id'] for r in rows if r['asset_status']=='ASSET_READY_FOR_STAGE_A_INPUT_ONLY'},
                         {'MP01','MP02','MP03','MP05','MP06'})
        self.assertEqual({r['point_id'] for r in rows if r['asset_status']=='ASSET_REUSE_READY_NO_HOLDOUT_EXECUTION'},
                         {'MP04','MP08'})
        self.assertEqual(next(r for r in rows if r['point_id']=='MP07')['asset_status'],'DEFERRED_HOLDOUT_ASSET')
        self.assertTrue(all(r['model_output_generated']=='false' and r['gpu_executed']=='false' for r in rows))
        self.assertFalse((PACK/'DISCOVERY_FREEZE_RECEIPT.json').exists())

    def test_tokenization_sources_and_ids(self):
        frozen={x['source_text_id']:x for x in data(PRE/'INPUT_SOURCE_FREEZE.json')['entries']}
        rows=table(PACK/'TOKENIZATION_RECEIPTS.tsv')
        self.assertEqual(len(rows),80)
        self.assertEqual({x['model_key'] for x in rows},{'QWEN_BF16','QWEN_AWQ','OLMOE','GRANITE'})
        for row in rows:
            self.assertEqual(row['source_utf8_sha256'],frozen[row['source_text_id']]['utf8_sha256'])
            self.assertEqual(row['model_output_generated'],'false')
            path=PACK/row['token_ids_relative_path']
            self.assertEqual(sha(path),row['token_id_file_sha256'])
            ids=json.loads(path.read_bytes())
            self.assertEqual(len(ids),int(row['prompt_token_count']))
            self.assertEqual(hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest(),row['token_ids_sha256'])
        q={x['source_text_id']:x for x in rows if x['model_key']=='QWEN_BF16'}
        a={x['source_text_id']:x for x in rows if x['model_key']=='QWEN_AWQ'}
        self.assertEqual({k:v['token_ids_sha256'] for k,v in q.items()},
                         {k:v['token_ids_sha256'] for k,v in a.items()})

    def test_batch_length_audit_and_decision(self):
        rows=table(PACK/'BATCH_INPUT_LENGTH_AUDIT.tsv')
        self.assertEqual(len(rows),20)
        self.assertEqual(sum(r['batch_id']=='MP03_B4' for r in rows),4)
        self.assertEqual(sum(r['batch_id']=='MP04_B16' for r in rows),16)
        self.assertEqual(next(r for r in rows if r['batch_id']=='MP04_B16' and r['position']=='0')['source_text_id'],'TRAIN_A_DISCOVERY_00')
        decision=data(PACK/'FINAL_DECISION.json')
        self.assertIn(decision['status'],('STAGEA_ASSET_INPUT_READY','STAGEA_ASSET_INPUT_PARTIAL'))
        self.assertEqual(decision['stage_A_assets_ready'],5)
        self.assertEqual(decision['tokenization_receipt_count'],80)
        self.assertFalse(decision['holdout_model_outputs_generated'])
        self.assertFalse(decision['gpu_inference_executed'])
        self.assertFalse(decision['scientific_109_execution_authorized'])
        if 'BATCH_SHAPE_CONTROL_HAS_CONTEXT_MIX' in decision['batch_context_mix_flags']:
            self.assertEqual(decision['status'],'STAGEA_ASSET_INPUT_PARTIAL')


if __name__=='__main__':unittest.main()
