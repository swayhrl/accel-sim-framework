import argparse,hashlib,json,csv,os,subprocess
from pathlib import Path
import torch
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def ts(t):return hashlib.sha256(t.contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--repo',required=True);a.add_argument('--root',required=True);x=a.parse_args();repo=Path(x.repo);root=Path(x.root)
 for n in ('raw','logs','receipts','source','tmp','cache','checkpoints'): (root/n).mkdir(parents=True,exist_ok=True)
 authority=json.loads((repo/'docs/vm_tlb/chatgpt_handoff/awma/r27r3_numeric_attribution_capacity_v1/PARENT_DATA_AUTHORITY.json').read_text());parent=repo/authority['r27r2_raw_pack'];errors=[];files=[]
 for line in (parent/'SHA256SUMS').read_text().splitlines():
  h,n=line.split('  ',1);p=parent/n;actual=sha(p);files.append({'path':str(p),'bytes':p.stat().st_size,'sha256':actual});assert actual==h,n
 prior=Path('/data/c16/awma/r27r2_varied_batch_capacity_109_v1_20261003');consumed={'parquet':Path('/data/c16/awma/r27_input_seed/train-00000-of-00001.parquet'),'bank_raw':prior/'input/token_bank/TOKEN_BANK_INT64.bin','bank_pt':prior/'input/token_bank/TOKEN_BANK.pt','common':prior/'checkpoints/COMMON_POST_BOOTSTRAP.pt'}
 expected={'parquet':authority['input']['sha256'],'bank_raw':authority['bank']['raw_sha256'],'bank_pt':authority['bank']['torch_save_sha256'],'common':authority['historical_R26_common_start']['sha256']}
 for k,p in consumed.items():
  h=sha(p);assert h==expected[k],k;files.append({'role':k,'path':str(p),'bytes':p.stat().st_size,'sha256':h})
 assert consumed['bank_raw'].stat().st_size==4325376
 assert consumed['parquet'].stat().st_size==6357543
 assert consumed['common'].stat().st_size==2626691315
 common=torch.load(consumed['common'],map_location='cpu',weights_only=False);cref=json.loads((parent/'PARENT_SEED_QUALIFICATION.json').read_text())['common'];tensorhash={n:ts(common[n]) for n in ('weight','m','v','cpu_rng','cuda_rng')}
 for n in tensorhash:assert tensorhash[n]==cref[n+'_sha256'],n
 assert common['step']==1
 bank=torch.load(consumed['bank_pt'],map_location='cpu',weights_only=False)['bank'];assert ts(bank)==expected['bank_raw']
 model=Path('/data/c16/models/.incoming/Llama-3.2-1B/4e20de362430cd3b72f300e6b0f18e50e7166e08');receipt=json.loads(Path('/data/c16/models/.provenance/R1_LLAMA3P2_1B_ASSET_RECEIPT.json').read_text())
 for f in receipt['payloads']:
  p=model/f['filename'];h=sha(p);assert h==f['sha256'] and p.stat().st_size==f['size_bytes'];files.append({'role':'model','path':str(p),'bytes':p.stat().st_size,'sha256':h})
 src=['util/vm_tlb/awma/r26_tied_weight_production_capacity/component.py','util/vm_tlb/awma/r27r2_varied_batch_capacity/component.py','util/vm_tlb/awma/r27r2_varied_batch_capacity/run_r27r2_campaign.py','util/vm_tlb/awma/r25_tied_weight_broader_validation/run_r25_campaign.py','util/vm_tlb/awma/r25_tied_weight_broader_validation/accepted_r24_base.py']
 for n in src:
  p=repo/n;h=sha(p);old=subprocess.check_output(['git','-C',str(repo),'show','ba73fa0bacf3db09f44d8ad421a0a36f56645898:'+n]);assert hashlib.sha256(old).hexdigest()==h;files.append({'role':'source','path':str(p),'bytes':p.stat().st_size,'sha256':h})
 cce=prior/'source/cce';frozen={'cce_backward.py':'e5402a590ef019692d8341805d3adf18ed95d3062c59236b364322c296b42d36','tl_utils.py':'e117b70a0fdc2ec4313fd7d9ba5a7e1d78b30fb478760c3c661f9d717cc65ea4','tl_autotune.py':'445745f6c20efcd5bcfb2fbc784361c3b4a3a0e8f2089242fde6d4362a977a20'}
 for n,h in frozen.items():p=cce/'cut_cross_entropy'/n;assert sha(p)==h;files.append({'role':'CCE','path':str(p),'sha256':h,'bytes':p.stat().st_size})
 index=list(csv.DictReader((parent/'RAW_DATA_INDEX.tsv').open(),delimiter='\t'));tensor_assets=[r for r in index if r['path'].endswith('.pt')];summary=json.loads((parent/'B1_NUMERICAL_QUALIFICATION.json').read_text())
 result={'qualified':True,'label':'R27R3_PARENT_DATA_QUALIFIED','files':files,'consumed':{k:str(p) for k,p in consumed.items()},'common_tensor_sha256':tensorhash,'common_step':1,'historical_element_tensors_available':False,'historical_tensor_index_entries':tensor_assets,'raw_evidence_fact':'B0 diagnostic tensors deleted by the R27R2 runner; checkpoint is C1 k2 and cannot recover B0 failing coordinates','historical_first_mismatch':summary['first_mismatch'],'errors':errors,'repeated_full_historical_audit':False}
 (root/'raw/PARENT_RECHECK.json').write_text(json.dumps(result,indent=2)+'\n')
 hypotheses=[{'hypothesis':'REFERENCE_VARIABILITY','discriminator':'two fresh-process unchanged B0 k0 complete steps; original tensor criterion; STOP if any required observable fails'}, {'hypothesis':'LOOKUP_REDUCTION_OR_MERGE','discriminator':'matched-dH embedding backward; scatter compact rows on CPU; compare duplicate vs unique input rows and total merge'}, {'hypothesis':'CCE_CLASSIFIER_PATH','discriminator':'matched hidden/LSE CCE dW full vs tiled, compare all rows with original criterion'}, {'hypothesis':'OPTIMIZER_OR_CHECKPOINT','discriminator':'same total gradient and same start m/v/step yields shared tile AdamW; compare moments and load/RNG identity'}, {'hypothesis':'OTHER_LOCALIZED','discriminator':'first stage mismatch and reproducible per-coordinate evidence; no inferred cause from mean/cosine'}]
 pre={'declared_before_new_GPU':True,'input':'B1 bank k0; k3 only if needed','max_pre_correction_GPU_processes':6,'processes':['repeat_b0_a','repeat_b0_b','component_attribution (bounded subprobes)','remaining processes only if unresolved discriminator needs k3 or directed fixture'],'atol':.01,'rtol':.01,'hypotheses':hypotheses,'one_correction_only':True,'no_capacity_until_A_D_pass':True}
 (root/'raw/PRE_DIAGNOSTIC_PLAN.json').write_text(json.dumps(pre,indent=2)+'\n');print(json.dumps({'Gate_A':'PASS','historical_elements':'ABSENT','consumed_file_count':len(files)}))
if __name__=='__main__':main()
