#!/usr/bin/env python3
"""Deterministic CPU-only Stage A asset/input decision from immutable receipts."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


REVISION={
    'QWEN_BF16':'aa8e72537993ba99e69dfaafa59ed015b17504d1',
    'QWEN_AWQ':'3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd',
    'OLMOE':'b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e',
}
POINTS={
    'MP01':('QWEN_BF16','discovery','STAGE_A'),
    'MP02':('QWEN_BF16','discovery','STAGE_A'),
    'MP03':('QWEN_BF16','transition','STAGE_A_DISCOVERY_SET'),
    'MP04':('QWEN_BF16','holdout','ASSET_REUSE_NO_EXECUTION'),
    'MP05':('QWEN_AWQ','control','STAGE_A'),
    'MP06':('OLMOE','discovery','STAGE_A'),
    'MP07':('GRANITE','holdout','DEFERRED_HOLDOUT_ASSET'),
    'MP08':('QWEN_BF16','holdout','ASSET_REUSE_NO_EXECUTION'),
}
RECEIPTS={'QWEN_BF16':'QWEN_BF16_ASSET_RECEIPT.json',
          'QWEN_AWQ':'QWEN_AWQ_ASSET_RECEIPT.json',
          'OLMOE':'OLMOE_ASSET_REVERIFY.json'}


def load(path: Path):
    return json.loads(path.read_bytes())


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path: Path) -> list[dict]:
    with path.open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))


def write_table(path: Path, rows: list[dict]):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)


def build(source: Path,out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    receipts={};gaps=[]
    for key,name in RECEIPTS.items():
        path=source/name
        if not path.is_file():
            gaps.append('MISSING_ASSET_RECEIPT_'+key)
            continue
        value=load(path)
        if value.get('status')!='PASS' or value.get('revision')!=REVISION[key]:
            gaps.append('ASSET_RECEIPT_NOT_PASS_'+key)
        receipts[key]=value
    if 'OLMOE' in receipts:
        ol=receipts['OLMOE']
        if ol['asset']['weight_total_bytes']!=13838721960 or ol['asset']['verified_file_count']!=11:
            gaps.append('OLMOE_EXPECTED_ASSET_MISMATCH')
    if 'QWEN_AWQ' in receipts:
        awq=receipts['QWEN_AWQ']
        if awq['quantization_config']['group_size']!=128 or not awq['quantization_config']['zero_point']:
            gaps.append('AWQ_QUANTIZATION_SEMANTICS_MISMATCH')
        if any(awq['awq_tensor_metadata'].get(x,{}).get('tensor_count',0)<1 for x in ('qweight','qzeros','scales')):
            gaps.append('AWQ_TENSOR_METADATA_MISSING')
    rows=[]
    for pid,(key,role,stage) in POINTS.items():
        receipt_name=RECEIPTS.get(key,'NOT_PREPARED')
        receipt=receipts.get(key)
        if key=='GRANITE':status='DEFERRED_HOLDOUT_ASSET';root='NOT_PREPARED'
        elif receipt is None:status='ASSET_INCOMPLETE';root='UNKNOWN'
        elif stage=='ASSET_REUSE_NO_EXECUTION':status='ASSET_REUSE_READY_NO_HOLDOUT_EXECUTION';root=receipt['durable_root']
        else:status='ASSET_READY_FOR_STAGE_A_INPUT_ONLY';root=receipt['durable_root'] if key!='OLMOE' else receipt['asset']['expected_path']
        if key=='OLMOE' and receipt is not None:root=receipt['asset']['expected_path']
        rows.append(dict(point_id=pid,scientific_role=role,execution_group=stage,model_key=key,
                         revision=REVISION.get(key,'DEFERRED'),durable_asset_root=root,
                         asset_receipt=receipt_name,asset_receipt_sha256=sha(source/receipt_name) if receipt else 'NOT_AVAILABLE',
                         asset_status=status,model_output_generated='false',gpu_executed='false'))
    write_table(out/'STAGEA_ASSET_MANIFEST.tsv',rows)
    token_path=source/'TOKENIZATION_RECEIPTS.tsv';batch_path=source/'BATCH_INPUT_LENGTH_AUDIT.tsv'
    token_rows=table(token_path) if token_path.is_file() else []
    batch_rows=table(batch_path) if batch_path.is_file() else []
    if len(token_rows)!=80:gaps.append('TOKENIZATION_80_ROWS_MISSING')
    expected={(m,s) for m in ('QWEN_BF16','QWEN_AWQ','OLMOE','GRANITE') for s in
              [f'TRAIN_A_DISCOVERY_{i:02}' for i in range(4)]+[f'TRAIN_B_SEALED_{i:02}' for i in range(1,16)]+['PG19_VALIDATION_11155_PREFIX']}
    if {(r['model_key'],r['source_text_id']) for r in token_rows}!=expected:
        gaps.append('TOKENIZATION_IDENTITY_COVERAGE_MISMATCH')
    for row in token_rows:
        ids=source/row['token_ids_relative_path']
        if not ids.is_file() or sha(ids)!=row['token_id_file_sha256']:
            gaps.append('TOKEN_IDS_SHA_MISMATCH_'+row['model_key']+'_'+row['source_text_id'])
        if row['model_output_generated']!='false':
            gaps.append('FORBIDDEN_MODEL_OUTPUT_PRESENT')
    if len(batch_rows)!=20:
        gaps.append('BATCH_LENGTH_AUDIT_MISSING')
    flags=sorted({r['context_mix_flag'] for r in batch_rows})
    batch_distribution={}
    for batch in sorted({r['batch_id'] for r in batch_rows}):
        selected=[r for r in batch_rows if r['batch_id']==batch]
        actual=[int(r['prompt_token_count']) for r in selected]
        full=[int(r['full_source_templated_token_count']) for r in selected]
        batch_distribution[batch]=dict(samples=len(selected),prompt_min=min(actual),prompt_max=max(actual),
                                       full_source_min=min(full),full_source_max=max(full),
                                       context_mix_flag=selected[0]['context_mix_flag'])
    if 'BATCH_SHAPE_CONTROL_HAS_CONTEXT_MIX' in flags:
        gaps.append('BATCH_SHAPE_CONTROL_HAS_CONTEXT_MIX_REQUIRES_PROJECT_REVIEW')
    status='STAGEA_ASSET_INPUT_READY' if not gaps else 'STAGEA_ASSET_INPUT_PARTIAL'
    decision=dict(schema='C16_STAGEA_ASSET_INPUT_CLOSURE_V1',status=status,
                  authority_preflight_commit='2f922c402c7f16c2bed278d07e12650cbaf82bfc',
                  authority_design_commit='5f0335b5f991890348e60e1f23a546f393f86d8b',
                  stage_A_points=['MP01','MP02','MP03','MP05','MP06'],
                  stage_A_assets_ready=sum(x['asset_status']=='ASSET_READY_FOR_STAGE_A_INPUT_ONLY' for x in rows),
                  holdout_asset_reuse_no_execution=['MP04','MP08'],
                  granite='DEFERRED_HOLDOUT_ASSET',
                  model_asset_receipts={key:name for key,name in RECEIPTS.items() if key in receipts},
                  tokenization_receipt_count=len(token_rows),
                  batch_length_audit_rows=len(batch_rows),
                  batch_length_distribution=batch_distribution,
                  batch_context_mix_flags=flags,blocking_gaps=gaps,
                  discovery_freeze_receipt_created=False,
                  holdout_model_outputs_generated=False,
                  gpu_inference_executed=False,scientific_109_execution_authorized=False)
    (out/'FINAL_DECISION.json').write_text(json.dumps(decision,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=status,stageA=decision['stage_A_assets_ready'],tokens=len(token_rows),flags=flags,gaps=gaps),sort_keys=True))
    return decision


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();build(args.source,args.out)


if __name__=='__main__':main()
