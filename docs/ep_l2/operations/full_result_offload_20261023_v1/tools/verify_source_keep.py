import pathlib,json,subprocess,hashlib,base64
import argparse
a=argparse.ArgumentParser();a.add_argument('--output-directory',type=pathlib.Path,required=True);args=a.parse_args();assert not args.output_directory.exists(),'fresh evidence directory required';args.output_directory.mkdir(parents=True);R=pathlib.Path(__file__).resolve().parent.parent;D=R;tool=(R/'tools/full_result_bundle.py').read_text();items=[]
for slug in ['EP_L2_E057','DTC_L1_AD_GEMM']:
 m=json.loads((R/'manifests'/(slug+'.json')).read_bytes());receipt=(R/'results'/slug/'RECEIPT.json').read_bytes();refs=list(m['accepted_reference_files'])
 if slug=='DTC_L1_AD_GEMM':
  refdoc=json.loads((R/'owner_aux/DTC_L1_AD_GEMM/REFERENCE_SEMANTICS.json').read_bytes())
  for row in refdoc['original_owner_publications']:refs.append({'path':'/workspace/worktrees/accel-sim-iscas2027-dtc-ag8r1-finite-resume-174-v1/'+row['path'],'sha256':row['sha256'],'bytes':row['bytes']})
 items.append({'manifest':m,'target_receipt_sha256':hashlib.sha256(receipt).hexdigest(),'references':refs})
code='TOOL='+repr(tool)+'\nITEMS='+repr(items)+'\n'+r'''
env={'__name__':'injected'};exec(compile(TOOL,'full_result_bundle.py','exec'),env)
import os,pathlib,time,json,hashlib,fcntl,datetime
P=pathlib.Path;canon=env['canon'];ident=env['ident'];check=env['source_check'];safe=env['safe'];require=env['require'];utc=env['utc'];resources=env['source_resources'];output={}
lock=(env['BRIDGE']/'.TLS_V10_SOURCE_SENDER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
for item in ITEMS:
 m=item['manifest'];res=resources();before=check(m);rows=[];bytes_read=0;start=time.monotonic()
 for r in m['entries']:
  if r['type']!='file':continue
  p=safe(m['source_root'],r['path']);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|getattr(os,'O_NOATIME',0));h=hashlib.sha256();count=0
  with os.fdopen(fd,'rb',buffering=0) as f:
   a=ident(os.fstat(f.fileno()));require(a=={k:r[k] for k in a},'source prehash stat changed')
   for b in iter(lambda:f.read(1024**2),b''):
    h.update(b);count+=len(b);bytes_read+=len(b);delay=bytes_read/(30*1024**2)-(time.monotonic()-start)
    if delay>0:time.sleep(delay)
   require(ident(os.fstat(f.fileno()))==a==ident(p.lstat()),'source changed during postcopy hash')
  require(count==r['size'] and h.hexdigest()==r['sha256'],'postcopy full original SHA drift '+r['path']);rows.append({'path':r['path'],'sha256':h.hexdigest(),'size':count,'identity':a})
 refs=[]
 for ref in item['references']:
  p=P(ref['path']);require(p.stat().st_size==ref['bytes'] and env['file_sha'](p)==ref['sha256'],'accepted reference drift '+str(p));refs.append(ref)
 after=check(m);output[m['project']]={'schema':'LANE_T_COMPLETE_SOURCE_POSTCOPY_READONLY_RECHECK_V1','status':'PASS_FULL_SOURCE_CONTENT_IDENTITY_AND_ACCEPTED_REFERENCES_UNCHANGED_SOURCE_KEEP','utc':utc(),'checker_role':'Lane T independent storage byte check, NOT owner E2/BA signature','owner_independent_postcopy_signature':'NOT_IMPERSONATED; owner must review/bind this evidence under its published requirements','txid':m['txid'],'target_receipt_sha256':item['target_receipt_sha256'],'source_owner_full_ready_sha256':m['owner_ready_sha256'],'files':rows,'regular_files_checked':len(rows),'regular_bytes_hashed':bytes_read,'directory_and_link_records_matched_before_after':True,'before':before,'after':after,'accepted_references_checked':refs,'resources':res,'elapsed_seconds':time.monotonic()-start,'source_disposition':'SOURCE_KEEP','source_released_bytes':0,'science_starts':0,'Source_new_files':0,'Source_permissions_or_timestamps_written':False,'data_payload_transferred':0}
print(json.dumps(output))
'''
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','hrl','python3 -B -'],input=code.encode(),capture_output=True,timeout=180)
if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
out=json.loads(p.stdout)
for slug,v in out.items():
 target=args.output_directory/(slug+'_T_SOURCE_POSTCOPY_FULL_RECHECK.json');target.write_bytes((json.dumps(v,indent=2)+'\n').encode());print(json.dumps({'project':slug,'status':v['status'],'files':v['regular_files_checked'],'bytes':v['regular_bytes_hashed'],'reference_count':len(v['accepted_references_checked']),'seconds':v['elapsed_seconds'],'owner_signature':'NOT_IMPERSONATED'}),flush=True)
