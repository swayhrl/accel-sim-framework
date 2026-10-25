"""Small source/metadata delta from published R13; no authority or simulation operations."""
import pathlib,json,hashlib,argparse,datetime,uuid,os
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=T/'docs-worktree';ROOT=F/'docs/dtc_l1/review_packs/DTC_AE_V100_FULL_SWEEP_20261025_V1';OLD=ROOT/'repair_validation_20261025_v1';DEST=ROOT/'repair_validation_r14_zero_start_continuation_20261026_v1';O=R/'ops';PRE=O/'r14_handoff_preimages_v1';BASE_COMMIT='7db6292af24c690553cdaaaffb3c9fe3496dca98'
def digest(body):return hashlib.sha256(body).hexdigest()
def sha(p):return digest(P(p).read_bytes())
def load(p):return json.loads(P(p).read_bytes())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def old_intact():
 m=OLD/'HANDOFF_COPY_MANIFEST.json';assert sha(m)=='2d9b6a641e970cf942489cdd16b2b3b8e1d48958f40a296cb5ff189fe7a3cb9f';r=load(m)
 for e in r['entries']:assert sha(OLD/e['pack_path'])==e['sha256'],e['pack_path']
 assert sha(OLD/'README.md')==r['README_sha256'];assert sum(1 for p in OLD.rglob('*')if p.is_file())==214
def good(p):
 r=load(p);s=str(r.get('status','')).upper();assert r.get('verified')is True or ('PASS'in s and not any(z in s for z in ['FAIL','HOLD','DRAFT'])),(str(p),s)
 return {'path':str(p),'sha256':sha(p),'status':r.get('status'),'verified':r.get('verified')}
def collect(extra):
 rows={};refs=[]
 def add(p,dest,baseline=None):
  p=P(p);dest=P(dest)
  if not p.is_file():return
  assert p.suffix in ['.py','.cc','.h','.sh','.json','.md']and p.stat().st_size<16*1024**2;assert not dest.is_absolute()and'..'not in dest.parts
  b=p.read_bytes()
  if p.suffix=='.json':json.loads(b)
  if baseline is not None and baseline.is_file()and digest(b)==sha(baseline):refs.append({'source':str(p),'published_pack_path':str(baseline.relative_to(OLD)),'sha256':digest(b),'publication_commit':BASE_COMMIT});return
  k=dest.as_posix();assert k not in rows or rows[k]['source']==str(p);rows[k]={'source':str(p),'pack_path':k,'bytes':len(b),'sha256':digest(b)}
 # Exact byte preimages are essential; no scientific payloads are in this dir.
 for p in sorted(PRE.rglob('*')):
  if p.is_file():add(p,'preimages/'+str(p.relative_to(PRE)))
 # R14 has its own source path. R13 code and the original 214-file pack remain frozen.
 revision=O/'revision14'
 if revision.exists():
  for p in sorted(revision.rglob('*')):
   if p.is_file()and p.suffix in ['.py','.cc','.h','.sh','.json','.md']:add(p,'source_tools/revision14/'+str(p.relative_to(revision)))
 for p in sorted(O.iterdir()):
  if not p.is_file():continue
  if p.suffix in ['.py','.cc','.h','.sh']and any(s in p.name.lower()for s in ['r14','revision14']):add(p,'source_tools/ops/'+p.name)
  if p.suffix=='.json'and'R14'in p.name.upper()and not p.name.startswith('R14_HANDOFF_'):add(p,'operations/'+p.name)
 for name in ['R13_PUBLICATION_READBACK_V1.json','R13_PUBLICATION_LOCAL_COMMIT_V1.json']:
  add(O/name,'prior_publication/'+name)
 for p in sorted((R/'validation/tools').iterdir()):
  if p.is_file()and p.suffix in ['.py','.cc','.h','.sh']:add(p,'source_tools/validation/'+p.name,OLD/'source_tools/validation/tools'/p.name)
 # The R14 assembler and true pre-Popen fixture live at FIX/tools.
 if (R/'tools').exists():
  for p in sorted((R/'tools').iterdir()):
   if p.is_file()and p.suffix in ['.py','.cc','.h','.sh']:add(p,'source_tools/repair_root/'+p.name)
 for ctrl in [R/'control',R/'validation/control']:
  for name in ['R14_METADATA_SUPERSESSION_AND_ALIAS_BINDING_V1.json','COMPAT_SPEC_LAYOUT_FIX_ZERO_START_V1.json','REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V1.json']:
   add(ctrl/name,'repair_metadata/root_control/'+name)
  historical=ctrl/'draft_preimages/R13_REGISTERED_ZERO_START_BEFORE_R14'
  if historical.exists():
   for p in sorted(historical.rglob('*')):
    if p.is_file()and p.suffix in ['.json','.py','.md']:add(p,'preimages/R13_REGISTERED_ZERO_START_BEFORE_R14/'+str(p.relative_to(historical)))
 for p in sorted((R/'validation/control').rglob('*.json')):
  if any(x in p.parts for x in ['draft_preimages','__pycache__','run','results','logs']):continue
  if p.name=='POOL_DISPATCH_RESERVATIONS.json'or p.name.endswith(('.DONE.json','.INTENT.json')):continue
  rel=p.relative_to(R/'validation/control');add(p,'repair_metadata/control/'+str(rel),OLD/'repair_metadata/control'/rel)
 for p in extra:
  p=P(p).resolve();assert p.is_relative_to(R)or p.is_relative_to(T);add(p,'freeze_gates/'+p.name)
 return list(rows.values()),refs
