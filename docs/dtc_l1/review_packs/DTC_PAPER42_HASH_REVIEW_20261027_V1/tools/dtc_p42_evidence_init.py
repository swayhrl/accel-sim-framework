import pathlib,json,hashlib,zipfile,subprocess,gzip,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=P('/root/data/dtc_failure_repair_20261025_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1');A.mkdir(exist_ok=False);(A/'evidence').mkdir();(A/'analysis').mkdir();(A/'tools').mkdir()
refs={}
def read(p):
 p=P(p);b=p.read_bytes();refs[str(p)]=dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));return json.loads(b)
receipt=read(F/'analysis/paper_suite_dedup_20261027_v1/ARCHIVE_RECEIPT.json');zp=P(receipt['zip_path']);assert hashlib.sha256(zp.read_bytes()).hexdigest()==receipt['zip_sha256']
with zipfile.ZipFile(zp)as z:
 for n in ['EVIDENCE_SNAPSHOT.json','REVIEW.json','MANIFEST.json']:(A/'evidence'/('prior_'+n)).write_bytes(z.read(n))
 e=json.loads(z.read('EVIDENCE_SNAPSHOT.json'))
regpath=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');reg=read(regpath);q=reg['registered_future_requests']['DTC_AE_V100_FULL_SWEEP_20261025_V1'];current=[];changes=[];stable=[]
for p,v in e['source_sha256'].items():
 p=P(p)
 if not p.exists():changes.append(dict(path=str(p),old=v,current=None));continue
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=v:changes.append(dict(path=str(p),old=v,current=h))
 else:stable.append(str(p))
for row in e['rows']:
 if not row['original_modes']and row['intake']['program']!='cutcp':continue
 x=dict(input_digest=row['intake']['input_digest'],program=row['intake']['program'],modes={})
 for mode,m in row['original_modes'].items():
  c=m['cohort'];uuid=m['consumed']['uuid'];out=T/'DTC/run/results'/uuid;r={}
  for label,p in [('result',T/'analysis'/(c+'.RESULT.json')),('DONE',T/'control/qualification_ledger'/(c+'.DONE.json')),('spec',T/'control'/(c+'_SPEC.json')),('strict',out/'AEFAIR_STRICT.json'),('launch',out/'NATIVE_LAUNCH.json'),('pid_maps',out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'),('science_qualification',T/'analysis'/(c+'.SCIENCE_QUAL.json')),('archive',T/'control'/(c+'_ARCHIVE_RECEIPT.json'))]:
   if p.exists():r[label]=read(p)
  r['uuid']=uuid;r['cohort']=c;r['out']=str(out);r['files']=[dict(name=p.name,bytes=p.stat().st_size)for p in out.iterdir()if p.is_file()];x['modes'][mode]=r
 current.append(x)
repair=[]
for key,root in [('DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1',F/'validation'),('DTC_AE_LAVAMEM_REPAIR_20261026_V2',F/'validation_lava_memory_v2'),('DTC_AE_LATE_FAILURE_REPAIR_20261026_V1',F/'validation_late_failure_v1'),('DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1',F/'validation_remaining_failure_v1'),('DTC_AE_STORAGE_RECOVERY12_20261026_V1',F/'validation_storage_recovery12_v1')]:
 qq=reg['registered_future_requests'][key]
 for c,b in qq['consumed'].items():
  r=dict(request=key,cohort=c,uuid=b['uuid'],root=str(root),performance_eligible=False)
  for lab,p in [('result',root/'analysis'/(c+'.RESULT.json')),('DONE',root/'control/qualification_ledger'/(c+'.DONE.json')),('independent_postprocess',F/'ops/r20_archive_namespace_fix_20261027_v1/points'/b['uuid']/'POSTPROCESS.RESULT.json')]:
   if p.exists():r[lab]=read(p)
  repair.append(r)
state=dict(observed_CST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),prior_archive_receipt=receipt,stable_prior_source_files=len(stable),changed_or_missing_source_files=changes,current_original=current,current_repair=repair,authority_counts={k:dict(state=v['state'],spent=len(v['consumed']),remaining=v['remaining'])for k,v in reg['registered_future_requests'].items()if k.startswith('DTC_AE_')},source_records=refs,no_simulator_start=True,no_controller_interaction=True)
(A/'evidence/LEDGER_AUDIT.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(dict(root=str(A),stable_prior_sources=len(stable),changed=changes,original_inputs=len(current),repair_attempts=len(repair))))
PY=P('/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection');FW=P('/root/workspace/offline-sim-v1/accel-sim-framework')
def cmd(args):
 r=subprocess.run(args,capture_output=True,text=True);return dict(args=args,rc=r.returncode,stdout=r.stdout,stderr=r.stderr)
discover=[]
for args in [['git','-C',str(PY),'rev-parse','HEAD'],['git','-C',str(PY),'status','--short'],['git','-C',str(FW),'rev-parse','HEAD'],['rg','-n','polybench-atax-1of10|atax-1of10|13920|193K',str(T/'docs-worktree/docs/dtc_l1'),str(FW/'util/job_launching/apps')],['rg','--files',str(PY/'src/cuda'),'--glob','*ScalarProd*','--glob','*vectorAdd*','--glob','*atax*','--glob','*euler3d*','--glob','*hybridsort*'],['find',str(PY/'src/cuda/rodinia'),'-maxdepth','3','-type','d'],['rg','-n','scalarProd|vectorAdd|fastWalsh|gaussian|backprop|heartwall|hybridsort|kmeans|streamcluster|dwt2d|nn-rodinia|lud-rodinia|nw-rodinia|pathfinder',str(FW/'util/job_launching/apps/define-all-apps.yml')]]:discover.append(cmd(args))
(A/'evidence/SOURCE_DISCOVERY.json').write_text(json.dumps(discover,indent=2)+'\n')
for row in e['rows']:
 if row['intake']['program']=='ATAX':
  print('ATAX ALIASES',row['intake']['input_digest'],[(a.get('host'),a.get('path'),a.get('realpath'))for a in row['intake']['asset']['source_aliases']])
print('DISCOVERY SUMMARY',[(r['args'][:3],r['rc'],len(r['stdout']))for r in discover])
