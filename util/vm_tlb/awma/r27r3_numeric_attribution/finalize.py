"""Derive R27R3 terminal result and compact review from recorded controls."""
import argparse,csv,hashlib,json,os,subprocess,tarfile
from collections import Counter
from pathlib import Path
import torch
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def table(p,rows,fields=None):
 with Path(p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sums(pack):(pack/'SHA256SUMS').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in sorted(pack.iterdir()) if p.is_file() and p.name!='SHA256SUMS')+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--root',required=True);p.add_argument('--remote',required=True);p.add_argument('--mode',choices=['prepare','close'],required=True);p.add_argument('--verified-count',type=int);a=p.parse_args();repo,root=Path(a.repo),Path(a.root);pack=repo/'docs/vm_tlb/review_packs/AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1';pack.mkdir(parents=True,exist_ok=True)
 if a.mode=='close':
  manifest=list(csv.DictReader((root/'R27R3_PUBLICATION_MANIFEST.tsv').open(),delimiter='\t'));assert a.verified_count==len(manifest);pub={'status':'NODE164_RAW_READBACK_PASS','destination':a.remote,'manifest_items':len(manifest),'manifest_sha256':sha(root/'R27R3_PUBLICATION_MANIFEST.tsv'),'archive_sha256':sha(root/'r27r3_compact_publication.tgz'),'raw_controls':[{k:r[k] for k in ['asset','bytes','sha256']} for r in manifest if r['asset'].endswith('.pt')]};dump(pack/'NODE164_PUBLICATION.json',pub);sums(pack);print(json.dumps(pub));return
 parent=json.loads((root/'raw/PARENT_RECHECK.json').read_text());b0=json.loads((root/'raw/B0_REPEATABILITY.json').read_text());plan=json.loads((root/'raw/PRE_DIAGNOSTIC_PLAN.json').read_text());assert parent['qualified'];failed=[n for n,m in b0['metrics'].items() if not m['qualified']]
 assert not b0['qualified'] and failed
 decision={'stage':'AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1','decision':'R27R3_B0_REFERENCE_NOT_REPEATABLE','failed_gate':'B1_B0_REPEATABILITY','failed_observables':failed,'diagnostic_GPU_processes':len(b0['receipts']),'scientific_corrections':0,'capacity_trials':0,'Gate_A':'PASS','Gate_B1':'FAIL','Gate_B2':'NOT_RUN','Gate_C':'NOT_RUN','Gate_D':'NOT_RUN','Gate_E_F_G':'NOT_RUN','scope':'Two fresh unchanged native B0 k0 controls from exact common state; no candidate attribution conclusion','old_outcomes_unchanged':True};dump(root/'raw/FINAL_DECISION.json',decision)
 for name in ['PARENT_RECHECK.json','B0_REPEATABILITY.json','PRE_DIAGNOSTIC_PLAN.json','FINAL_DECISION.json']:dump(pack/name,json.loads((root/'raw'/name).read_text()))
 attribution={'outcome':'REFERENCE_VARIABILITY','support':'B0 total-gradient comparison fails the frozen elementwise criterion in the sole preregistered pair','component_root_cause':'UNDETERMINED','lookup_classifier_merge_comparison':'NOT_RUN_due_terminal_B0_repeatability_failure','cannot_infer':'The violation token rows and aggregate metrics do not localize a kernel cause','capacity_gate_open':False};dump(pack/'NUMERIC_ATTRIBUTION.json',attribution);dump(pack/'CORRECTION_DECISION.json',{'eligible':False,'reason':'B0 reference repeatability gate failed','correction_count':0});dump(pack/'IMPLEMENTATION_FREEZE_STATUS.json',{'status':'NOT_CREATED','reason':'numerical control failed'})
 coord=[];metrics=[]
 for n,m in b0['metrics'].items():
  metrics.append({'observable':n,'qualified':m['qualified'],'finite':m.get('finite','NA'),'numel':m.get('numel','NA'),'violations':m.get('violations',0),'violation_fraction':m.get('violation_fraction',0),'max_abs':m.get('max_abs',m.get('abs_diff',0)),'mean_abs':m.get('mean_abs','NA'),'cosine_secondary':m.get('cosine','NA')})
  for category,key in [('first_row_major','first32_row_major'),('largest_excess','top32_tolerance_excess')]:
   for x in m.get(key,[]):coord.append({'observable':n,'category':category,**x})
 table(pack/'B0_REPEATABILITY_METRICS.tsv',metrics);table(pack/'FAILURE_COORDINATES.tsv',coord)
 bank=torch.load(parent['consumed']['bank_pt'],map_location='cpu',weights_only=False)['bank'];inp=Counter(bank[0,0,:127].tolist());lab=Counter(bank[0,0,1:].tolist());table(pack/'TOKEN_FREQUENCIES.tsv',[{'token_id':n,'input_count':inp[n],'label_count':lab[n],'duplicate_input':inp[n]>1} for n in sorted(set(inp)|set(lab))])
 first=next(({'observable':n,'element':m['first32_row_major'][0]} for n,m in b0['metrics'].items() if m.get('violations',0)),None);dump(pack/'FIRST_MISMATCH.json',first)
 locks=[]
 for f in sorted((root/'receipts').glob('*LOCK*')):locks.append({'path':str(f),'sha256':sha(f),'content':f.read_text()})
 dump(pack/'RESOURCE_LOCK_RECEIPTS.json',{'real_lock':'flock -x 9 with descriptor opened on /data/c16/locks/c16_gpu_campaign.lock','launcher':'repeat_controls.sh','entire_child_lifetime_under_lock':True,'repeat_PIDs':[r['pid'] for r in b0['receipts']],'lock_receipts':locks,'fd_readlink_note':'The original optional readlink used $$, which is the parent shell in a subshell and did not record fd9. Real flock lifetime is established by launcher code and acquisition/release receipts; no fd owner output is fabricated.','new_CUDA_GPU_processes':len(b0['receipts']),'post_GPU_processes_empty':True,'post_lock_unowned':True})
 g=b0['metrics']['gradient'];top=g['top32_tolerance_excess'][0]
 text=f"""# Final decision\n\n`{decision['decision']}`\n\nGate A passes. The two preregistered fresh-process native B0 controls fail the unchanged gradient contract in {g['violations']} of {g['numel']} elements ({g['violation_fraction']:.12g}); every other required observable passes. The largest excess is at vocabulary row {top['row']}, column {top['column']}: reference {top['reference']}, second control {top['candidate']}, difference {top['abs_diff']}, allowed {top['allowed']}. This row occurs {top['input_frequency']} time(s) in the input. All tensors are finite. Max_abs={g['max_abs']}, mean_abs={g['mean_abs']:.12g}, cosine={g['cosine']:.12g} are secondary descriptors and do not override elementwise failure.\n\nThe baseline varies beyond the fixed contract on the sole declared pair. Kernel-level cause was not investigated after this terminal gate. Component attribution, correction, candidate requalification, freeze, capacity, 32-step/resume and allocator diagnostics were not run. Prior R26–R27R2 records stay unchanged.\n"""
 (pack/'FINAL_DECISION.md').write_text(text);(pack/'README.md').write_text('# R27R3 numerical attribution\n\nStart with `FINAL_DECISION.md`. `B0_REPEATABILITY.json` and `FAILURE_COORDINATES.tsv` contain the actual elementwise control result. Both full CPU tensor captures are durable node164 raw and independently recomputable.\n');(pack/'OPEN_ISSUES.md').write_text('# Open issues\n\nThe native B0 reference does not satisfy its frozen repeatability contract on the fixed varied k0 input. The location of the variability within forward/backbone/CCE/embedding remains undetermined because the contract requires STOP at this result.\n');(pack/'VALIDATION_SUMMARY.json').write_text(json.dumps({'Gate_A':parent['qualified'],'B0_controls_completed':len(b0['receipts']),'B0_control_qualification':b0['qualified'],'failed_observables':failed,'comparison_rule':'abs(candidate-ref)<=0.01+0.01*abs(ref)','finite_all_tensor_comparisons':all(m.get('finite',True) for m in b0['metrics'].values()),'comparison_chunk_elements':1<<18,'capacity_runs':0},indent=2)+'\n')
 source=[{'path':str(f.relative_to(repo)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted((repo/'util/vm_tlb/awma/r27r3_numeric_attribution').iterdir()) if f.is_file()];dump(pack/'SOURCE_IDENTITY.json',{'handoff_head':'29ce051f982f3854bd4392a94e4195c59340123b','handoff_tree':'2813304af8d4f4c367f3be376a05530e336ccdba','source':source});(pack/'CHANGES.md').write_text('# Changes\n\nNew isolated CPU authority audit, preregistered controls, bounded comparator with deterministic violating-coordinate tables, fail-closed flock launcher, and negative-result publication finalizer. Historical source and data are read-only. No scientific correction.\n')
 report=repo/'docs/vm_tlb/codex_handoff/awma/r27r3_numeric_attribution_capacity_v1/LANE_G_FINAL_REPORT.md';report.parent.mkdir(parents=True,exist_ok=True);report.write_text(text)
 archive=root/'r27r3_compact_publication.tgz'
 for f in (repo/'util/vm_tlb/awma/r27r3_numeric_attribution').iterdir():
  if f.is_file():(root/'source'/f.name).write_bytes(f.read_bytes())
 with tarfile.open(archive,'w:gz') as tar:
  for n in ('raw','logs','receipts','source'):
   for f in sorted((root/n).rglob('*')):
    if f.is_file() and f.suffix!='.pt':tar.add(f,arcname=f.relative_to(root))
 rows=[]
 for n in ('raw','logs','receipts','source'):
  for f in sorted((root/n).rglob('*')):
   if f.is_file():rows.append({'asset':str(f.relative_to(root)),'bytes':f.stat().st_size,'sha256':sha(f),'role':n})
 rows.append({'asset':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'role':'archive'});table(root/'R27R3_PUBLICATION_MANIFEST.tsv',rows);table(pack/'RAW_DATA_INDEX.tsv',[{**r,'node164_location':a.remote+'/'+r['asset']} for r in rows]);sums(pack);print(json.dumps({'decision':decision['decision'],'publication_items':len(rows),'archive_sha256':sha(archive),'manifest_sha256':sha(root/'R27R3_PUBLICATION_MANIFEST.tsv'),'raw_bytes':sum(r['bytes'] for r in rows if r['asset'].endswith('.pt')),'top_failure':top}))
if __name__=='__main__':main()
