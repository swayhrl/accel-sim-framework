"""Read-only standalone helper import/shell/dependency checks, no restore."""
from local_common import *

CODE=r'''
import pathlib,json,subprocess,time,sys,hashlib
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');sys.path.insert(0,str(T/'tools'))
import retire_174new_build_duplicates as a
rows=[json.loads(z) for z in (T/'control/LEDGER.jsonl').read_text().splitlines()];done={z['asset_id']:z for z in rows if z['status']=='ARCHIVED_CONTENT_VERIFIED'}
probe="""import sys,pathlib,importlib.util,json,hashlib
p=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(p.parent))
s=importlib.util.spec_from_file_location('restore_dependency_probe',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);v=m.v9();rr=getattr(m,'rr',None)
print(json.dumps({'module_import':'PASS','restore_native_callable':callable(m.restore_native),'pinned_v9_load':'PASS','pinned_external_v9_path':v.__file__,'resource_module':getattr(rr,'__file__',None),'resource_module_in_bundle':bool(rr and pathlib.Path(rr.__file__).parent==p.parent),'restore_entry_exists':(p.parent/'RESTORE.sh').exists(),'helper_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'resource_sha256':hashlib.sha256(pathlib.Path(rr.__file__).read_bytes()).hexdigest() if rr else None}))
"""
results=[]
for aid,row in done.items():
 m=json.loads((T/'manifests'/(aid+'.json')).read_bytes());b=P(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));p=b/'trace_copy.py'
 cp=subprocess.run(['/usr/bin/python3','-B','-c',probe,str(p)],cwd='/tmp',capture_output=True,text=True,timeout=20)
 shell=subprocess.run(['/bin/sh','-n',str(b/'RESTORE.sh')],capture_output=True,text=True,timeout=10)
 result={'asset_id':aid,'bundle':str(b),'returncode':cp.returncode,'shell_syntax_returncode':shell.returncode}
 if cp.returncode==0:result.update(json.loads(cp.stdout))
 else:result['error']=cp.stderr[-1800:]
 if shell.returncode:result['shell_error']=shell.stderr[-1000:]
 results.append(result)
x={'schema':'COMMITTED_RESTORE_IMPORT_DEPENDENCY_AUDIT_V1','unix':time.time(),'scopes':len(results),'PASS':sum(z['returncode']==0 and z['shell_syntax_returncode']==0 and z.get('restore_native_callable') and z.get('resource_module_in_bundle') for z in results),'results':results,'data_payload_reads_or_restores':0,'science_starts_or_signals':0,'scope_limit':'Shell syntax, import and pinned existing-controller dependency loading only. Does not claim native payload recovery, independent namespace portability or changed frozen-helper resource gates.'}
N=a.DEST.parent/'active_science_io_monitor_only_20261025_v1';dest=N/('RESTORE_IMPORT_DEPENDENCY_AUDIT_'+str(time.time_ns())+'.json');a.put(dest,a.blob(x));x['true164_receipt']=str(dest);print(json.dumps(x))
'''

if __name__=='__main__':
    x=remote('hrl-174-new',CODE,180)
    save('t2/RESTORE_IMPORT_DEPENDENCY_AUDIT.json',x)
    print(json.dumps({k:x[k] for k in ['scopes','PASS','data_payload_reads_or_restores','science_starts_or_signals','scope_limit']}))
