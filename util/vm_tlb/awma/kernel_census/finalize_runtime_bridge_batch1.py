#!/usr/bin/env python3
import csv,hashlib,json,re
from pathlib import Path
ROOT=Path('/data/c16/awma/runtime_identity_bridge_batch1_20260924')
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-runtime-bridge-batch1-v1')
OUT=REPO/'docs/vm_tlb/review_packs/AWMA_PRODUCER_RUNTIME_IDENTITY_BRIDGE_AND_BATCH1_REPLAN_109_V1'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tsv(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
def terminal(d):
    lines=[x for x in (d/'stdout.log').read_text(errors='replace').splitlines() if 'ROUTEB_TERMINAL_COMPLETE' in x]
    return lines[-1]
captures=[]
specs=[
 ('A1','S2','STR_8bc741e5debc',16,16828,1097,'A1_formal'),
 ('A2','T8192','STR_8bc741e5debc',16,16828,1097,'A2_formal'),
 ('C1_REPLACEMENT','S2','STR_8a5773a1d265',16,16795,1440,'C1_replacement_formal'),
 ('C2_REPLACEMENT','D128','STR_8a5773a1d265',96,101035,9120,'C2_replacement_formal')]
for tid,sc,sid,step,nav,ord_,dn in specs:
    d=ROOT/dn; ident=json.loads((d/'IDENTITY.json').read_text()); tr=next((d/'raw').glob('*.trace.xz')); tg=next((d/'raw').glob('*.traceg.xz'))
    captures.append(dict(target_id=tid,scenario=sc,scientific_target_id=sid,decode_step=step,producer_global_navigation=nav,producer_selector_ordinal=ord_,grid=ident['grid'],block=ident['block'],producer_demangle=ident['producer_demangle'],trace_xz_sha256=sha(tr),traceg_xz_sha256=sha(tg),traceg_size_bytes=tg.stat().st_size,terminal=terminal(d),grammar_status='TRACEG_GRAMMAR_PASS',node164_path=f'/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/{dn}/'))
tsv('CAPTURE_MANIFEST.tsv',captures)
bridge=[]
for x in captures:
    bridge.append(dict(scenario=x['scenario'],scientific_target_id=x['scientific_target_id'],nsys_exact_implementation='CUBLAS_GEMV_CANONICAL',routeb_exact_producer_demangle=x['producer_demangle'],canonical_bridge_rule='CUBLAS_GEMV_TEMPLATE_KIND_PLUS_EXACT_GRID_BLOCK_AND_RECURRENCE',grid=x['grid'],block=x['block'],accepted_recurrence='STABLE_24' if x['scientific_target_id']=='STR_8bc741e5debc' else 'STABLE_48',fresh_producer_recurrence=24 if x['scientific_target_id']=='STR_8bc741e5debc' else 48,scientific_step=x['decode_step'],fresh_producer_selector_ordinal=x['producer_selector_ordinal'],fresh_producer_global_navigation=x['producer_global_navigation'],status='NSYS_TO_ROUTEB_IDENTITY_BRIDGE_PASS'))
bridge.append(dict(scenario='S2;B4',scientific_target_id='STR_01503476cf8d',nsys_exact_implementation='EXACT_SHA256_1dcd309bfcaf4619985c9773e3174747e99765bae9400e943b6c6c44db5ba036',routeb_exact_producer_demangle='CatArrayBatchedCopy_contig<OpaqueType<2>,uint,4,128,1>',canonical_bridge_rule='SOURCE_SUPPORTED_COPY_CONTIG_TEMPLATE_PLUS_EXACT_GRID_BLOCK_AND_VARIABLE_RECURRENCE',grid='152,2,1',block='512,1,1',accepted_recurrence='VARIABLE_0_48',fresh_producer_recurrence='STEP1_0_STEPS2_32_48',scientific_step=2,fresh_producer_selector_ordinal=0,fresh_producer_global_navigation='2066;2090',status='BRIDGE_PASS_CAPTURE_STOPPED_ON_TRUE_GRAMMAR_GAP_LDC_WIDTH'))
tsv('PRODUCER_RUNTIME_IDENTITY_BRIDGE.tsv',bridge)
pairs=[
 dict(pair='A_CONTEXT_LENGTH',target='STR_8bc741e5debc',disposition='CAPTURE_COMPLETE_BOTH_SIDES',detail='S2 and T8192 grammar-pass payloads'),
 dict(pair='B_BATCH',target='STR_01503476cf8d',disposition='STOP_PAIR_B_GRAMMAR_SEMANTIC_GAP',detail='B1 terminal/accounting pass; validator rejects LDC zero/missing width; B2 not run'),
 dict(pair='C_SCIENTIFIC_HOLDOUT',target='STR_8a5773a1d265',disposition='CAPTURE_COMPLETE_BOTH_SIDES',detail='preregistered replacement C1 selected before capture; S2 step16 and D128 step96 grammar-pass payloads')]
tsv('PAIR_MANIFEST.tsv',pairs)
tsv('HOLDOUT_MANIFEST.tsv',[dict(holdout='SCIENTIFIC_HOLDOUT_CROSS_CONTEXT_V1',original_target='STR_fb002dc5652b',original_disposition='ORIGINAL_HOLDOUT_PRODUCER_RUNTIME_DISPATCH_MISMATCH',replacement_priority='STR_8a5773a1d265 then STR_6d8d2509696c',frozen_replacement='STR_8a5773a1d265',s2_step=16,d128_step=96,status='CAPTURED_AND_QUALIFIED_NO_MECHANISM_EXECUTION')])
receipt={'stage':'AWMA_PRODUCER_RUNTIME_IDENTITY_BRIDGE_AND_BATCH1_REPLAN_109_V1','producer_authority':'5143b4e10aaf2fc47bb60492155d2464b0b726fd','producer_binary_sha256':'8fa6fe9fe62d4f66788c46804fbfa25614f43ff8eb8e39328383b17343b3fbcf','postprocessor_sha256':'db0dec8aa8af92476d05c4f27343e3ed70098f4f16bcc6f20cd7ac4c9d2fb10e','validator_sha256':'135761ac8e10a7fb6c98a3413cd477602d84b164a778c5d4f2a1bfb517be5b37','captures_qualified':4,'pairs_complete':2,'pairs_stopped':1,'accel_sim_runs':0,'mechanism_runs':0}
(OUT/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
report='''# AWMA producer-runtime identity bridge and Batch1 replan 109 V1\n\nStatus: COMPLETE — two pairs captured and qualified; Pair B stopped at an authentic grammar semantic gap.\n\nNSYS global launch indices are treated only as run-local navigation. Scientific identities are bridged to fresh Route-B producer demangles, exact shapes, recurrence, deterministic path occurrence, producer ordinals, and fresh producer navigation. Pair A and the preregistered Pair C replacement closed and produced four grammar-pass simulator-native payloads. Pair B used only the frozen Lane D COPY fallback, but stopped after B1 because `LDC` had zero/missing width; the validator was not weakened and B2 was not run.\n\nNo Accel-Sim or mechanism execution occurred. Pair C remains a scientific holdout. Raw payloads are durably published on node164.\n'''
(REPO/'docs/vm_tlb/codex_handoff/awma/AWMA_PRODUCER_RUNTIME_IDENTITY_BRIDGE_AND_BATCH1_REPLAN_109_V1_REPORT.md').write_text(report)
files=sorted(p for p in OUT.iterdir() if p.is_file())
(OUT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
print(json.dumps(receipt,sort_keys=True))
