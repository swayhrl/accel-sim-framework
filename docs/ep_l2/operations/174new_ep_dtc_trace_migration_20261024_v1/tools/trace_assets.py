"""Read-only asset queries. No science routing, budget edits or transfer starts."""
import pathlib,os,json,hashlib,argparse,sys
P=pathlib.Path;ROOT=P('/root/data/ep_dtc_trace_migration_20261024_v1')
def need(x,msg):
 if not x:raise RuntimeError(msg)
def read(p):return json.loads(P(p).read_bytes())
def inspect_asset(row):
 need(row['copy_state'] in ['TRUE164_DIRECT_READ_READY','ALREADY_VERIFIED_TRUE164_DIRECT_READ_READY'],'asset is not yet verified: '+row['copy_state']);need(row['mapping_state']=='EXACT_NATIVE_COMPATIBILITY_PATH_READY','compatibility path held: '+row['mapping_state']);tree=P(row['mount_tree']);source=P(row['source_root']);need(source.is_symlink() and source.resolve()==tree.resolve(),'compatibility mapping identity changed');checks=[]
 for m in row['members']:
  p=tree/m['relative_path'];s=p.stat();need([s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]==m['verified_tree_identity'],'verified tree identity drift, bounded revalidation required')
  with p.open('rb') as f:first=f.read(min(128,s.st_size));f.seek(max(0,s.st_size-32));tail=f.read(32)
  with p.open('rb') as f:need(f.read(len(first))==first,'reopen changed')
  need(first.hex()==m['header_prefix_hex'],'header differs from frozen input');checks.append({'path':str(p),'bytes':s.st_size,'open_seek_reopen':True,'readable':True})
 entry=tree/row['entry_name'];need(hashlib.sha256(entry.read_bytes()).hexdigest()==row['commandlist_sha256'],'ordered commandlist SHA changed')
 return {'state':'AVAILABLE_FROZEN_TWO_MEMBER_INPUT_TRUE164' if row['asset_id'] in ['EP_VECTORADD_S','DTC_AD_GEMM'] else 'TRUE164_DIRECT_READ_READY','data_readiness':'TRUE164_DIRECT_READ_READY','asset_id':row['asset_id'],'aliases':row['aliases'],'projects':row['projects'],'source_root':str(source),'native_compatibility_realpath':str(source.resolve()),'target_mount_root':str(tree),'true164_tree':row['true164_tree'],'current_metadata_checks':checks,'prior_closed_full_SHA_proof':row['proof_reference'],'fresh_large_body_rehash':False,'new_payload_bytes':0,'old_originals':'SOURCE_KEEP','ordered_kernel_members':row['ordered_kernel_members'],'scientific_contexts':row['scientific_contexts'],'scientific_qualification_changed':False,'scope':'Exact frozen trace input only; COPY readiness never grants science/format/benchmark/budget acceptance'}
def main(argv=None):
 need(os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]','query only from verified174-new namespace')
 p=argparse.ArgumentParser();p.add_argument('group',choices=['asset','project']);p.add_argument('operation');p.add_argument('asset_id',nargs='?');p.add_argument('--project',choices=['EP_L2','DTC_L1']);p.add_argument('--dry-run',action='store_true');a=p.parse_args(argv);catalog=read(ROOT/'controls/ASSET_CATALOG.json');project={'EP_L2':'EP','DTC_L1':'DTC'}.get(a.project)
 if a.group=='asset' and a.operation=='ensure':
  matches=[x for x in catalog['assets'] if a.asset_id in x['aliases']];need(len(matches)==1,'unknown/unregistered asset; this readonly query never starts a second receiver');row=matches[0];need(project is None or project in row['projects'],'asset/project mismatch');return inspect_asset(row)
 if a.group=='project' and a.operation=='assets':
  out={}
  for row in catalog['assets']:
   if project and project not in row['projects']:continue
   if row['copy_state'] in ['TRUE164_DIRECT_READ_READY','ALREADY_VERIFIED_TRUE164_DIRECT_READ_READY'] and row['mapping_state']=='EXACT_NATIVE_COMPATIBILITY_PATH_READY':out[row['asset_id']]=inspect_asset(row)
   else:out[row['asset_id']]={'state':row['copy_state'],'mapping_state':row['mapping_state'],'projects':row['projects'],'source_root':row['source_root'],'scientific_qualification_changed':False,'old_originals':'SOURCE_KEEP'}
  return out
 raise RuntimeError('only read-only asset ensure/project assets are handled here')
if __name__=='__main__':
 try:print(json.dumps(main(),indent=2))
 except (RuntimeError,ValueError,OSError,KeyError) as e:print(json.dumps({'status':'HOLD_ASSET_QUERY_ONLY','reason':str(e),'new_scientific_starts':0,'new_payload_bytes':0}),file=sys.stderr);sys.exit(2)
