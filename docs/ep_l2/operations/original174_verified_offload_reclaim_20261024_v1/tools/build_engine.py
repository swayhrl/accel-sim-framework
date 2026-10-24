from local_common import *
import ast

s=(TRACE/'tools/trace_copy.py').read_text()
original_sha=hashlib.sha256((TRACE/'tools/trace_copy.py').read_bytes()).hexdigest()
s=s[:s.index("if __name__=='__main__':")]
s=s.replace('/root/data/ep_dtc_trace_migration_20261024_v1',NATIVE)
s=s.replace('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_ep_dtc_trace_inputs_v1',NAS+'/assets')
old="need(h.hexdigest()==event['sha256'] and hash_file(partial,gate=g)==event['sha256'],'closed chunk full SHA mismatch')"
assert s.count(old)==1
s=s.replace(old,"need(h.hexdigest()==event['sha256'],'streamed chunk full SHA mismatch')")
s=s.replace("if x.is_file()};need(actual==expected", "if x.is_file() and not x.is_symlink()};need(actual==expected")
# The final immutable chunk is still closed/reopened and fully hashed. Only
# the duplicate partial-name hash before the same-inode atomic rename is gone.
needle="  if dest.exists():need(dest.stat().st_size==row['size'] and hash_file(dest,gate=g)==row['sha256'],'existing tree file collision');continue\n"
assert s.count(needle)==1
s=s.replace(needle,needle+"""  if len(ranges[row['relative_path']])==1:
   c=ranges[row['relative_path']][0];chunk=bundle/'chunks'/digest(row['relative_path'].encode())/c['name']
   try:os.link(chunk,dest)
   except OSError:pass
   else:
    need(dest.stat().st_ino==chunk.stat().st_ino and hash_file(dest,gate=g)==row['sha256'],'single-chunk immutable tree link verification');dest.chmod(0o444);continue
""")
s+='\n'+(R/'tools/copy_extensions.py').read_text()
ast.parse(s)
(R/'tools/copy_engine.py').write_bytes(s.encode())
save('QUALIFIED_ENGINE_ADAPTATION.json',dict(base_trace_commit='b93fc0dbac79d6f9c5ca027baa2d2e1cf371455b',base_trace_copy_sha256=original_sha,adapted_engine_sha256=hashlib.sha256(s.encode()).hexdigest(),changes=['Own task/true164 roots','Fresh live scientific registry and exact source/target resource admission','Frozen generic file selection and original directory metadata','One immutable single-chunk hardlink where supported, fallback to existing materialization','One final closed/reopened chunk hash instead of duplicate hashes under partial and final names','Qualified independent native restore plus all selected directories','No change to128MiB range size,15MiB/s sender rate,256MiB staging cap,V9 atomic no-replace or COMMIT-last'],new_scientific_starts=0))
print('engine_bytes',len(s))