def main():
 a=argparse.ArgumentParser();a.add_argument('--phase',choices=['plan','freeze'],default='plan');a.add_argument('--qualification',action='append',default=[]);a.add_argument('--extra',action='append',default=[]);x=a.parse_args();old_intact();rows,refs=collect(x.qualification+x.extra);plan={'schema':'R14_ZERO_START_HANDOFF_DELTA_PLAN_V1','phase':x.phase,'observed_utc':now(),'destination':str(DEST),'prior_publication_commit':BASE_COMMIT,'file_count':len(rows),'total_bytes':sum(r['bytes']for r in rows),'unchanged_prior_file_references':refs,'entries':rows,'old214_files_unchanged':True,'diagnosis39_recopied':False,'authority_entry_writes':False,'scientific_starts':0,'git_commit_push':False};(O/'R14_HANDOFF_PLAN_V1.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 if x.phase=='plan':print(json.dumps({k:v for k,v in plan.items()if k not in ['entries','unchanged_prior_file_references']},ensure_ascii=False));return
 assert len(x.qualification)>=2,'Need final R14 and alias/real-pre-Popen qualification after DTC-MAIN freeze.';gates=[good(P(p))for p in x.qualification]
 cert=load(O/'R14_ZERO_MODEL_QUALIFICATION_V1.json');controller=O/'revision14/sweep_controller.py';assert cert['status']=='PASS'and cert['controller_sha256']==sha(controller)
 # Validate every source binding recognized by the final qualification schema.
 pins=cert.get('source_pins',[])
 if isinstance(pins,dict):pins=[{'path':p,'sha256':s}for p,s in pins.items()]
 for e in pins:
  path=P(e['path']);resolved=str(path.resolve())
  assert not resolved.startswith('/root/share/mnt164/'),('FUSE payload hashing is outside copyfreeze scope',str(path))
  assert sha(path)==e['sha256'],e['path']
 assert not DEST.exists()and DEST.resolve().is_relative_to(F.resolve());stage=DEST.with_name('.'+DEST.name+'.staging-'+uuid.uuid4().hex);stage.mkdir(parents=True)
 for r in rows:
  b=P(r['source']).read_bytes();assert digest(b)==r['sha256'];p=stage/r['pack_path'];p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb')as f:f.write(b)
  assert sha(p)==r['sha256']
 for r in rows:assert sha(P(r['source']))==r['sha256'],r['source']
 old_intact();readme=(O/'R14_HANDOFF_README_TEMPLATE_V1.md').read_text().replace('{{FREEZE_UTC}}',now()).replace('{{FILE_COUNT}}',str(len(rows))).replace('{{PACK_BYTES}}',str(sum(r['bytes']for r in rows)));(stage/'README.md').write_text(readme)
 manifest={'schema':'R14_ZERO_START_HANDOFF_FROZEN_MANIFEST_V1','freeze_utc':now(),'phase':'ZERO_START_ENGINEERING_CONTINUATION_NOT_SCIENTIFIC_PASS','prior_publication_commit':BASE_COMMIT,'old214_files_unchanged':True,'required_qualifications':gates,'entries':rows,'unchanged_prior_file_references':refs,'README_sha256':sha(stage/'README.md'),'new_models_started_by_pack':0,'authority_entry_writes':False,'git_commit_push':False};(stage/'HANDOFF_COPY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');os.rename(stage,DEST)
 result={'status':'R14_COPYFREEZE_PASS_NOT_COMMITTED','destination':str(DEST),'copied_files':len(rows),'total_files':len(rows)+2,'manifest_sha256':sha(DEST/'HANDOFF_COPY_MANIFEST.json'),'README_sha256':sha(DEST/'README.md'),'prior214_unchanged':True,'freeze_utc':manifest['freeze_utc']};(O/'R14_HANDOFF_COPY_RECEIPT_V1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
