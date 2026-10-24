"""Private scheduling/integrity fixtures. No GPU and no new scientific PASS claim."""
import pathlib,json,hashlib,csv,subprocess,time,os,copy,signal
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');BASE=C.parent/'validator_hot_v4r3_descendant_A1';assert not BASE.exists();BASE.mkdir()
V=C/'validate_app_hot_resume_v4r3.py';SOURCE=V.read_text();B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1');R=B/'objects/ORD_Parboil_stencil_c2c817b38690_A001'
CM=json.loads((C.parent/'validator_resume_v3_qualification_A1/CACHE_FULL100.json').read_text());FIRST=next(x for x in CM['kernels']if x['name'].startswith('kernel-1-'));N=FIRST['name'];results=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,indent=2)+'\n')
def case(label,mutate=None,patch=None,extra=None,terminate=False):
 d=BASE/label;d.mkdir();root=d/'root';(root/'traces').mkdir(parents=True);(root/'EXECUTION.json').write_bytes((R/'EXECUTION.json').read_bytes())
 ctx=next((R/'traces').glob('kernelslist_ctx_*'));stats=next((R/'traces').glob('stats_ctx_*'));(root/'traces'/ctx.name).write_text(N+'\n')
 with stats.open()as f:rows=list(csv.reader(f))
 row=next(x for x in rows[1:]if x and x[0]==N)
 with(root/'traces'/stats.name).open('x',newline='')as f:csv.writer(f).writerows([rows[0],row])
 (root/'traces'/N).symlink_to(R/'traces'/N)
 manifest=d/'RAW_MANIFEST.json';entry=next(x for x in json.loads((R/'MANIFEST.json').read_text())['files']if x['path']=='traces/'+N);save(manifest,{'files':[entry]})
 cm=copy.deepcopy(CM);cm['root']=str(root);cm['source_control_files']={str(p):sha(p)for p in[root/'EXECUTION.json',R/'map/manifest.json',root/'traces'/ctx.name,root/'traces'/stats.name]};cm['kernels']=[copy.deepcopy(FIRST)]
 if mutate:mutate(cm,manifest,root)
 cache=d/'CACHE.json';save(cache,cm);code=V
 if patch:
  code=d/'guard_fixture.py';code.write_text(patch(SOURCE));assert code.read_text()!=SOURCE
 output=C/('NEG_HOT_V4R3_'+label+'.json');work=d/'work'
 cmd=['python3','-B',str(code),str(root),str(R/'map/manifest.json'),'--helper',str(C/'stencil_original_f9_validator.py'),'--parser',str(R/'contract/validate_v7.py'),'--work',str(work),'--output',str(output),'--raw-manifest',str(manifest),'--raw-manifest-sha256',sha(manifest),'--reuse-manifest',str(cache),'--reuse-manifest-sha256',sha(cache),'--max-workers','1','--deadline','20']
 if extra:cmd+=extra
 sentinel=subprocess.Popen(['sleep','45'],start_new_session=True);sentinel_ticks=pathlib.Path('/proc',str(sentinel.pid),'stat').read_text().split(') ',1)[1].split()[19]
 start=time.time()
 try:
  with(d/'controller.log').open('x')as f:p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  if terminate:
   time.sleep(1);p.send_signal(signal.SIGTERM)
  rc=p.wait(timeout=40)
  assert rc!=0 and not output.exists()and not(work/'CONTROLLER_COMPLETE.json').exists(),label
  assert sentinel.poll()is None and pathlib.Path('/proc',str(sentinel.pid),'stat').read_text().split(') ',1)[1].split()[19]==sentinel_ticks
  complete=list(work.glob('kernels/*/COMPLETE.json'))
  if label.startswith('kernel_')or label in ['missing_stdout','proof_sha_mismatch','raw_sha_mismatch','hot_too_small','free_floor','bad_portable_binding']:assert not complete
  fail=json.loads((work/'FAILURE.json').read_text())if(work/'FAILURE.json').exists()else{'error':'Rejected before work admission'}
  results.append({'label':label,'status':'GUARD_FIXTURE_REJECTED_WITHOUT_PUBLIC_PASS','returncode':rc,'seconds':time.time()-start,'complete_kernel_receipts_before_failure':len(complete),'failure':fail,'foreign_sentinel_unchanged':True,'fixture_code_sha256':sha(code),'fixture_not_scientific_producer_qualification':bool(patch),'GPU_runs':0})
 finally:
  if sentinel.poll()is None:sentinel.terminate();sentinel.wait(timeout=5)
 save(BASE/'NEGATIVES.json',{'results':results,'source_raw_unchanged':True,'real_F9_original_not_modified':True})

def childblocked(s):return s.replace('def kernel(a):',"def kernel(a):\n subprocess.Popen(['sleep','30'])\n time.sleep(30)")
case('kernel_descendant_block_deadline',patch=childblocked,extra=['--deadline','2'])
save(BASE/'QUALIFICATION.json',{'status':'OWN_THREE_PROCESS_PG_GUARD_AND_FOREIGN_SENTINEL_PASS','results':results,'source_KEEP':True})
