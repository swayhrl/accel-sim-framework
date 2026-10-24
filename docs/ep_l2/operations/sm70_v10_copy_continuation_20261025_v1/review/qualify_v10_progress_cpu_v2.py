"""Finite CPU-only progress metadata tests, no Source/driver/publication/science."""
from pathlib import Path
import os,sys,json,time,gzip,zlib,hashlib,subprocess,importlib.util,ast,difflib
N=Path('/root/data/closed_audit_offload_independent_review_20261025_v1');W=N/'v10_progress_cpu_qualification_A2';W.mkdir(exist_ok=False);source=Path('/root/data/shared_sm70_trace_library_20261024_v1/tools/library_copy_v10.py');spec=importlib.util.spec_from_file_location('qualified_resource_v10',source);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ticks=int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);proof={'pid':os.getpid(),'start_ticks':ticks};results=[]
def row(**kw):return dict(pid=proof['pid'],start_ticks=ticks,mono_ns=time.monotonic_ns(),phase='CPU_FIXTURE',completed=7,**kw)
def data(r):return(json.dumps(r)+'\n').encode()
def gzlive(b):
 c=zlib.compressobj(wbits=31);return c.compress(b)+c.flush(zlib.Z_SYNC_FLUSH)
def fixture(name,payload,plain=False):
 p=W/name;p.mkdir();(p/('progress.jsonl'if plain else'progress.jsonl.gz')).write_bytes(payload);return p
def positive(name,payload,plain=False,check=None):
 p=fixture(name,payload,plain);r=v._current_foreign_progress(p,proof);assert r and r['completed']==7
 if check:check(r)
 results.append({'name':name,'status':'PASS','progress_reader':r['progress_reader']})
def reject(name,payload,expected,plain=False):
 p=fixture(name,payload,plain)
 try:v._current_foreign_progress(p,proof);raise AssertionError('unexpected acceptance '+name)
 except RuntimeError as e:assert expected in str(e),(name,str(e));results.append({'name':name,'status':'PASS_REJECTED','reason':str(e)})
