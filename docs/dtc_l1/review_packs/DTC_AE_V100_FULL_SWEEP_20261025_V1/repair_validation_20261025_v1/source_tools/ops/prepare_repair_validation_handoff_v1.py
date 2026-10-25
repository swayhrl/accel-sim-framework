"""Prepare a metadata/source-only handoff plan; freeze-copy only when DTC-MAIN instructs."""
import pathlib,json,hashlib,datetime,argparse,re,os,uuid
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=T/'docs-worktree';DEST=F/'docs/dtc_l1/review_packs/DTC_AE_V100_FULL_SWEEP_20261025_V1/repair_validation_20261025_v1';OPS=R/'ops'
def sha(body):return hashlib.sha256(body).hexdigest()
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def parsed(p):return json.loads(p.read_bytes())
def qualified(p):
 r=parsed(p);s=str(r.get('status','')).upper();good=r.get('verified')is True or r.get('PASS')is True or r.get('passed')is True or ('PASS'in s and not any(x in s for x in ['FAIL','HOLD','DRAFT']))
 assert good,('qualification/publication gate is not affirmative',str(p),s)
 return {'path':str(p),'sha256':sha(p.read_bytes()),'status':r.get('status'),'verified':r.get('verified')}
def collect(extra):
 found={}
 def add(p,dest):
  p=P(p);dest=P(dest);assert not dest.is_absolute()and'..'not in dest.parts
  if not p.is_file():return
  assert p.suffix.lower()in ['.json','.py','.cc','.h','.sh','.md'],('disallowed suffix',str(p))
  assert p.stat().st_size<16*1024**2,('metadata/source exceeds16MiB review boundary',str(p))
  body=p.read_bytes()
  if p.suffix=='.json':json.loads(body)
  key=dest.as_posix();assert key not in found or found[key]['source']==str(p),key
  found[key]={'source':str(p),'pack_path':key,'bytes':len(body),'sha256':sha(body)}
 # Operations and runner sources; no recursion into CPU fixture/run outputs.
 for rel in ['ops','validation/tools']:
  root=R/rel
  if root.exists():
   for p in sorted(root.iterdir()):
    if p.is_file()and p.suffix in ['.py','.cc','.h','.sh']:add(p,'source_tools/'+rel+'/'+p.name)
 # The standalone FW CPU qualification sources are also published by FW commit.
 for p in sorted((R/'framework/gpu-simulator/tests').glob('*')):
  if p.is_file()and p.suffix in ['.py','.cc']:add(p,'source_tools/framework_tests/'+p.name)
 # Final/draft scope, exact specs/caps and their manifests retain original bytes.
 for p in sorted((R/'validation/control').rglob('*.json')):
  if any(x in p.parts for x in ['__pycache__','run','results','logs']):continue
  if p.name=='POOL_DISPATCH_RESERVATIONS.json'or p.name.endswith(('.INTENT.json','.DONE.json')):continue
  add(p,'repair_metadata/control/'+str(p.relative_to(R/'validation/control')))
 for p in sorted((R/'validation/analysis').glob('*')):
  if p.is_file()and p.suffix in ['.json','.md']and any(s in p.name.upper()for s in ['AUDIT','PREPARATION','MANIFEST','QUALIFICATION']):add(p,'repair_metadata/analysis/'+p.name)
 # Only compact build/qualification/publication receipts, never their outputs.
 for name in ['FRAMEWORK_COMPILE_RESULT.json','FRAMEWORK_REPAIR_FINAL_BUILD_RESULT.json','FRAMEWORK_SOURCE_AND_CPU_RECEIPT.json']:
  add(R/name,'qualification_build/'+name)
 for name in ['CORE_BUILD_PROFILE.json','CORE_SOURCE_COMMIT.json','REPAIR_SOURCE_PUBLICATION_READBACK_V1.json']:
  add(R/'control'/name,'qualification_build/'+name)
 for p in sorted(OPS.glob('*.json')):
  if p.name.startswith('HANDOFF_PACK_'):continue
  if any(s in p.name.upper()for s in ['QUALIFICATION','FORENSIC','READBACK','PUBLICATION','SOURCE','PLAN','PROFILE','R13']):add(p,'operations/'+p.name)
 for p in sorted(OPS.glob('*FORENSIC*.md')):add(p,'operations/'+p.name)
 for p in sorted((R/'framework-cpu-tests').glob('RESULT.json')):add(p,'qualification_build/FRAMEWORK_CPU_TEST_RESULT.json')
 # Existing RAM transition is provenance, not a fourth new repair.
 for name in ['HOST_EXECUTION_PLAN_V4.json','LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json','LIVE_RAM_GUARD_CPU_QUALIFICATION_R12.json']:
  add(T/'control'/name,'existing_RAM_fix/'+name)
 for name in ['sweep_host_execution_v4.py','sweep_live_ram_override_v1.py']:
  add(T/'tools'/name,'existing_RAM_fix/'+name)
 # Original R13 qualification/source receipts may be finalized after this plan.
 for p in sorted((T/'control').glob('*R13*.json')):
  add(p,'original_R13/'+p.name)
 # Preserve the bounded failure diagnosis, not scientific raw/log payloads.
 diag=T/'analysis/failure_diagnosis_20261025_v1'
 if diag.exists():
  for p in sorted(diag.rglob('*')):
   if p.is_file()and p.suffix in ['.json','.md']and not any(x in p.parts for x in ['draft_preimages','CPU_PRODUCER_CAP_FIXTURE']):add(p,'diagnosis/'+str(p.relative_to(diag)))
 add(T/'analysis/FAILURE_DIAGNOSIS_CURRENT_INVENTORY.json','diagnosis/FAILURE_DIAGNOSIS_CURRENT_INVENTORY.json')
 for p in extra:
  p=P(p).resolve();assert p.is_relative_to(R)or p.is_relative_to(T),str(p)
  add(p,'freeze_gates/'+p.name)
 return list(found.values())
