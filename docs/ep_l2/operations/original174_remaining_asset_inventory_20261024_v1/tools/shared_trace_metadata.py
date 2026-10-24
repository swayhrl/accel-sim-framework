from audit_local import *
aliases=json.loads((R/'evidence/SOURCE_TRACE_ALIAS_AND_STORAGE_ENDPOINTS.json').read_text(encoding='utf8'))['symlinks']
roots=[]
for r in sorted(aliases,key=lambda r:len(r['resolved_path'])):
 p=r['resolved_path']
 if p.startswith('/root/share/accel-sim/') and p not in roots and not any(p.startswith(z+'/') for z in roots):roots.append(p)
save('evidence/OWNER_REFERENCED_SHARED_TRACE_EXACT_SCAN_ROOTS.json',roots)
code=Path(__file__).with_name('metadata_scan.py').read_text();pending=roots
for i in range(3):
 if not pending:break
 x=remote('hrl',code+'\nprint(json.dumps(scan('+repr(pending)+',seconds=17,max_entries=140000)))',35)
 save('evidence/SOURCE_SHARED_TRACE_METADATA_BATCH_%02d.json'%(i+1),x)
 pending=[r['path'] for r in x['roots'] if r['status']=='BATCH_BUDGET_NOT_SCANNED']
 print(i+1,'entries',x['entries'],'pending',len(pending),flush=True)
save('evidence/SOURCE_SHARED_TRACE_REMAINDER.json',pending)
