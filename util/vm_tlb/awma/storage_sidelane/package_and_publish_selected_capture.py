#!/usr/bin/env python3
"""Close one already-qualified selected capture and publish it through Pipeline V1.

This deliberately never creates SIM_INPUT material: it creates only an immutable
producer bundle, transfers it to the qualified node164 inbox, and waits for the
independent verify/admit/ACK chain.
"""
from __future__ import annotations

import argparse, hashlib, json, lzma, re, shutil, socket, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

AUTH = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-producer-authority-v1')
DP = AUTH / 'util/vm_tlb/c16/data_plane'
ROOT164 = '/root/share/mnt164/huangrulin/c16_ai_workload'
STAGING = Path('/data/c16/capture/staging')
READY = Path('/data/c16/capture/ready')
TRANSFERRED = Path('/data/c16/capture/transferred')
BINROOT = Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin')
PARSER = Path('/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/hotfix_fb5d0b_admission/traceg_grammar_smoke_fb5d0b')

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''): h.update(b)
    return h.hexdigest()

def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)

def header(trace: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    with lzma.open(trace, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#traces format'): break
            if line.startswith('-') and '=' in line:
                k,v=line[1:].split('=', 1); fields[k.strip()] = v.strip()
    return fields

def command(argv: list[str], out: Path) -> None:
    with out.open('w', encoding='utf-8') as f: subprocess.run(argv, check=True, stdout=f, stderr=subprocess.STDOUT, text=True)

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('--capture', type=Path, required=True); ap.add_argument('--run-id', required=True); x=ap.parse_args()
    cdir=x.capture.resolve(); run=x.run_id
    if not re.fullmatch(r'C16R_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_\d{8}T\d{6}Z_[0-9a-f]{12}', run): raise SystemExit('unsafe/noncanonical run id')
    receipt=json.loads((cdir/'CAPTURE_RECEIPT.json').read_text())
    if receipt.get('status') != 'FORMAL_LOCAL_COMPLETE': raise SystemExit('not a locally complete formal capture')
    candidate=json.loads((cdir/'TARGET_IDENTITY.json').read_text())
    trace=next((cdir/'raw').glob('kernel-*.trace.xz')); traceg=next((cdir/'raw').glob('kernel-*.traceg.xz'))
    h=header(trace); stage=STAGING/run
    if stage.exists() or (READY/run).exists() or (TRANSFERRED/run).exists(): raise SystemExit('run id collision')
    stage.mkdir(parents=True); (stage/'CAPTURING').write_text('CAPTURING\n')
    for src,rel in [(trace,'traces/'+trace.name),(traceg,'traces/'+traceg.name),(cdir/'raw/kernelslist','traces/kernelslist'),(cdir/'raw/kernelslist.g','traces/kernelslist.g'),(cdir/'CAPTURE_RECEIPT.json','receipts/CAPTURE_RECEIPT.json'),(cdir/'TARGET_IDENTITY.json','sidecars/TARGET_IDENTITY.json'),(cdir/'CAPTURE_COMMAND.json','receipts/CAPTURE_COMMAND.json'),(cdir/'GUARD.json','receipts/GUARD.json'),(cdir/'lifecycle.log','receipts/LIFECYCLE.log'),(cdir/'driver.stdout','receipts/DRIVER.stdout'),(cdir/'driver.stderr','receipts/DRIVER.stderr'),(cdir/'postprocess.stdout','receipts/POSTPROCESS.stdout'),(cdir/'postprocess.stderr','receipts/POSTPROCESS.stderr'),(cdir/'validator.stdout','receipts/VALIDATOR.stdout'),(cdir/'validator.stderr','receipts/VALIDATOR.stderr'),(cdir/'SHA256SUMS','receipts/CAPTURE_SHA256SUMS')]: copy(src,stage/rel)
    source=AUTH/'util/tracer_nvbit/route_b_1771/route_b_tracer.cu'; fmt=AUTH/'util/tracer_nvbit/route_b_1771/route_b_raw_formatter.hpp'; driver=Path('/data/c16/awma/storage_sidelane_v1/requalification_20260917T121512Z/driver.py')
    build={'accepted_producer_commit':'5143b4e10aaf2fc47bb60492155d2464b0b726fd','route_b_source_sha256':sha(source),'formatter_sha256':sha(fmt),'tracer_binary_sha256':sha(BINROOT/'route_b_5143.so'),'postprocessor_source_sha256':sha(AUTH/'util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing.cpp'),'postprocessor_binary_sha256':sha(BINROOT/'post-traces-processing_5143'),'validator_binary_sha256':sha(PARSER),'driver_sha256':sha(driver),'runtime':{'python':'/data/c16/env/c16-py310/bin/python','torch':'2.5.1+cu124','transformers':'4.46.3','dtype':'float16','attention_backend':'sdpa','cuda_toolkit':'12.8'}}
    context={'schema_version':'AWMA_ADDRESS_CONTEXT_V1','context_from_trace_member':trace.name,'cuda_context_observed':re.search(r'ctx_0x[0-9a-f]+',trace.name).group(0),'asid_epoch':'0','va_width':49,'page_policy':'4K','shmem_base_addr':h['shmem base_addr'],'local_mem_base_addr':h['local mem base_addr'],'address_mode_policy':'MODE1_BASE_STRIDE_OR_MODE0_LIST_ALL_ONLY','mode2_records':0}
    terminal={'status':'COMPLETE','drop_count':0,'overflow_count':0,'device_channel_order':['device_kernel_complete','channel_flush_complete','receiver_fully_drained','trace_sink_closed','terminal_complete'],'receipt_line':receipt['terminal_line']}
    for name,obj in [('BUILD_RUNTIME_RECEIPT.json',build),('ADDRESS_CONTEXT.json',context),('TERMINAL_RECEIPT.json',terminal)]:
        p=stage/'sidecars'/name; p.parent.mkdir(exist_ok=True); p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    asset=Path('/data/c16/models/.provenance/c16_recovery_v3/receipts/R1_QWEN2P5_0P5B_ASSET_RECEIPT.json'); inputr=Path('/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S2_TEXT/C16_FROZEN_INPUT_BINDING_TRANSFER_RECEIPT.json')
    copy(asset,stage/'authority'/asset.name); copy(inputr,stage/'authority'/inputr.name)
    manifest={'schema_version':1,'run_id':run,'created_at_utc':datetime.now(timezone.utc).isoformat(),'scientific_status':'FORMAL','producer':{'hostname':socket.gethostname(),'gpu_name':'NVIDIA GeForce RTX 4080','gpu_uuid':'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59','driver':'580.178.04','cuda':'12.8'},'git':{'repository':'accel-sim-framework','commit':'5143b4e10aaf2fc47bb60492155d2464b0b726fd','dirty':False},'model':{'model_id':'Qwen/Qwen2.5-0.5B-Instruct','revision':'7ae557604adf67be50417f59c2c2f167def9a775','asset_receipt_sha256':sha(asset)},'input':{'binding_id':'S2_TEXT','authority_status':'PASS_HASH_CLOSED_EXACT_FROZEN_BINDING','receipt_sha256':sha(inputr),'token_ids_sha256_or_semantic_hash':'0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'},'scenario':{'batch':1,'prefill_tokens':2048,'decode_tokens':32,'input_class':'TEXT','phase':candidate['phase']},'runtime':build['runtime'],'capture':{'instrument':'AWMA_ROUTE_B_NVBIT1771_SIM_NATIVE','tool_version':'NVBit 1.7.7.1','tool_identity_sha256_if_applicable':sha(BINROOT/'route_b_5143.so'),'target':candidate['candidate_id']+'; producer-function-occurrence='+str(candidate['producer_selector_function_ordinal']),'exact_argv':json.loads((cdir/'CAPTURE_COMMAND.json').read_text())['argv']},'artifacts':[]}
    (stage/'RUN_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    (stage/'CAPTURING').unlink()
    command(['/data/c16/env/c16-py310/bin/python',str(DP/'finalize_capture.py'),'--staging',str(stage),'--ready',str(READY),'--manifest',str(stage/'RUN_MANIFEST.json'),'--run-id',run],cdir/'pipeline_finalize.stdout')
    ready=READY/run
    # Re-close after adding a finalizer receipt would alter the immutable
    # manifest; keep that command receipt beside the producer capture instead.
    source_manifest=sha(ready/'RUN_MANIFEST.json'); close=json.loads((ready/'LOCAL_CLOSE_RECEIPT.json').read_text())
    remote=f'hrl174new:{ROOT164}/inbox/{run}.partial/'
    command(['rsync','-r','--partial','--append-verify','--protect-args','--no-owner','--no-group','--no-perms','--omit-dir-times',str(ready)+'/',remote],cdir/'pipeline_rsync.stdout')
    remote_script=f'''set -euo pipefail\ncd /root/workspace/awma-hotfix-admit\nroot={ROOT164}\nrun={run}\npython3 util/vm_tlb/c16/data_plane/verify_capture.py --root "$root" --run-id "$run" --output "$root/reports/verification_receipts/$run.VERIFY.json"\npython3 util/vm_tlb/c16/data_plane/admit_capture.py --root "$root" --verification-receipt "$root/reports/verification_receipts/$run.VERIFY.json" --output "$root/reports/admission_receipts/$run.ADMIT.json"\npython3 util/vm_tlb/c16/data_plane/write_transfer_ack.py --root "$root" --admission-receipt "$root/reports/admission_receipts/$run.ADMIT.json"\ncat "$root/reports/transfer_acks/$run.TRANSFER_ACK.json"\n'''
    tmp=Path('/tmp')/(run+'.remote_admit.sh'); tmp.write_text(remote_script); subprocess.run(['scp',str(tmp),'hrl174new:'+str(tmp)],check=True); command(['ssh','hrl174new','bash',str(tmp)],cdir/'pipeline_remote_admit.stdout')
    ack_local=cdir/'TRANSFER_ACK.json'; subprocess.run(['scp',f'hrl174new:{ROOT164}/reports/transfer_acks/{run}.TRANSFER_ACK.json',str(ack_local)],check=True)
    command(['/data/c16/env/c16-py310/bin/python',str(DP/'verify_remote_ack.py'),'--ack',str(ack_local),'--run-id',run,'--manifest-sha',source_manifest,'--destination',f'{ROOT164}/raw/{run}','--file-count',str(close['file_count']),'--total-bytes',str(close['total_bytes']),'--ready',str(READY),'--transferred',str(TRANSFERRED)],cdir/'pipeline_ack.stdout')
    print(json.dumps({'run_id':run,'manifest_sha256':source_manifest,'durable_path':f'{ROOT164}/raw/{run}','ack_sha256':sha(ack_local)},sort_keys=True))

if __name__=='__main__': main()