positive('fresh_partial_gzip',gzlive(data(row())),check=lambda r: r['progress_reader']['live_unfinalized_gzip_CRC_not_claimed']or(_ for _ in()).throw(AssertionError('partial falsely finalized')))
positive('closed_gzip',gzip.compress(data(row())),check=lambda r: r['progress_reader']['gzip_last_member_eof']is True or(_ for _ in()).throw(AssertionError('closed not EOF')))
positive('concatenated_closed',gzip.compress(data(row()))+gzip.compress(data(row())),check=lambda r:r['progress_reader']['gzip_completed_members']==2 or(_ for _ in()).throw(AssertionError('concat frames')))
positive('concat_closed_plus_live',gzip.compress(data(row()))+gzlive(data(row())))
positive('plain_with_identity',data(row()),plain=True)
legacy=row();del legacy['pid'];del legacy['start_ticks'];positive('legacy_plain_without_PID_fields',data(legacy),plain=True)
positive('plain_complete_JSON_no_newline',json.dumps(row()).encode(),plain=True)
reject('truncated_no_complete_gzip_record',gzip.compress(data(row()))[:10],'UNREADABLE')
reject('closed_truncated_JSON',gzip.compress(b'{"pid":'),'TRUNCATED_JSON')
corrupt=bytearray(gzip.compress(data(row())));corrupt[-8]^=1;reject('closed_bad_CRC',bytes(corrupt),'BAD_GZIP')
reject('closed_plus_bad_partial_header',gzip.compress(data(row()))+b'X','BAD_GZIP_HEADER')
r=row();r['mono_ns']-=31_000_000_000;reject('stale',gzlive(data(r)),'FRESHNESS')
r=row();r['pid']+=1;reject('wrongPID',gzlive(data(r)),'PID_TICKS')
r=row();r['start_ticks']+=1;reject('wrong_ticks',gzlive(data(r)),'PID_TICKS')
r=row();r['pid']+=1;reject('plain_identity_wrongPID',data(r),'PID_TICKS',plain=True)
r=row();del r['pid'];del r['start_ticks'];reject('gzip_missing_record_identity',gzlive(data(r)),'PID_TICKS')
p=fixture('compressed16M_limit',b'')
with (p/'progress.jsonl.gz').open('r+b')as f:f.truncate(16*v.MIB+1)
try:v._current_foreign_progress(p,proof);raise AssertionError('16M accepted')
except RuntimeError as e:assert 'COMPRESSED16M_LIMIT'in str(e);results.append({'name':'compressed16M_limit','status':'PASS_REJECTED','reason':str(e)})
# Generate >64MiB decoded JSONL using a small streaming compressor; no64MiB fixture allocation.
p=fixture('decoded64M_limit',b'');c=zlib.compressobj(wbits=31);large=row();large['padding']='x'*(64*1024);line=data(large)
with (p/'progress.jsonl.gz').open('wb')as f:
 for i in range((64*v.MIB)//len(line)+1):f.write(c.compress(line))
 f.write(c.flush())
try:v._current_foreign_progress(p,proof);raise AssertionError('64M accepted')
except RuntimeError as e:assert 'DECODED64M_LIMIT'in str(e);results.append({'name':'decoded64M_limit','status':'PASS_REJECTED','reason':str(e)})
# A currently zombie process is not active, so an absent metadata file is not a HOLD.
child=subprocess.Popen(['/usr/bin/python3','-c','pass']);event=os.waitid(os.P_PID,child.pid,os.WEXITED|os.WNOWAIT);zt=int(Path('/proc',str(child.pid),'stat').read_text().rsplit(')',1)[1].split()[19]);assert v._current_foreign_progress(W/'missing_zombie',{'pid':child.pid,'start_ticks':zt})is None;child.wait();results.append({'name':'real_Z_not_active','status':'PASS'})
# Explicit concurrent-exit boundary: pre live, then metadata missing, post gone. No real foreign process modified.
original=v._progress_process_identity;counter=[0]
def ending(p):
 counter[0]+=1;return proof if counter[0]==1 else None
v._progress_process_identity=ending
try:assert v._current_foreign_progress(W/'missing_after_exit',proof)is None
finally:v._progress_process_identity=original
results.append({'name':'concurrent_exit_during_missing_progress_not_hold','status':'PASS_SYNTHETIC_IDENTITY_BOUNDARY'})
try:v._current_foreign_progress(W/'missing_still_alive',proof);raise AssertionError('alive missing accepted')
except RuntimeError as e:assert 'RESOURCE_HOLD_ACTIVE_PROGRESS_UNREADABLE'in str(e);results.append({'name':'alive_missing_progress_hold','status':'PASS_REJECTED','reason':str(e)})
# Exact-byte derivation check: all original non-Resource functions/quotas and main dispatch unchanged.
v8=Path('/root/data/shared_sm70_trace_library_20261024_v1/tools/library_copy_v8.py').read_text();v10=source.read_text()
def defs(s):return{n.name:ast.get_source_segment(s,n)for n in ast.parse(s).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
a,b=defs(v8),defs(v10);assert all(a[k]==b[k]for k in a if k!='Resources');old=a['Resources'];new=b['Resources'];assert old[:old.index('   i=read(f);')]==new[:new.index('   try:i=read(f)')];assert old[old.index('  # This COPY_ONLY task'):]==new[new.index('  # This COPY_ONLY task'):];assert v8[v8.index("if __name__=='__main__':"):]==v10[v10.index("if __name__=='__main__':"):];results.append({'name':'all_Source_protocol_partial_manifest_and_quotas_byte_identical','status':'PASS'})
assert "except FileNotFoundError as e:raise RuntimeError('RESOURCE_HOLD_FOREIGN_INTENT_UNREADABLE: '+str(f))from e"in v10;results.append({'name':'missing_enumerated_or_registered_intent_fail_closed','status':'PASS_EXACT_SOURCE_ASSERTION'})
report={'status':'PASS_BOUNDED_PROGRESS_CPU_ENGINEERING_ONLY','engine_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':len(results),'results':results,'limits':{'compressed_bytes':16*v.MIB,'decoded_bytes':64*v.MIB,'tail_records':32,'single_record_bytes':256*1024},'partial_frame_integrity_boundary':'A live gzip prefix is qualified only for complete fresh JSON+exact live proof before/after. Missing future trailer/CRC cannot be distinguished from intentional live incompleteness. No final CRC claim for partial last member.','Source_or_driver_or_foreign_writes':0,'Source_trace_bytes_read':0,'production_main_or_locks_used':False,'GPU_SIM_109':False,'observed_unix':time.time()};out=W/'QUALIFICATION.json';out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps({'path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'engine_sha256':report['engine_sha256'],'cases':len(results)}))
