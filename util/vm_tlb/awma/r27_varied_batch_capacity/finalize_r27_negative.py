#!/usr/bin/env python3
"""CPU-only R27 Gate-B negative finalizer."""

from __future__ import annotations

import argparse,csv,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path


STAGE='AWMA_R27_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1'
DECISION='R27_INPUT_OR_SOURCE_NOT_QUALIFIED'
URL='https://huggingface.co/datasets/Salesforce/wikitext/resolve/8aaa8b27d493dba10b8553290236799e6dc57829/wikitext-2-raw-v1/train-00000-of-00001.parquet'


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def tsv(p,rows):
    with Path(p).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sums(pack):
    rows=[f'{sha(f)}  {f.relative_to(pack).as_posix()}' for f in sorted(x for x in pack.rglob('*') if x.is_file() and x.name!='SHA256SUMS')]
    (pack/'SHA256SUMS').write_text('\n'.join(rows)+'\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--repo',required=True);ap.add_argument('--pack',required=True);a=ap.parse_args()
    root,repo,pack=Path(a.root),Path(a.repo),Path(a.pack);pack.mkdir(parents=True,exist_ok=True)
    gate_a=load(root/'raw/R26_RAW_READBACK.json')
    if not gate_a['qualified']:raise SystemExit('Gate A is not qualified')
    acquisition={
        'schema':'R27_INPUT_ACQUISITION_RECEIPT_V1','stage':STAGE,'status':DECISION,
        'dataset':{'repo':'Salesforce/wikitext','revision':'8aaa8b27d493dba10b8553290236799e6dc57829','config':'wikitext-2-raw-v1','split':'train','relative_file':'wikitext-2-raw-v1/train-00000-of-00001.parquet','source_url':URL,'expected_bytes':6357543,'expected_sha256':'e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7'},
        'attempts':[
            {'environment':'node109','source':URL,'method':'curl exact URL','attempts':1,'result':'connection timeout after >80 seconds; interrupted; zero bytes'},
            {'environment':'local_execution_environment','source':URL,'method':'curl exact URL','attempts':3,'connect_timeout_seconds':20,'result':'three connection timeouts; zero bytes'},
            {'environment':'node164_storage_host','source':URL,'method':'curl exact URL','attempts':3,'connect_timeout_seconds':20,'result':'three connection timeouts; zero bytes'},
            {'environment':'controlled_web_access','source':URL,'method':'exact URL open/search','attempts':2,'result':'no downloadable response or filesystem artifact'},
        ],
        'cache_searches':[
            {'environment':'node109','roots':['/data/c16','/home/huangrulin/.cache','/home/huangrulin/workspace'],'predicate':'exact size 6357543 bytes','matches':0},
            {'environment':'node164','roots':['/root/.cache/huggingface','/root/share/mnt164/huangrulin/.cache/huggingface'],'predicate':'exact size 6357543 bytes','matches':0},
        ],
        'node109_final_path':str(root/'input/train-00000-of-00001.parquet'),'node109_file_present':False,
        'node164_incoming_file_present':False,'bytes_acquired':0,'sha256_verified':False,
        'alternate_source_used':False,'validation_or_test_used':False,'tokenization_started':False,
        'CUDA_operations':0,'GPU_lock_acquisitions':0,'stopped_before_new_CUDA':True,
        'completed_utc':datetime.now(timezone.utc).isoformat(),
    }
    dump(root/'raw/INPUT_ACQUISITION_RECEIPT.json',acquisition)
    gate_status={'stage':STAGE,'decision':DECISION,'gates':{'A_R26_RAW_READBACK':{'status':'PASS','label':gate_a['status'],'remote_manifest_items':gate_a['remote_readback']['manifest_ok_entries'],'endpoint_receipt_log_files':len(gate_a['selected_file_evidence'])},'B_VARIED_INPUT_AND_COMPONENT':{'status':'STOP','reason':'exact authorized parquet unavailable from all allowed network/cache paths','dataset_bytes_acquired':0},'C_NATURAL_CAPACITY_SEARCH':{'status':'NOT_RUN'},'D_POSITIVE_ONLY_32_STEP':{'status':'NOT_RUN'}},'CUDA_operations':0,'formal_timing':False,'production_pilot':False,'hardware_work':False}
    dump(pack/'GATE_STATUS.json',gate_status);dump(pack/'INPUT_ACQUISITION_RECEIPT.json',acquisition)
    shutil.copy2(root/'raw/R26_RAW_READBACK.json',pack/'R26_RAW_READBACK.json')
    shutil.copy2(repo/'docs/vm_tlb/chatgpt_handoff/awma/r27_varied_batch_capacity_v1/PARENT_AUTHORITY.json',pack/'PARENT_AUTHORITY.json')
    source=[]
    for p in [repo/'util/vm_tlb/awma/r27_varied_batch_capacity/gate_a_readback.py',repo/'docs/vm_tlb/chatgpt_handoff/awma/r27_varied_batch_capacity_v1/R27_EXPERIMENT_CONTRACT.json',repo/'docs/vm_tlb/chatgpt_handoff/awma/r27_varied_batch_capacity_v1/LANE_G_R27_VARIED_BATCH_CAPACITY_109_GOAL.md']:
        source.append({'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)})
    dump(pack/'SOURCE_IDENTITY.json',{'handoff_head':'5144bde8f9d7b399a596395e0c88ee89025b3a6f','handoff_tree':'605f0360debb3f62a1923452c91552ca1f2acaa9','sources':source})
    validation={'Gate_A':{'qualified':True,'archive_sha256':gate_a['authority_files']['archive']['sha256'],'manifest_sha256':gate_a['authority_files']['manifest']['sha256'],'common_checkpoint_sha256':gate_a['authority_files']['common_checkpoint']['sha256'],'remote_ok':gate_a['remote_readback']['manifest_ok_entries'],'endpoint_groups':gate_a['endpoint_group_counts'],'errors':gate_a['errors']},'Gate_B':{'qualified':False,'classification':DECISION,'input_bytes':0},'new_CUDA_work':0}
    dump(pack/'VALIDATION_SUMMARY.json',validation)
    dump(pack/'RESOURCE_LOCK_RECEIPTS.json',{'gpu_lock':'/data/c16/locks/c16_gpu_campaign.lock','acquisitions':0,'CUDA_or_JIT_operations':0,'final_lock_owner':None,'campaign_GPU_processes':[]})
    decision={'stage':STAGE,'decision':DECISION,'priority_rule':'Gate B qualification STOP before capacity observation','Gate_A_parent_raw':'QUALIFIED','Gate_B_input':'NOT_QUALIFIED','Gate_C':'NOT_RUN','Gate_D':'NOT_RUN','scientific_interpretation':'No varied-input capacity or numerical conclusion exists; failure is input availability, not a negative GPU result','R26_conclusion_changed':False}
    dump(pack/'FINAL_DECISION.json',decision)
    (pack/'ENGINEERING_ATTEMPTS.md').write_text("""# Engineering attempts\n\nGate A initially reported expected-hash mismatches because four SHA constants were transcribed with duplicated characters at wrapped line boundaries. Direct 64-character values from `PARENT_AUTHORITY.json` were substituted; evidence bytes were unchanged, and the complete Gate A audit then passed.\n\nThe exact authorized parquet URL was attempted on node109, the local execution environment, and node164. All network paths timed out before receiving bytes. Bounded exact-size searches of known node109 and node164 Hugging Face/cache roots found no byte-identical cached copy. No alternate URL, corpus, split, model, tokenizer, or generated proxy was used.\n""")
    (pack/'OPEN_ISSUES.md').write_text("""# Open issues\n\nThe exact pinned WikiText-2 train parquet was unavailable from all authorized network/cache paths. A future review may provide the byte-exact 6,357,543-byte payload with SHA256 `e83889...0c9f7`; this execution must not be resumed implicitly. No CUDA work began.\n""")
    (pack/'FINAL_DECISION.md').write_text(f"""# Final decision\n\n`{DECISION}`\n\nGate A independently qualified the R26 raw witness: 207 node164 manifest entries, the archive/common checkpoint, 12 endpoint confirmation receipts and logs, the B71 five-step 3/3 witness, and frozen source all match.\n\nGate B stopped before tokenization and before CUDA because the sole authorized WikiText-2 train parquet could not be obtained byte-for-byte. Direct downloads timed out from all available network environments and bounded cache searches found no exact-size candidate. Gates C/D, formal timing, production work, and hardware work were not run. This is an input-authority availability STOP, not a capacity or numerical negative.\n""")
    (pack/'README.md').write_text(f"""# {STAGE}\n\nStart with `FINAL_DECISION.md`. Decision: `{DECISION}`. Gate A qualified the complete parent R26 raw witness; Gate B could not acquire the only authorized pinned parquet and stopped with CUDA=0. `R26_RAW_READBACK.json` and `INPUT_ACQUISITION_RECEIPT.json` are the primary evidence.\n""")
    report=repo/'docs/vm_tlb/codex_handoff/awma/r27_varied_batch_capacity_v1/LANE_G_FINAL_REPORT.md';report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(f"""# Lane G R27 final report\n\nDecision: `{DECISION}`. Gate A independently passed for the R26 node164 archive, 207-item manifest, common checkpoint and endpoint witness. Gate B stopped before tokenization/CUDA because the exact pinned WikiText-2 train parquet was unreachable and absent from bounded caches. Gates C/D were not run; there is no R27 varied-input capacity result.\n""")
    raw=[]
    for sub in (root/'raw',root/'receipts',root/'logs'):
        for f in sorted(x for x in sub.rglob('*') if x.is_file()):raw.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f),'role':sub.name})
    # Parent common payload remains immutable at its already verified R26 node164 location.
    raw.append({'path':'/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r26_tied_weight_production_capacity_boundary_109_v1_20261002/checkpoints/COMMON_POST_BOOTSTRAP.pt','bytes':2626691315,'sha256':'09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55','role':'external_parent_checkpoint'})
    tsv(pack/'RAW_DATA_INDEX.tsv',raw)
    sums(pack)
    print(json.dumps(decision,indent=2,sort_keys=True))


if __name__=='__main__':main()
