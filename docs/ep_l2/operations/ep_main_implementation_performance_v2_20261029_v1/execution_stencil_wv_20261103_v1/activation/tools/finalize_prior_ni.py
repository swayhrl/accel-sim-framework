"""Main passive prior-NI closeout; runs only after prior finite owner exits. No model starts."""
import pathlib,json,hashlib,os,subprocess,datetime,shutil,fcntl
P=pathlib.Path;J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');E=J/'execution_v2_20261103_v1';C=E/'control';R=E/'runtime_t'
def read(p):return json.loads(P(p).read_bytes())
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(P(p).read_bytes()).hexdigest())
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name('.'+p.name+'.main_ni_repair');tmp.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');os.replace(tmp,p);return ref(p)
def live(x):
 try:s=(P('/proc')/str(x['pid'])/'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==x['start_ticks'] and s[0] not in ['Z','X']
 except OSError:return False
def main():
 assert (C/'EXECUTOR_FINISHED.json').exists() and not live(read(C/'MAIN_BACKGROUND_LAUNCH_RECEIPT.json')),'prior Main owner still active'
 original_finish=ref(C/'EXECUTOR_FINISHED.json');results=[]
 for arm in ['A_F_MINUS_T','B_LEGACY_F','C_CORRECTED_F']:
  off='EP_PERF_T3_CONV16X8_'+arm+'_OFF_V1';on=off.replace('_OFF_','_ON_');p=C/'NI_RESULTS'/(off+'.json')
  old=read(p) if p.exists() else None
  if old and old.get('status')=='PASS_ACCEPTED_SAME_ARM_COMPACT_SEMANTICS':results.append(ref(p));continue
  if old:
   history=C/'NI_ANALYSIS_FAILURE_HISTORY'/(off+'.'+ref(p)['sha256']+'.json');history.parent.mkdir(exist_ok=True)
   if not history.exists():history.write_bytes(p.read_bytes())
  code='import sys,json;sys.path.insert(0,'+repr(str(R))+');import t3_application_ni;print(json.dumps(t3_application_ni.compare(sys.argv[1],sys.argv[2]),sort_keys=True))'
  r=subprocess.run(['/usr/bin/python3','-B','-c',code,off,on],capture_output=True,text=True,timeout=120)
  v=json.loads(r.stdout) if r.returncode==0 else dict(status='NI_ANALYSIS_HOLD',reason=(r.stderr+r.stdout)[-8000:])
  v['Main_offline_wrapper_repair']=dict(approved_by='EP-MAIN',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),change='standalone invocation imports missing json; exact comparator/criteria/Core/ELF/spec/accepteddata unchanged',original_failure_ref=ref(history) if old else None,model_starts=0)
  repaired=C/'NI_RECOMPUTED_RESULTS'/(off+'.json');put(repaired,v);put(p,v);results.append(ref(p))
 ok=all(read(r['path']).get('status')=='PASS_ACCEPTED_SAME_ARM_COMPACT_SEMANTICS' for r in results)
 status='MAIN_CONFIRMED_THREE_SAME_ARM_NI_PASS_AFTER_OFFLINE_WRAPPER_REPAIR' if ok else 'MAIN_NI_REVIEW_HOLD_NO_MODEL_RETRY'
 addendum=dict(schema='EP_MAIN_T3_NI_OFFLINE_CLOSEOUT_ADDENDUM_V1',status=status,approved_by='EP-MAIN',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_executor_finish_ref=original_finish,original_finish_retained=True,comparator_ref=ref(R/'t3_application_ni.py'),criteria_ref=ref(C/'NI_CRITERIA.json'),NI_results=results,repair_source_ref=ref(__file__),science_starts=0,Source_ELF_runtime_specs_raw_and_budget_unchanged=True,scope='accepted same-arm compact semantics only; ordered request trace and strict demand unique NEW not instrumented; numerical output UNKNOWN')
 out=C/'MAIN_NI_OFFLINE_CLOSEOUT_ADDENDUM.json';put(out,addendum)
 # Small analysis/correction evidence on genuine164, preserving original failure records.
 mount=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0];assert mount['source']=='admin-wcx@10.208.130.164:/home/shared' and mount['fstype']=='fuse.sshfs'
 nas=P('/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_execution_v2_20261103_v1/ni_offline_closeout_v1');nas.mkdir(parents=True,exist_ok=True);members=[]
 for src in [out,*[P(r['path']) for r in results],*sorted((C/'NI_ANALYSIS_FAILURE_HISTORY').glob('*.json'))]:
  rel=str(src.relative_to(C));dst=nas/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert ref(dst)['sha256']==ref(src)['sha256'],'immutable NI archive different'
  else:shutil.copy2(src,dst)
  assert ref(dst)['sha256']==ref(src)['sha256'];members.append(dict(source_ref=ref(src),archive_ref=ref(dst)))
 archive=put(nas/'COMMIT.json',dict(status='TRUE164_REOPENED_SHA_OFFLINE_ANALYSIS_REPAIR_PASS',members=members,source_keep=True))
 m=read(C/'EXACT_EXECUTION_MANIFEST.json');pub=m['publication'];repo=P(pub['repo']);rel=pub['relative_directory'];dst=repo/rel
 with (C/'MAIN_GIT_PUBLICATION.lock').open('a+b') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).strip()
  for src in [out,*[P(r['path']) for r in results],*sorted((C/'NI_ANALYSIS_FAILURE_HISTORY').glob('*.json'))]:
   d=dst/src.relative_to(C);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,d)
  subprocess.run(['git','-C',str(repo),'add','--sparse','--',rel],check=True)
  names=subprocess.check_output(['git','-C',str(repo),'diff','--cached','--name-only'],text=True).splitlines();assert all(n.startswith(rel+'/') for n in names)
  if names:subprocess.run(['git','-C',str(repo),'commit','-m','Close three accepted T NI pairs after passive JSON wrapper repair'],check=True,stdout=subprocess.DEVNULL)
  subprocess.run(['git','-C',str(repo),'push','origin',pub['branch']],check=True,capture_output=True,text=True)
  head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();remote=subprocess.check_output(['git','-C',str(repo),'ls-remote','origin','refs/heads/'+pub['branch']],text=True).split()[0];assert head==remote
 receipt=put(C/'MAIN_NI_OFFLINE_CLOSEOUT_RECEIPT.json',dict(status=status,addendum_ref=ref(out),true164_ref=archive,remote_HEAD=head,remote_verified=True,model_starts=0))
 print(json.dumps(dict(status=status,receipt_ref=receipt,model_starts=0)))
if __name__=='__main__':main()
