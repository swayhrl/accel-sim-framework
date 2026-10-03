#!/usr/bin/env python3
"""CPU-only finalizer for R27R2 pre-freeze numerical STOP."""
import argparse,csv,hashlib,json,shutil
from pathlib import Path
STAGE='AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1';DECISION='R27R2_NUMERIC_OR_STATE_NOT_QUALIFIED'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def tsv(p,rows):
 with Path(p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n',extrasaction='ignore');w.writeheader();w.writerows(rows)
def sums(pack):(pack/'SHA256SUMS').write_text('\n'.join(f'{sha(f)}  {f.relative_to(pack).as_posix()}' for f in sorted(x for x in pack.rglob('*') if x.is_file() and x.name!='SHA256SUMS'))+'\n')
def row(pol,k,n,m):return {'policy':pol,'trajectory_index':k,'observable':n,'qualified':m.get('allclose'),'finite':m.get('finite'),'shape':json.dumps(m.get('shape',[]),separators=(',',':')),'dtype':m.get('dtype',''),'max_abs':m.get('max_abs',''),'mean_abs':m.get('mean_abs',''),'max_rel':m.get('max_rel',''),'cosine_similarity':m.get('cosine_similarity','')}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--repo',required=True);ap.add_argument('--pack',required=True);a=ap.parse_args();root,repo,pack=Path(a.root),Path(a.repo),Path(a.pack);pack.mkdir(parents=True,exist_ok=True)
 gate=load(root/'raw/PARENT_SEED_QUALIFICATION.json');adm=load(root/'raw/EXACT_INPUT_ADMISSION.json');bank=load(root/'input/token_bank/BANK_AUTHORITY.json');num=load(root/'raw/B1_NUMERICAL_QUALIFICATION.json');switch=load(root/'raw/B1_CHECKPOINT_SWITCH_QUALIFICATION.json')
 if not gate['qualified'] or adm['status']!='R27R2_EXACT_INPUT_ADMITTED' or bank['status']!='R27R2_TOKEN_BANK_QUALIFIED' or num['qualified']:raise SystemExit('unexpected gate state')
 dump(pack/'PARENT_SEED_QUALIFICATION.json',gate);dump(pack/'EXACT_INPUT_ADMISSION.json',adm);dump(pack/'BANK_AUTHORITY.json',bank);dump(pack/'B1_NUMERICAL_QUALIFICATION.json',num);dump(pack/'B1_CHECKPOINT_SWITCH_QUALIFICATION.json',switch);dump(pack/'FIRST_MISMATCH.json',{'status':'MISMATCH','first_mismatch':num['first_mismatch']});dump(pack/'IMPLEMENTATION_FREEZE_STATUS.json',{'status':'NOT_CREATED','reason':'B1 required numerical contract failed','capacity_observations':0})
 rows=[]
 for p,v in num['details'].items():
  for x in v:
   for n,m in x['metrics'].items():rows.append(row(p,x['trajectory_index'],n,m))
 tsv(pack/'B1_NUMERICAL_QUALIFICATION.tsv',rows)
 status={'stage':STAGE,'decision':DECISION,'gates':{'A_PARENT_AND_EXTERNAL_SEED_ADMISSION':{'status':'PASS'},'B1_BANK_AUTHORITY':{'status':'PASS','bank_sha256':bank['bank']['sha256'],'unique_windows':bank['bank']['unique_windows']},'B1_NUMERICAL':{'status':'STOP','classification':DECISION,'first_mismatch':num['first_mismatch']},'B1_FRESH_LOAD_POLICY_SWITCH':{'status':'PASS','qualified':switch['qualified']},'IMPLEMENTATION_FREEZE':{'status':'NOT_CREATED'},'C_CAPACITY':{'status':'NOT_RUN'},'D_POSITIVE_ONLY':{'status':'NOT_RUN'},'E_DIAGNOSTIC':{'status':'NOT_RUN'}},'formal_timing':False}
 dump(pack/'GATE_STATUS.json',status);dump(pack/'FINAL_DECISION.json',{'stage':STAGE,'decision':DECISION,'scientific_interpretation':'Exact varied input and bank qualified, but mandatory B1 B0/C1/S2 total-gradient contract failed before freeze; no capacity conclusion','R26_result_changed':False})
 source=[]
 for p in sorted((repo/'util/vm_tlb/awma/r27r2_varied_batch_capacity').glob('*.py')):source.append({'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)})
 dump(pack/'SOURCE_IDENTITY.json',{'handoff_head':'578615d953b9c286cbafada997b3ed09217140a6','handoff_tree':'777ffacbcc3dfd6cdad6f77acb591f5f3a041102','sources':source,'R26_component_unchanged':True})
 locks=[]
 for p in sorted((root/'receipts').glob('GPU_LOCK*.txt')):locks.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'text':p.read_text()})
 dump(pack/'RESOURCE_LOCK_RECEIPTS.json',{'gpu_lock':'/data/c16/locks/c16_gpu_campaign.lock','receipts':locks,'all_CUDA_JIT_under_lock':True,'actual_B1_GPU_campaigns':1,'capacity_GPU_campaigns':0,'profiles':0})
 (pack/'ENGINEERING_ATTEMPTS.md').write_text("""# Engineering attempts\n\nThe preferred seed path was absent because the user-provided exact payload had been admitted under a neutral node109 input-authority path after closed R27R1. A byte-identical reflink/copy was staged at the contract path and revalidated before R27R2 node164 admission.\n\nThe first B1 invocation stopped during Python import because the new `component.py` name shadowed the frozen R26 module. It performed no CUDA/JIT. The loader was changed to import the exact R26 file under a unique module name. The retried B1 numerical run completed. Its shell pipeline did not propagate the qualification process failure through `tee`, so the already-authorized fresh-load/policy-switch subgate also ran and passed; freeze and capacity remained closed.\n""")
 (pack/'OPEN_ISSUES.md').write_text("""# Open issues\n\nThe accepted compact lookup reducer does not meet the fixed B0 total-gradient tolerance on this varied B1 stream. C1 also crosses the FP32-moment tolerance at trajectory index 4. No reducer, tolerance, tile, optimizer, input, or classifier change is authorized after treating this as the scientific B1 result.\n""")
 (pack/'FINAL_DECISION.md').write_text(f"""# Final decision\n\n`{DECISION}`\n\nThe exact parquet and immutable token bank qualified: 36,718 rows, 2,435,023 tokens, fixed first 540,672 IDs, and 4,224/4,224 distinct windows. At B1, both C1 and S2 differ from B0 in the required complete total gradient on all four bank steps. The first mismatch is C1 step 1 (`max_abs=0.09375`, `mean_abs≈1.80e-7`); C1's FP32 first moment also reaches `max_abs≈0.01464` at step 4. Fixed `rtol=atol=1e-2` was not changed. Fresh checkpoint load and C1↔S2 policy switch pass, but cannot override the B0 qualification failure. No implementation freeze, capacity search, Gate D, allocator diagnostic, or formal timing was run.\n""")
 (pack/'README.md').write_text(f"""# {STAGE}\n\nStart with `FINAL_DECISION.md`. Decision: `{DECISION}`. Exact seed/bank authority passed, but the mandatory pre-freeze varied B1 total-gradient/state comparison failed. Capacity and trajectory gates were not opened.\n""")
 report=repo/'docs/vm_tlb/codex_handoff/awma/r27r2_varied_batch_capacity_seeded_continuation_v1/LANE_G_FINAL_REPORT.md';report.parent.mkdir(parents=True,exist_ok=True);report.write_text(f"""# Lane G R27R2 final report\n\nDecision: `{DECISION}`. Exact seed and token-bank admission passed. B1 B0/C1/S2 qualification failed the frozen total-gradient tolerance on all four varied steps, with a C1 moment mismatch by step 4. Fresh-load/switch passed, but freeze/capacity/Gate-D were not run. This is a pre-freeze numerical STOP and does not alter R26's repeated-input observation.\n""")
 raw=[]
 for sub in (root/'raw',root/'receipts',root/'logs',root/'input/token_bank',root/'checkpoints'):
  for p in sorted(x for x in sub.rglob('*') if x.is_file()):raw.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'role':sub.name})
 raw.append({'path':'/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r27r2_varied_batch_capacity_109_v1_20261003/input_authority/train-00000-of-00001.parquet','bytes':6357543,'sha256':'e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7','role':'node164_input_authority'})
 tsv(pack/'RAW_DATA_INDEX.tsv',raw);sums(pack);print(json.dumps({'decision':DECISION,'seed':'PASS','bank':'PASS','B1':'FAIL','capacity':'NOT_RUN'},sort_keys=True))
if __name__=='__main__':main()
