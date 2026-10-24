from audit_local import *
import time
rows=list(csv.DictReader((P/'SOURCE_COLD_CENSUS_ROOT_LEDGER.csv').open(encoding='utf-8-sig')))
eligible=[r for r in rows if r['project'] not in ['Other_tmp_scratch','Local_software_environment','Local_software_cache']]
eligible.sort(key=lambda r:-int(r['allocated_bytes'] or 0))
roots=[r['source_path'] for r in eligible]
snap=json.loads((R/'evidence/SOURCE_ENDPOINT_ACTIVITY_START.json').read_text())
for x in snap['discovery']:
 p=x['path']
 if p.startswith('/workspace/') and p not in roots:roots.append(p)
code=Path(__file__).with_name('metadata_scan.py').read_text();pending=roots;start=time.monotonic();i=0
while pending and i<12 and time.monotonic()-start<230:
 i+=1;batch=pending[:100];pending=pending[100:]
 x=remote('hrl',code+'\nprint(json.dumps(scan('+repr(batch)+',seconds=19,max_entries=170000)))',45)
 save('evidence/SOURCE_METADATA_BATCH_%02d.json'%i,x)
 retry=[r['path'] for r in x['roots'] if r['status']=='BATCH_BUDGET_NOT_SCANNED'];pending=retry+pending
 print(i,'entries',x['entries'],'seconds',round(x['seconds'],1),'pending',len(pending),flush=True)
save('evidence/METADATA_SCAN_BUDGET.json',dict(max_batches=12,max_wall_seconds=230,max_entries_per_batch=170000,per_root_seconds=12,remaining_roots=pending,large_content_reads=0,source_writes=0))
