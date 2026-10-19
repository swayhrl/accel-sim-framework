from common import *
from mapping_roles import *
import copy,sys
CASES={'positive_sequence':(0,'PASS'),'missing_cache':(42,'CACHE_REGISTRATION_MISSING'),'cache_SHA':(42,'FROZEN_FILE_SHA_MISMATCH'),'cache_inode':(42,'MAP_DEVICE_INODE_MISMATCH'),'unknown_file':(42,'UNREGISTERED_FILE_MAPPING'),'wrong_role':(42,'ROLE_REQUIRES_ELF'),'ELF_as_data':(42,'ELF_MASQUERADING_AS_DATA'),'unknown_pseudo':(42,'UNKNOWN_NONFILE_MAPPING')}
def case(name):
 q=json.loads((PACK/'CPU_AUTHORITY_QUALIFICATION.json').read_text());root=Path(q['raw']);reg=json.loads((root/'PREREGISTRATION.json').read_text())['manifests'];target=str(BUILD/'ag6-cpu-authority');m=copy.deepcopy(reg[target]);events=[json.loads(l) for l in (root/'normal_fork_exec_exit/MAP_EVENTS.jsonl').read_text().splitlines()];events=[e for e in events if e.get('exe')==target and e.get('pid')==q['cases'][0]['result']['root_pid']]
 early=next(e for e in events if e.get('cache_present'));maps=root/'normal_fork_exec_exit/maps';text=(maps/early['maps']).read_text();r={e['path']:e for e in m['files']}
 if name=='positive_sequence':
  s=Sequence(m)
  for e in events:s.observe((maps/e['maps']).read_text(),target)
  s.close(True)
 elif name=='missing_cache':m['files'].remove(r[CACHE]);validate_manifest(m)
 elif name=='cache_SHA':r[CACHE]['sha256']='0'*64;validate_snapshot(text,r)
 elif name=='cache_inode':
  lines=[]
  for line in text.splitlines():
   a=line.split(None,5)
   if len(a)==6 and a[5]==CACHE:a[4]=str(int(a[4])+1)
   lines.append(' '.join(a))
  validate_snapshot('\n'.join(lines),r)
 elif name=='unknown_file':validate_snapshot(text.replace(CACHE,'/etc/UNREGISTERED_AG4'),r)
 elif name=='wrong_role':r[CACHE]['role']='ELF_SHARED_OBJECT';verify_file(r[CACHE])
 elif name=='ELF_as_data':r[target]['role']='LOADER_DATA_CACHE';verify_file(r[target])
 elif name=='unknown_pseudo':validate_snapshot(text.rstrip()+'\n1-2 r--p 0 00:00 0 [UNKNOWN_AG4]\n',r)
if __name__=='__main__':
 if len(sys.argv)>1:
  try:case(sys.argv[1]);print(json.dumps(dict(reason='PASS')))
  except Reject as e:print(json.dumps(dict(reason=str(e))));sys.exit(42)
 else:
  rows=[]
  for n,(rc,reason) in CASES.items():
   r=subprocess.run(['/usr/bin/python3','-E','-B',__file__,n],capture_output=True,text=True);d=json.loads(r.stdout) if r.stdout else dict(reason='NO_STDOUT:'+r.stderr);ok=r.returncode==rc and d['reason'].split(':')[0]==reason and not r.stderr
   rows.append(dict(case=n,expected_exit=rc,actual_exit=r.returncode,expected_reason=reason,actual_reason=d['reason'],status='PASS' if ok else 'FAIL',stderr=r.stderr))
  write(PACK/'MAPPING_ROLE_REGRESSION.json',dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'STOP',cases=rows,parser_sha256=sha(PACK/'tools/mapping_roles.py'),simulator_starts=0));assert all(r['status']=='PASS' for r in rows),rows
  print('PASS_MAPPING_ROLE_REGRESSION',len(rows))
