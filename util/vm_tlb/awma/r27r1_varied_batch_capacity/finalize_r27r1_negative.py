#!/usr/bin/env python3
"""CPU-only R27R1 Gate-B0 input-unavailable finalizer."""

import argparse,csv,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path


STAGE='AWMA_R27R1_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1';DECISION='R27R1_INPUT_OR_SOURCE_NOT_QUALIFIED'
PINNED='https://huggingface.co/datasets/Salesforce/wikitext/resolve/8aaa8b27d493dba10b8553290236799e6dc57829/wikitext-2-raw-v1/train-00000-of-00001.parquet'
MAIN='https://huggingface.co/datasets/Salesforce/wikitext/resolve/main/wikitext-2-raw-v1/train-00000-of-00001.parquet'
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
 (pack/'SHA256SUMS').write_text('\n'.join(f'{sha(f)}  {f.relative_to(pack).as_posix()}' for f in sorted(x for x in pack.rglob('*') if x.is_file() and x.name!='SHA256SUMS'))+'\n')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--repo',required=True);ap.add_argument('--pack',required=True);a=ap.parse_args();root,repo,pack=Path(a.root),Path(a.repo),Path(a.pack);pack.mkdir(parents=True,exist_ok=True)
 gate=load(root/'raw/PARENT_IDENTITY_RECHECK.json')
 if not gate['qualified']:raise SystemExit('Gate A not qualified')
 receipt={'schema':'R27R1_GATE_B0_INPUT_ACQUISITION_V1','stage':STAGE,'status':DECISION,'payload':{'repo':'Salesforce/wikitext','revision':'8aaa8b27d493dba10b8553290236799e6dc57829','config':'wikitext-2-raw-v1','split':'train','file':'wikitext-2-raw-v1/train-00000-of-00001.parquet','expected_bytes':6357543,'expected_sha256':'e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7','pinned_url':PINNED,'official_main_url':MAIN},'prior_closed_R27':{'decision':'R27_INPUT_OR_SOURCE_NOT_QUALIFIED','pinned_URL_attempted_on_node109_local_node164':True,'cached_exact_copy_found':False},'R27R1_attempts':[{'environment':'node109','url':MAIN,'result':'curl connect timeout after 20 seconds; zero bytes','log':str(root/'logs/GATE_B0_NODE109_MAIN_DOWNLOAD.log')},{'environment':'local_execution_environment','url':MAIN,'result':'curl connect timeout after 20 seconds; zero bytes'},{'environment':'node164_storage_host','url':MAIN,'result':'curl connect timeout; zero bytes','log':str(root/'logs/GATE_B0_NODE164_MAIN_DOWNLOAD.log')},{'environment':'controlled_browser_transport','url':MAIN,'result':'browser runtime initialization failed twice; no file created'},{'environment':'local_workspace_exact_size_search','predicate':'6357543 bytes','result':'zero matches'}],'producer_file_present':False,'bytes_acquired':0,'local_size_sha_admission':False,'node164_input_admission_started':False,'tokenization_started':False,'CUDA_JIT_operations':0,'GPU_lock_acquisitions':0,'alternate_payload_used':False,'completed_utc':datetime.now(timezone.utc).isoformat()}
 dump(root/'raw/INPUT_ACQUISITION_RECEIPT.json',receipt);dump(pack/'INPUT_ACQUISITION_RECEIPT.json',receipt);dump(pack/'PARENT_IDENTITY_RECHECK.json',gate)
 shutil.copy2(repo/'docs/vm_tlb/chatgpt_handoff/awma/r27r1_varied_batch_capacity_continuation_v1/SOURCE_AUTHORITY.json',pack/'SOURCE_AUTHORITY.json')
 status={'stage':STAGE,'decision':DECISION,'gates':{'A_ACCEPTED_PARENT_IDENTITY_RECHECK':{'status':'PASS','full_207_audit_rerun':False,'reused_R27_parent_raw_qualification':True},'B0_EXACT_INPUT_ACQUIRE_ADMIT':{'status':'STOP','bytes_acquired':0,'reason':'exact payload unavailable on all authorized transports/caches'},'B1_BANK_NUMERIC_AND_IMPLEMENTATION_FREEZE':{'status':'NOT_RUN'},'C_NATURAL_CAPACITY_SEARCH':{'status':'NOT_RUN'},'D_POSITIVE_ONLY_32_STEP_AND_RESUME':{'status':'NOT_RUN'}},'CUDA_JIT_operations':0,'GPU_lock_acquisitions':0,'formal_timing':False}
 dump(pack/'GATE_STATUS.json',status);dump(pack/'FINAL_DECISION.json',{'stage':STAGE,'decision':DECISION,'scientific_interpretation':'Input availability STOP before tokenization/CUDA; no R27R1 capacity or numerical result','closed_R27_unchanged':True})
 source=[]
 for p in [repo/'util/vm_tlb/awma/r27r1_varied_batch_capacity/gate_a_recheck.py',repo/'docs/vm_tlb/chatgpt_handoff/awma/r27r1_varied_batch_capacity_continuation_v1/R27R1_EXPERIMENT_CONTRACT.json',repo/'docs/vm_tlb/chatgpt_handoff/awma/r27r1_varied_batch_capacity_continuation_v1/LANE_G_R27R1_VARIED_BATCH_CAPACITY_109_GOAL.md']:
  source.append({'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)})
 dump(pack/'SOURCE_IDENTITY.json',{'handoff_head':'ad361be589de85787c3f724582ae1862cb3c3539','handoff_tree':'aa0acb61acd0e1a2fa16fedd75cf8d69d314f06e','sources':source})
 dump(pack/'VALIDATION_SUMMARY.json',{'Gate_A':{'qualified':True,'closed_R27_pack_entries':gate['closed_R27']['review_pack_entries'],'common_checkpoint_sha256':gate['consumed_common_checkpoint']['sha256'],'model_payload_bytes':gate['model']['payload_total_bytes'],'errors':gate['errors']},'Gate_B0':{'qualified':False,'classification':DECISION,'bytes':0},'CUDA_JIT':0})
 dump(pack/'RESOURCE_LOCK_RECEIPTS.json',{'gpu_lock':'/data/c16/locks/c16_gpu_campaign.lock','acquisitions':0,'CUDA_JIT_operations':0,'campaign_processes':[]})
 (pack/'ENGINEERING_ATTEMPTS.md').write_text("""# Engineering attempts\n\nThe bounded accepted-parent identity recheck passed without rerunning R27's historical 207-item audit. The R26 common checkpoint was read back again from node164 and its file/tensor identities, logical step, model payloads, R26 component, and CCE source matched.\n\nFor Gate B0, the newly authorized official current-main URL was attempted from node109, the local execution environment, and node164. All timed out before receiving bytes. The built-in browser transport could not initialize and produced no artifact. The closed R27 already records bounded pinned-URL and cache attempts. No alternate payload, mirror, corpus, split, or reserialization was used.\n""")
 (pack/'OPEN_ISSUES.md').write_text("""# Open issues\n\nThe sole exact 6,357,543-byte parquet remains unavailable. A future separately reviewed continuation may provide the exact file with SHA256 `e83889...0c9f7`; this execution must not be implicitly resumed.\n""")
 (pack/'FINAL_DECISION.md').write_text(f"""# Final decision\n\n`{DECISION}`\n\nGate A bounded identity recheck passed and reused the accepted closed-R27 parent-raw qualification. Gate B0 could not acquire the exact parquet from either official transport or an existing exact local copy, so node164 input admission and tokenization never began. CUDA/JIT and GPU-lock acquisitions are zero; B1/C/D were not run. This is an input-availability STOP, not a varied-input capacity or numerical negative. Closed R27 remains unchanged.\n""")
 (pack/'README.md').write_text(f"""# {STAGE}\n\nStart with `FINAL_DECISION.md`. Decision: `{DECISION}`. Gate A passed by bounded identity recheck; Gate B0 stopped before admission/tokenization/CUDA because the only authorized byte-exact parquet remained unavailable.\n""")
 report=repo/'docs/vm_tlb/codex_handoff/awma/r27r1_varied_batch_capacity_continuation_v1/LANE_G_FINAL_REPORT.md';report.parent.mkdir(parents=True,exist_ok=True);report.write_text(f"""# Lane G R27R1 final report\n\nDecision: `{DECISION}`. The accepted R27 parent identity and the exact R26 common checkpoint/model/source consumed by this continuation passed bounded recheck. The exact WikiText-2 train parquet remained unavailable from the official current-main URL and existing local sources, so B0 stopped with tokenization=0, CUDA/JIT=0 and GPU lock=0. B1/C/D were not run; closed R27 was not resumed or modified.\n""")
 raw=[]
 for sub in (root/'raw',root/'receipts',root/'logs'):
  for f in sorted(x for x in sub.rglob('*') if x.is_file()):raw.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f),'role':sub.name})
 raw.append({'path':'/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r26_tied_weight_production_capacity_boundary_109_v1_20261002/checkpoints/COMMON_POST_BOOTSTRAP.pt','bytes':2626691315,'sha256':'09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55','role':'external_parent_checkpoint'})
 tsv(pack/'RAW_DATA_INDEX.tsv',raw);sums(pack);print(json.dumps({'decision':DECISION,'Gate_A':'PASS','Gate_B0':'STOP','CUDA':0},sort_keys=True))
if __name__=='__main__':main()
