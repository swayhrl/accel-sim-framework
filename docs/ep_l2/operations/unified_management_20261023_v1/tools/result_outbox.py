"""Bound a future owner-frozen result to the already verified finite engine.

No scanning, owner scientific signature generation, scheduling or source delete.
Preparing an offer never transfers payload; execute requires exact current owner
accepted identity/closed writer and full freeze, plus original resource/locks.
"""
import pathlib,json,hashlib,ast,base64
P=pathlib.Path;ROOT=P(__file__).resolve().parent.parent
BASE='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_unified_results'
NATIVE='/root/data/ep_l2_dtc_l1_management_20261023_v1/result_recovery'
SOURCE_PREFIX={'EP_L2':'/workspace/ep_l2_ms20261019_e_results','DTC_L1':'/workspace/dtc-ag8r1-finite-resume-174-v1/attempts'}
def require(v,why):
 if not v:raise RuntimeError(why)
def canonical(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def owner_entries(ready,offer,source):
 rows=[]
 if isinstance(ready.get('files'),list):records=ready['files']+ready['directories']+ready.get('filesystem_link_semantics',{}).get('symlinks',[])
 else:
  records=[];aux=offer['owner_auxiliary_base64']
  for desc in ready['full_file_records']+[ready['directory_records'],ready['link_records']]:
   raw=base64.b64decode(aux[desc['path']],validate=True);require(sha(raw)==desc['sha256'] and len(raw)==desc['bytes'],'owner auxiliary raw binding')
   records.extend(json.loads(line) for line in raw.splitlines()) if desc['path'].endswith('.jsonl') else records.extend(json.loads(raw)['symlinks'])
 for r in records:
  s=r.get('stat',r);name=P(r['absolute_path']).relative_to(source).as_posix() if 'absolute_path' in r else r['relative_path'];t={'regular':'file','directory':'directory','symlink':'symlink'}.get(r.get('kind',r.get('type')))
  require(t is not None,'unknown owner member type');row={k:s[k] for k in ['dev','inode','nlink','size','uid','gid','mtime_ns','ctime_ns']};row.update(path=name,type=t,mode=s.get('permissions_mode',s['mode']&0o7777),allocated=s['allocated_bytes'])
  if t=='file':row['sha256']=r['sha256']
  if t=='symlink':row['target']=r['target']
  rows.append(row)
 return sorted(rows,key=lambda r:r['path'])
def bind(offer,catalog,source_record):
 project=offer['project'];require(project in SOURCE_PREFIX,'unknown project');m=offer['manifest'];raw=base64.b64decode(offer['owner_ready_base64'],validate=True);ready=json.loads(raw)
 require(sha(raw)==m['owner_ready_sha256'],'owner frozen ready SHA');require(ready.get('status')=='COPY_READY','owner not COPY_READY');require(offer['source_disposition']=='SOURCE_KEEP' and m['source_disposition']=='SOURCE_KEEP','COPY_ONLY required')
 require(offer['owner_qualification_publication'] and len(offer['owner_qualification_publication'])==40,'published owner identity required');require(m['source_frozen_commit']==offer['owner_qualification_publication'],'publication/txid mismatch')
 source=P(m['source_root']);require(source.parent==P(SOURCE_PREFIX[project]) and source.name not in ['.','..'],'unapproved source-root namespace');require(source_record['data']['source_root']==str(source) and source_record['data']['owner_accepted_reference'] is not None and not source_record['data']['scientific_hold'],'not a currently owner-accepted result')
 require(all(r['source_root']!=str(source) for r in catalog['results'].values()),'already-qualified archived dataset must use metadata reuse, not a new upload')
 require(ready.get('complete_tree_path',ready.get('source_root'))==str(source),'owner full scope/root mismatch');require(offer['owner_membership_manifest_sha256']==sha(canonical(m['entries'])),'owner full membership binding')
 require(owner_entries(ready,offer,source)==m['entries'],'typed manifest differs from every exact raw owner file/directory/link record')
 require(m['full_owner_ready_verified'] is True and offer['all_owner_file_hashes_stat_directories_links_crosschecked'] is True,'full owner manifest join missing')
 require(offer['owner_writer_closed'] is True and offer['owner_reader_disposition'] and offer['scientific_acceptance_reference'],'owner lifecycle/reference evidence missing')
 if project=='EP_L2':
  accepted=source_record['data']['owner_accepted_reference'];byname={r['path']:r for r in m['entries']};require(byname.get('run_status.json',{}).get('sha256')==accepted.get('sha256'),'result summary differs from canonical accepted reference');require(byname.get('accel-sim.out',{}).get('sha256')==accepted.get('identity',{}).get('binary_sha256'),'binary differs from canonical science identity')
 else:require(ready['accepted_state']['scientific_strict_pass'] is True and ready['original_accepted_references_unchanged'] is True,'DTC full owner original acceptance join missing')
 require(not m['reused_objects'],'new offers have no implicit old9 pilot dependency');seen={};logical=allocation=0
 for r in m['entries']:
  name=P(r['path']);require(not name.is_absolute() and '..' not in name.parts and '\\' not in r['path'],'unsafe member')
  require(r['type'] in ['file','directory','symlink'],'unsupported special member');allocation+=r['allocated']
  require(not r['path'].lower().endswith(('.lock','.sqlite','.sqlite3','.db')),'live/controller/database-like state requires an explicit separately reviewed cold snapshot policy; never silently omit it')
  if r['type']=='file':
   require(len(r['sha256'])==64 and r['size']>=0,'missing whole file SHA/size');logical+=r['size'];key=(r['dev'],r['inode']);require(key not in seen,'internal hardlink topology needs a separately qualified adapter');seen[key]=r['path']
 slug=m['project'];require(slug==project+'_'+source.name,'project/experiment identity');require(m['genuine164_destination_root']==str(P(BASE)/slug).replace('/root/share/mnt164','/home/shared',1),'new true164 namespace required')
 require(m['selector_sha256']==sha(canonical(m['entries'])),'selector SHA');require(m['txid']==sha(canonical({k:m[k] for k in ['source_filesystem_identity','source_root','selector_sha256','source_frozen_commit','genuine164_destination_root']})),'txid encoding')
 exemplar=catalog['results']['E057'];core=P(exemplar['engine']).read_bytes();require(sha(core)==exemplar['engine_sha256'],'frozen transport core changed');text=core.decode()
 old=" oldtx,oldsha,prefix,names=PILOT_REUSE[slug];require(set(m['reused_objects'])==names,'all9 existing sidecars must be reused')\n for name,ref in m['reused_objects'].items():require(ref['path_on_target']==str(PILOT/slug/oldtx/'tree'/prefix/name) and ref['pilot_receipt_sha256']==oldsha,'unqualified existing164 reference')"
 require(text.count(old)==1,'unexpected core qualifier shape');text=text.replace(old," require(not m['reused_objects'],'new owner-frozen offer has no implicit pilot objects')")
 old=" oldtx,oldsha,oldprefix,names=PILOT_REUSE[slug];require(digest((PILOT/slug/'RECEIPT.json').read_bytes())==oldsha,'original pilot receipt changed')\n for name,ref in m['reused_objects'].items():require(file_sha(Path(ref['path_on_target']))==next(r['sha256'] for r in m['entries'] if r['path']==name),'pinned9 existing archive bytes no longer match')"
 require(text.count(old)==1,'unexpected core reuse qualifier');text=text.replace(old," require(not m['reused_objects'],'new result reuse policy')")
 binding='\n# Exact owner-qualified namespace binding; payload/locks/verification unchanged.\nROOTS='+repr({slug:str(source)})+'\nNAS=Path('+repr(BASE)+')\nNATIVE=Path('+repr(NATIVE)+')\n'
 text=text.replace("\nif __name__=='__main__':main()",binding+"\nif __name__=='__main__':main()");text=text.replace('uncompressed PAX tar excluding pinned9 referenced files','uncompressed PAX tar for every member of the exact new owner-frozen result');text=text.replace('/root/data/full_result_offload_20261023_v1/recovery_NEW_ABSENT_',NATIVE+'/recovery_NEW_ABSENT_');ast.parse(text)
 config={'manifest':m,'owner_raw_base64':offer['owner_ready_base64'],'v9_base64':base64.b64encode(P(exemplar['v9']).read_bytes()).decode(),'native_reservation_bytes':allocation+320*1024**2,'NAS_reservation_bytes':3*logical+64*1024**2,'concurrent_write_reservation_bytes':offer['current_all_project_write_reservation_bytes']}
 return config,text,{'status':'OFFER_PREPARED_EXACT_FROZEN_SCOPE','raw_bytes':logical,'Source_disposition':'SOURCE_KEEP','NAS_namespace':BASE,'native_namespace':NATIVE,'source_root':str(source),'txid':m['txid'],'payload_engine':'Pinned baseline full-result engine; only exact namespace and no-pilot-reference bindings vary','qualification':'Control binding/negative gates tested; first new offer payload requires actual current owner freeze and resource admission, no migration test repeated this round'}
