#!/usr/bin/python3
"""All-project immutable metadata discovery; does not read trace bodies or run applications."""
import pathlib,json,hashlib,os,sys,argparse,resource,types,stat
sys.dont_write_bytecode=True
ROOT=pathlib.Path('/root/share/mnt164/huangrulin/traces')
def need(x,m):
 if not x:raise RuntimeError('DISCOVERY_REFUSED: '+m)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p,cap):
 need(not p.is_symlink(),'symlink metadata')
 with p.open('rb')as f:
  s=os.fstat(f.fileno());need(stat.S_ISREG(s.st_mode)and 0<s.st_size<=cap,'metadata bounds')
  b=f.read(cap+1);e=os.fstat(f.fileno())
 need(len(b)==s.st_size and(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(e.st_dev,e.st_ino,e.st_size,e.st_mtime_ns),'metadata changed')
 return b
def main():
 resource.setrlimit(resource.RLIMIT_AS,(512*2**20,512*2**20));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 os.nice(max(0,15-os.getpriority(os.PRIO_PROCESS,0)))
 allowed=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,set(allowed[:2]))
 a=argparse.ArgumentParser(description='Read-only asset metadata. Historical access is not Native restore qualification.')
 a.add_argument('--architecture',choices=['SM70','SM89']);a.add_argument('--program');a.add_argument('--id');args=a.parse_args()
 here=pathlib.Path(__file__).resolve().parent
 manifest=json.loads(read(here/'CODE_MANIFEST.json',65536))
 need(set(manifest['files'])=={'trace_assets_list.py','trace_discovery_v1.py'},'exact code members')
 canonical=(json.dumps(manifest['files'],sort_keys=True,separators=(',',':'))+'\n').encode()
 need(here.name==manifest['code_version_id']==sha(canonical),'version directory code ID')
 need(manifest['metadata_only']is True and manifest['allowed_operations']==['COUNTS','LIST','SHOW'],'metadata scope')
 verified={}
 for rel,pin in manifest['files'].items():
  need(rel in ['trace_assets_list.py','trace_discovery_v1.py'],'fixed package filenames')
  raw=read(here/rel,128*1024);need(len(raw)==pin['bytes']and sha(raw)==pin['sha256'],'immutable code SHA');verified[rel]=raw
 pointer_path=ROOT/'catalog/CURRENT_UNIFIED_DISCOVERY.json';rawpointer=read(pointer_path,65536);pointer=json.loads(rawpointer)
 need(pointer['schema']=='PUBLIC_METADATA_DISCOVERY_POINTER_V1'and pointer['metadata_only']is True and pointer['tool_code_version_id']==manifest['code_version_id'],'public pointer scope')
 rel=pathlib.PurePosixPath(pointer['relative_path'])
 need(str(rel)==pointer['relative_path']and not rel.is_absolute()and len(rel.parts)==2 and rel.parts[0]=='versions'and rel.parts[1]=='unified_'+pointer['sha256']+'.json','exact index CAS path')
 raw=read(ROOT/'catalog'/str(rel),16*2**20);need(sha(raw)==pointer['sha256']and len(raw)==pointer['bytes'],'index raw SHA/bytes')
 m=types.ModuleType('immutable_discovery');m.__file__=str(here/'trace_discovery_v1.py');exec(compile(verified['trace_discovery_v1.py'],m.__file__,'exec'),m.__dict__)
 v=m.parse(raw);m.validate_index(v)
 current={};cas_current={}
 for key in ['SM89_ordinary','SM89_derived','SM89_qualification_overlay','SM70_current_NAS_access']:
  if key not in v['source_refs']:continue
  ref=v['source_refs'][key]['pointer'];p=pathlib.Path(ref['path'])
  allowed=ROOT/'catalog'if key=='SM70_current_NAS_access'else ROOT/'rtx4080_sm89/bulk_20261024_v1/catalog'
  need(p.is_relative_to(allowed),'source pointer scope')
  try:
   rawptr=read(p,1024*1024);current[key]=sha(rawptr)==ref['sha256']
   live=json.loads(rawptr);target=v['source_refs'][key]['target']
   rel=pathlib.PurePosixPath(live['relative_path'])
   safe=not rel.is_absolute()and str(rel)==live['relative_path']and '..'not in rel.parts
   cas_current[key]=safe and live['sha256']==target['sha256']and p.parent/str(rel)==pathlib.Path(target['path'])and sha(read(pathlib.Path(target['path']),32*2**20))==target['sha256']
  except (OSError,RuntimeError,ValueError,KeyError,TypeError):current[key]=False;cas_current[key]=False
 try:
  q=v['source_refs']['historical_queue'];current['historical_queue_snapshot_still_matches']=sha(read(pathlib.Path(q['path']),32*2**20))==q['sha256']
 except (OSError,RuntimeError):current['historical_queue_snapshot_still_matches']=False
 rows=None
 if args.architecture or args.program or args.id:
  rows=(v['SM70_exact_inputs']if args.architecture=='SM70'else v['SM89_committed_trace_assets']if args.architecture=='SM89'else v['SM70_exact_inputs']+v['SM89_committed_trace_assets'])
  if args.program:rows=[x for x in rows if x.get('program')==args.program]
  if args.id:rows=[x for x in rows if x.get('id',x.get('asset_id'))==args.id]
 result=dict(schema='PUBLIC_METADATA_DISCOVERY_QUERY_V1',scope='READ_ONLY_METADATA_NO_TRACE_BODY_RESTORE_OR_SIMULATOR_ADMISSION',snapshot_sha256=pointer['sha256'],snapshot_published_unix=pointer['published_unix'],current_source_pointer_matches=current,current_source_cas_content_matches=cas_current,CAS_match_basis='metadata CAS target path plus actual small table SHA; pointer timestamp changes reported separately',counts=v['counts'],historical_SM70_access_unix=v['SM70_exact_inputs'][0]['access_snapshot_unix'],SM70_access_is_historical_not_current_Native_readback=True,counts_are_different_units=True,consumer_scientific_or_budget_qualification_granted=False)
 if 'SM70_current_NAS_access_acceptance'in v:result['current_SM70_NAS_access_evidence']=v['SM70_current_NAS_access_acceptance']
 if rows is not None:result['records']=rows
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