def main():
 a=argparse.ArgumentParser();a.add_argument('--phase',choices=['plan','freeze'],default='plan');a.add_argument('--qualification',action='append',default=[]);a.add_argument('--publication',action='append',default=[]);x=a.parse_args();extra=x.qualification+x.publication;rows=collect(extra);plan={'schema':'REPAIR_VALIDATION_HANDOFF_PLAN_V1','observed_utc':stamp(),'phase':x.phase,'destination':str(DEST),'file_count':len(rows),'total_bytes':sum(r['bytes']for r in rows),'source_metadata_only':True,'copies_raw_logs_binaries_build_trees_traces':False,'git_commit_or_push':False,'live_authority_mutation':False,'requires_explicit_DTC_MAIN_freeze_notification_before_copy':True,'entries':rows};planpath=OPS/'HANDOFF_PACK_PLAN_V1.json';planpath.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 if x.phase=='plan':print(json.dumps({k:v for k,v in plan.items()if k!='entries'},ensure_ascii=False));return
 assert len(x.qualification)>=2,'Provide final R13 and runner qualification receipts after DTC-MAIN freeze.'
 assert x.publication,'Provide verified source publication readback.'
 gates={'qualification':[qualified(P(p))for p in x.qualification],'publication':[qualified(P(p))for p in x.publication]}
 scope=parsed(R/'validation/control/REPAIR_SCOPE_CANDIDATE_V2.json');assert scope['finite_budget']==23 and len(scope['points'])==23 and scope['repair_points']==13 and scope['nonformal_component_sentinels']==10 and scope['counts_toward_original_40_limit']is False
 assert DEST.resolve().is_relative_to(F.resolve())and not DEST.exists(),'New pack destination must not already exist.'
 stage=DEST.with_name('.'+DEST.name+'.staging-'+uuid.uuid4().hex);stage.mkdir(parents=True)
 for row in rows:
  body=P(row['source']).read_bytes();assert sha(body)==row['sha256'],('source changed since freeze inventory',row['source']);p=stage/row['pack_path'];p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb')as f:f.write(body)
  assert sha(p.read_bytes())==row['sha256']
 for row in rows:assert sha(P(row['source']).read_bytes())==row['sha256'],('source mutated during freeze copy',row['source'])
 template=OPS/'REPAIR_HANDOFF_README_TEMPLATE_V1.md';body=template.read_text().replace('{{FREEZE_UTC}}',stamp()).replace('{{FILE_COUNT}}',str(len(rows))).replace('{{PACK_BYTES}}',str(sum(r['bytes']for r in rows)))
 (stage/'README.md').write_text(body)
 manifest={'schema':'REPAIR_VALIDATION_HANDOFF_FROZEN_MANIFEST_V1','freeze_utc':stamp(),'destination':str(DEST),'phase':'METADATA_SOURCE_HANDOFF_ONLY_NOT_ALL_SCIENCE_PASS','required_gates':gates,'expected_new_attempts':23,'repair_attempts':13,'nonformal_sentinel_attempts':10,'entries':rows,'README_sha256':sha((stage/'README.md').read_bytes()),'old_288_and_history_preserved':True,'paper_last_confirmed_master':'English v0.23','no_old_missing_receipt_reconstruction':True,'git_commit_or_push':False,'live_authority_mutation':False};(stage/'HANDOFF_COPY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');os.rename(stage,DEST)
 receipt={'status':'COPY_FREEZE_PASS_NOT_COMMITTED','destination':str(DEST),'file_count':len(rows),'manifest_sha256':sha((DEST/'HANDOFF_COPY_MANIFEST.json').read_bytes()),'README_sha256':sha((DEST/'README.md').read_bytes()),'freeze_utc':manifest['freeze_utc'],'git_commit_or_push':False,'live_authority_mutation':False};(OPS/'HANDOFF_PACK_COPY_RECEIPT_V1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
