#!/usr/bin/env python3
"""Offline deterministic synthesis of pinned C16 execution-preflight evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


PACK=Path('docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_EXECUTION_PREFLIGHT_174NEW_V1')
DESIGN=Path('docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_DESIGN_174NEW_V1')
MODEL_FOR_POINT={
    'MP01':'QWEN_BF16','MP02':'QWEN_BF16','MP03':'QWEN_BF16','MP04':'QWEN_BF16',
    'MP05':'QWEN_AWQ','MP06':'OLMOE','MP07':'GRANITE','MP08':'QWEN_BF16',
}
BASELINE_FOR_MODEL={'QWEN_BF16':'SB01','QWEN_AWQ':'SB02','OLMOE':'SB03','GRANITE':'SB04'}
GIB=1024**3


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def read_tsv(path: Path) -> list[dict]:
    with path.open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))


def write_tsv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise AssertionError('empty table '+str(path))
    fields=list(rows[0])
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n')
        w.writeheader()
        for row in rows:
            if set(row)!=set(fields):
                raise AssertionError((path,set(row),set(fields)))
            w.writerow(row)


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')


def model_rows(remote: dict) -> list[dict]:
    result=[]
    for key,m in sorted(remote['models'].items()):
        q=m['config'].get('quantization_config')
        result.append(dict(model_key=key,repository=m['repository'],revision=m['revision'],
                           config_sha256=m['small_files']['config.json']['sha256'],
                           tokenizer_revision=m['tokenizer_revision'],
                           tokenizer_config_sha256=m['small_files']['tokenizer_config.json']['sha256'],
                           tokenizer_json_sha256=m['small_files'].get('tokenizer.json',{}).get('sha256','NOT_PRESENT'),
                           weight_shard_count=len(m['weight_shards']),weight_shard_inventory=';'.join(
                               f'{x["path"]}:{x["size_bytes"]}:{x["sha256"]}' for x in m['weight_shards']),
                           weight_total_bytes=m['weight_total_bytes'],
                           quantization_config=json.dumps(q,sort_keys=True,separators=(',',':')) if q else 'NONE',
                           license=m['license_name'] if m['license_name']!='UNKNOWN' else m['license'],
                           public_access=('PUBLIC_UNGATED' if not m['private'] and not m['gated'] else 'ACCESS_REVIEW_REQUIRED'),
                           pin_status='PINNED_REMOTE_METADATA',license_review='REQUIRED_BEFORE_ASSET_TRANSFER',
                           metadata_authority=m['api_url']))
    return result


def asset_rows(points: list[dict],remote: dict,local: dict) -> list[dict]:
    result=[]
    for point in points:
        pid=point['point_id'];key=MODEL_FOR_POINT[pid]
        m=remote['models'][key];asset=local['models'][key]
        if asset['status']=='ASSET_READY':
            if (asset['expected_revision']!=m['revision'] or
                asset['config_sha256']!=m['small_files']['config.json']['sha256'] or
                asset['weight_total_bytes']!=m['weight_total_bytes'] or
                not asset['full_weight_hash_checked']):
                raise AssertionError('local versus remote pinned identity mismatch '+key)
        result.append(dict(point_id=pid,model_key=key,expected_repository=m['repository'],
                           expected_revision=m['revision'],asset_status=asset['status'],
                           local_164_path=asset['expected_path'],receipt_sha256=asset.get('receipt_sha256','NOT_PRESENT'),
                           local_weight_hash_closure=('PASS' if asset.get('full_weight_hash_checked') and asset['status']=='ASSET_READY' else 'NOT_AVAILABLE'),
                           local_weight_bytes=asset.get('weight_total_bytes','UNKNOWN'),
                           remote_pinned_weight_bytes=m['weight_total_bytes'],
                           completeness='11_OF_11_SHA_AND_INDEX_PASS' if key=='OLMOE' and asset['status']=='ASSET_READY' else 'NO_LOCAL_DURABLE_ASSET',
                           qualification_boundary='asset alone never qualifies 109 whole-run strong runtime'))
    return result


def runtime_rows(remote: dict,source: dict) -> list[dict]:
    c=source['commit'];tag=source['tag']
    descriptions={
        'SB01':('QWEN_BF16','qwen2.py Qwen2ForCausalLM with merged MLP source;v1 flash_attn.py candidate',
                'FlashAttention candidate;exact selected backend UNKNOWN','Qwen2 merged projection source present;exact kernel UNKNOWN',
                'identity canary graph OFF;graph ON strong control only if capability/correctness/neutrality pass'),
        'SB02':('QWEN_AWQ','Qwen2 model plus auto_awq.py and marlin_utils.py;no requantization proposed',
                'FlashAttention candidate;exact selected backend UNKNOWN','AWQ GEMM zero-point group128 W4 with AWQ-Marlin candidate;exact repack/kernel UNKNOWN',
                'same graph policy as SB01;quantized correctness and packing first'),
        'SB03':('OLMOE','olmoe.py OlmoeForCausalLM with FusedMoE source path',
                'FlashAttention candidate;exact selected backend UNKNOWN','FusedMoE source class present;expert GEMM/GEMV kernel UNKNOWN',
                'identity canary graph OFF;graph ON only after routing/correctness neutrality'),
        'SB04':('GRANITE','granitemoe.py GraniteMoeForCausalLM with FusedMoE source path',
                'FlashAttention candidate;exact selected backend UNKNOWN','FusedMoE source class present;expert kernel UNKNOWN',
                'holdout cannot run before Stage A freeze and independent authorization'),
    }
    result=[]
    for bid,(model_key,impl,attention,projection,graph) in descriptions.items():
        result.append(dict(baseline_id=bid,model_key=model_key,framework='vllm-project/vllm',
                           exact_source_tag=tag,exact_source_commit=c,implementation_candidate=impl,
                           attention_backend=attention,projection_or_expert_backend=projection,
                           cuda_graph_policy=graph,runtime_status='RUNTIME_UNQUALIFIED',
                           exact_109_installed_binary='UNKNOWN',
                           strong_software_status='SOURCE_CAPABILITY_CANDIDATE_ONLY',
                           fail_closed='no eager/reference fallback;canary must bind selected kernels and correctness'))
    return result


def compatibility_rows(source: dict) -> list[dict]:
    s=source['source_files']
    checks=[
        ('SM89_BUILD_TARGET','ALL','CMakeLists.txt',s['cmake']['markers']['8.9'],'source mentions 8.9;actual 109 build target unknown'),
        ('DENSE_BF16_MERGED','MP01;MP02;MP03;MP04;MP08','qwen2.py',s['qwen2']['markers']['MergedColumnParallelLinear'],'BF16 model config pinned;selected fused kernel unknown'),
        ('FLASH_ATTENTION_ADA','ALL','flash_attn.py',s['flash_attn']['markers']['FlashAttention'],'source path present;exact backend and head-dim support need canary'),
        ('AWQ_W4_ZEROPOINT','MP05','auto_awq.py',s['auto_awq']['markers']['zero_point'] and s['auto_awq']['markers']['group_size'],'checkpoint AWQ GEMM bits4 group128 zero_point true;selected Marlin repack unknown'),
        ('AWQ_MARLIN_SM89','MP05','marlin_utils.py',s['marlin_utils']['markers']['SM89'],'source recognizes SM89;compiled kernel/packing correctness unknown'),
        ('OLMOE_FUSED_MOE','MP06','olmoe.py',s['olmoe']['markers']['FusedMoE'],'routing implementation source present;actual expert kernel and graph path unknown'),
        ('GRANITE_FUSED_MOE','MP07','granitemoe.py',s['granitemoe']['markers']['FusedMoE'],'source path present;actual expert kernel and graph path unknown'),
        ('CUDA_GRAPH_POLICY','ALL','runtime canary not source-only',False,'must be frozen by 109 ON/OFF neutrality pair;no assumption'),
        ('TLB_PTW_BLOCKED_TIME','MP08','NCU/tool capability not resolved',False,'VA pages are not translation timing;retain UNKNOWN'),
    ]
    return [dict(capability_id=cid,point_scope=scope,source_anchor=anchor,
                 source_marker_present=str(marker).lower(),
                 static_assessment=('SOURCE_PATH_PRESENT' if marker else 'UNKNOWN_NOT_PROVEN'),
                 known_incompatible='NO_EVIDENCE_OF_KNOWN_INCOMPATIBILITY',
                 binary_status='TO_BE_CONFIRMED_BY_109_CANARY',boundary=note,
                 pinned_vllm_commit=source['commit']) for cid,scope,anchor,marker,note in checks]


def vram_rows(points: list[dict],remote: dict) -> list[dict]:
    workspace={
        'MP01':(0.5,2.0),'MP02':(0.5,2.0),'MP03':(0.6,2.2),'MP04':(0.8,2.5),
        'MP05':(0.5,2.0),'MP06':(0.5,2.0),'MP07':(0.5,2.0),'MP08':(0.8,3.0),
    }
    result=[]
    for point in points:
        pid=point['point_id'];key=MODEL_FOR_POINT[pid];m=remote['models'][key];cfg=m['config']
        batch={'MP03':4,'MP04':16}.get(pid,1)
        context=int(point['context_tokens'])
        steps=0 if point['phase']=='prefill' else 32
        heads=int(cfg['num_attention_heads']);kvheads=int(cfg['num_key_value_heads'])
        head_dim=int(cfg.get('head_dim') or int(cfg['hidden_size'])//heads)
        layers=int(cfg['num_hidden_layers'])
        dtype_bytes=2
        kv=2*layers*kvheads*head_dim*dtype_bytes*batch*(context+steps)
        w=m['weight_total_bytes'];lo_ws,hi_ws=workspace[pid]
        lo=w+kv+int((lo_ws+1.0)*GIB);hi=w+kv+int((hi_ws+3.0)*GIB)
        cls='LIKELY_FITS_16GB' if hi<16*GIB*0.9 else 'LIKELY_DOES_NOT_FIT' if lo>16*GIB else 'BORDERLINE'
        result.append(dict(point_id=pid,model_key=key,weight_bytes=w,batch=batch,
                           context_plus_decode_tokens=context+steps,layers=layers,kv_heads=kvheads,
                           head_dim=head_dim,kv_dtype_bytes=dtype_bytes,theoretical_KV_bytes=kv,
                           workspace_low_GiB=lo_ws,workspace_high_GiB=hi_ws,
                           runtime_reserve_low_GiB=1.0,runtime_reserve_high_GiB=3.0,
                           estimated_total_low_bytes=lo,estimated_total_high_bytes=hi,
                           nominal_device_bytes=16*GIB,classification=cls,
                           static_only='NO_GPU_PROOF;loader_duplication_and_allocator_fragmentation_UNKNOWN',
                           design_review=('POINT_REQUIRES_DESIGN_REVIEW' if cls=='LIKELY_DOES_NOT_FIT' else 'CANARY_REQUIRED')))
    return result


def input_rows(freeze: dict,pack: Path) -> list[dict]:
    result=[]
    for item in freeze['entries']:
        path=pack/item['relative_path']
        payload=path.read_bytes()
        if hashlib.sha256(payload).hexdigest()!=item['utf8_sha256'] or len(payload)!=item['byte_count']:
            raise AssertionError('input byte closure '+item['source_text_id'])
        result.append(dict(source_text_id=item['source_text_id'],role=item['role'],
                           source=item['source'],dataset_repository=item['dataset_repository'],
                           observed_dataset_revision=item['observed_dataset_revision'],
                           revision_association=item['revision_association'],split=item['split'],
                           row_start=item['row_start'],row_end_inclusive=item['row_end_inclusive'],
                           relative_path=item['relative_path'],byte_count=item['byte_count'],
                           utf8_sha256=item['utf8_sha256'],token_ids='NOT_GENERATED',
                           source_url=item['source_url']))
    return result


def readiness_rows(points: list[dict],assets: list[dict],vram: list[dict]) -> list[dict]:
    asset={x['point_id']:x for x in assets};memory={x['point_id']:x for x in vram}
    result=[]
    for point in points:
        pid=point['point_id'];a=asset[pid];m=memory[pid]
        primary='NEW_ASSET_REQUIRED' if a['asset_status']!='ASSET_READY' else 'RUNTIME_UNQUALIFIED'
        result.append(dict(point_id=pid,scientific_role=point['scientific_role'],
                           asset_status=a['asset_status'],runtime_status='RUNTIME_UNQUALIFIED',
                           tokenizer_source_text='SOURCE_BYTES_FROZEN_TOKEN_IDS_PENDING',
                           instrumentation='SOURCE_PLAN_ONLY_109_CANARY_REQUIRED',
                           holdout_seal='NOT_OPERATIONAL' if pid in ('MP04','MP07','MP08') else 'NOT_APPLICABLE',
                           vram_static_classification=m['classification'],
                           readiness=primary,secondary_blocker=('VRAM_RISK' if m['classification']=='BORDERLINE' else 'IDENTITY_INCOMPLETE'),
                           ready_for_tier0_contract='false',
                           next_gate='separate project review after asset/runtime/tool/correctness and seal qualification'))
    return result


def question_rows() -> list[dict]:
    data=[
        ('DQ1','PRIMARY','MP01;MP02;MP06','MP07;MP08','dense asset and strong runtime absent;MoE fused runtime unknown'),
        ('DQ2','PRIMARY','MP02;MP03;MP05;MP06','MP04;MP07','Qwen BF16/AWQ assets absent;small-M and W4 backend not qualified'),
        ('DQ3','PRIMARY','MP01;MP02;MP03;MP05','MP08','dense assets/runtime absent;service oracle still requires Tier1 authority'),
        ('DQ4','PRIMARY','MP01;MP02;MP06','MP07;MP08','natural chronology instrumentation and matched strong runtime unqualified'),
        ('DQ4a','ANALYSIS_SUBQUESTION_OF_DQ4','MP01;MP02;MP06','MP07;MP08','producer-consumer boundary gap requires same-process Tier0 wall chronology'),
        ('DQ4b','ANALYSIS_SUBQUESTION_OF_DQ4','MP06','MP07','expert route sequence is not cache/page turnover;no Tier0 page trace'),
        ('SQ_TRANSLATION_AUTHORITY_ONLY','SECONDARY_AUTHORITY_ONLY','NONE','MP08','direct Ada TLB/PTW/blocked-time observable UNKNOWN'),
    ]
    return [dict(question_id=q,role=role,stage_A_points=stage,holdout_points=hold,
                 readiness='CAMPAIGN_QUESTION_NOT_EXECUTION_READY',blocker=why,
                 new_experiment_authorized='false') for q,role,stage,hold,why in data]


def seal_manifest(freeze: dict) -> dict:
    sha={item['source_text_id']:item['utf8_sha256'] for item in freeze['entries']}
    holdout={
        'MP04':['TRAIN_A_DISCOVERY_00']+[f'TRAIN_B_SEALED_{i:02}' for i in range(1,16)],
        'MP07':['TRAIN_A_DISCOVERY_00'],
        'MP08':['PG19_VALIDATION_11155_PREFIX'],
    }
    return dict(schema='C16_HOLDOUT_SEAL_MANIFEST_V1',
                status='INPUTS_FROZEN_OUTPUT_SEAL_UNPROVISIONED',
                holdout_points={pid:[dict(source_text_id=sid,utf8_sha256=sha[sid]) for sid in ids]
                                for pid,ids in holdout.items()},
                producer_can_generate_outputs_only_after_separate_109_authorization=True,
                output_storage='FUTURE_ENCRYPTED_ONLY_164_HOLDOUT_ROOT_NOT_CREATED',
                encryption_format='OPENSSL_CMS_AES256_DER_PROPOSED',
                recipient_certificate_sha256='UNPROVISIONED',
                recipient_private_key_location='COORDINATOR_ONLY_NOT_ON_109_OR_174',
                encrypted_output_sha256='NOT_PRODUCED',
                encrypted_outputs=[],
                authorized_freeze_receipt_sha256='UNPROVISIONED',
                trusted_coordination_commit='UNPROVISIONED',
                release_requires=['DQ_id','phenomenon','sign','estimator','materiality_threshold',
                                  'STOP_rule','exact_holdout_points','receipt_sha256_in_trusted_coordination_commit'],
                consumer_access_allowed=False,
                explicit_boundary='inputs public and frozen;holdout outputs nonexistent and future ciphertext inaccessible until authenticated freeze')


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=PACK)
    parser.add_argument('--source-pack',type=Path,default=PACK)
    args=parser.parse_args()
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    source=args.source_pack
    remote=read_json(source/'REMOTE_MODEL_METADATA.json')
    local=read_json(source/'LOCAL_164_ASSET_AUDIT.json')
    runtime=read_json(source/'RUNTIME_SOURCE_AUDIT.json')
    freeze=read_json(source/'INPUT_SOURCE_FREEZE.json')
    points=read_tsv(DESIGN/'MEASUREMENT_POINT_PLAN.tsv')
    if len(points)!=8 or set(MODEL_FOR_POINT)!={x['point_id'] for x in points}:
        raise AssertionError('frozen eight-point identity')
    model=model_rows(remote);assets=asset_rows(points,remote,local);run=runtime_rows(remote,runtime)
    comp=compatibility_rows(runtime);memory=vram_rows(points,remote);inputs=input_rows(freeze,source)
    ready=readiness_rows(points,assets,memory);questions=question_rows()
    outputs={
        'MODEL_IDENTITY_PINS.tsv':model,'ASSET_READINESS.tsv':assets,
        'RUNTIME_STRONG_BASELINE_PINS.tsv':run,'SM89_STATIC_COMPATIBILITY.tsv':comp,
        'VRAM_FEASIBILITY.tsv':memory,'INPUT_SOURCE_MANIFEST.tsv':inputs,
        'POINT_EXECUTION_READINESS.tsv':ready,'QUESTION_EXECUTION_READINESS.tsv':questions,
    }
    for name,rows in outputs.items():
        write_tsv(out/name,rows)
    write_json(out/'HOLDOUT_SEAL_MANIFEST.json',seal_manifest(freeze))
    print(json.dumps(dict(point_ready=sum(x['ready_for_tier0_contract']=='true' for x in ready),
                          assets={k:v['status'] for k,v in local['models'].items()},
                          input_streams=len(inputs),vram={x['point_id']:x['classification'] for x in memory}),sort_keys=True))


if __name__=='__main__':
    main()
