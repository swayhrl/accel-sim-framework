import hashlib,importlib.util,json,os,stat,tarfile,uuid
from pathlib import Path
import sys
A=Path(__file__).resolve().parent;R=A/'runtime';sys.path.insert(0,str(R));import ep_perf_archive as archive
T=A/'archive_CPU'/str(uuid.uuid4());T.mkdir(parents=True);src=T/'tiny_fixture';src.mkdir();(src/'ONLY_CPU_FIXTURE.txt').write_text('TEST_ONLY no application or scientific result\n')
members=archive.inventory(src);tar=T/'fixture.tar'
with tarfile.open(tar,'w')as z:
 for row in members:
  p=src/row['member'];info=tarfile.TarInfo(row['member']);info.size=row['bytes'];info.mode=row['mode'];info.uid=row['uid'];info.gid=row['gid'];info.mtime=row['mtime_ns']//1000000000
  with p.open('rb')as f:z.addfile(info,f)
manifest=dict(archive_sha256=archive.sha(tar),members=members);mp=T/'manifest.json';mp.write_text(json.dumps(manifest));total=sum(r['bytes']for r in members);rows=[]
def check(label,fn,reject=False):
 try:out=fn();ok=not reject;error=None
 except Exception as e:out=None;ok=reject;error=str(e)
 rows.append(dict(label=label,PASS=ok,error=error,result=out));assert ok
check('first_independent_native_restore_SHA_metadata',lambda:archive.restore(tar,mp,T/'fresh_A',total))
check('second_independent_native_restore_SHA_metadata',lambda:archive.restore(tar,mp,T/'fresh_B',total))
check('existing_target_rejected',lambda:archive.restore(tar,mp,T/'fresh_A',total),True)
check('byte_bound_rejected',lambda:archive.restore(tar,mp,T/'fresh_C',0),True)
bad=dict(manifest,archive_sha256='0'*64);bp=T/'bad_manifest.json';bp.write_text(json.dumps(bad));check('wrong_archive_SHA_rejected',lambda:archive.restore(tar,bp,T/'fresh_D',total),True)
for name in ['/tmp/outside','../outside','x/../../outside']:
 check('unsafe_member_'+name,lambda name=name:archive.safe_member(name),True)
x=dict(schema='EP_PF_RELOCATED_ARCHIVE_NATIVE_RESTORE_CPU_CONTROLS_V1',status='PASS_TINY_ENGINEERING_FIXTURE_NOT_FORMAL_RESULT_ARCHIVE',controls=rows,total=len(rows),passed=sum(r['PASS']for r in rows),archive_module_ref=dict(path=str(R/'ep_perf_archive.py'),sha256=archive.sha(R/'ep_perf_archive.py')),model_starts=0,real_ledger_writes=0,large_assets=0)
(A/'ARCHIVE_CPU_CONTROLS.json').write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');print('PASS',len(rows))
