import pathlib,subprocess,json,time,hashlib,importlib.util,sys,os,signal
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');V=C/'validate_app_hot_resume_v4r3.py';Q=C.parent/'validator_hot_v4r3_rate_A1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if len(sys.argv)>1:
 Q=pathlib.Path(sys.argv[1]);index=sys.argv[2];source=pathlib.Path(sys.argv[3]);dest=Q/(index+'.xz');start=time.time()
 spec=importlib.util.spec_from_file_location('v',V);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 with(Q/'TOTAL_READ.lock').open('a')as f:h=m.digest(source,f,dest,source.stat().st_size)
 assert sha(dest)==h;end=time.time();(Q/(index+'.json')).write_text(json.dumps({'bytes':dest.stat().st_size,'sha256':h,'start':start,'end':end,'pid':os.getpid()}));sys.exit(0)
assert not Q.exists();Q.mkdir();source=next(pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/objects/ORD_Parboil_stencil_c2c817b38690_A001/traces').glob('*.trace.xz'))
assert source.stat().st_size*16<4*2**30;ps=[]
try:
 for i in range(16):ps.append(subprocess.Popen(['python3','-B',str(pathlib.Path(__file__)),str(Q),str(i),str(source)],start_new_session=True))
 deadline=time.time()+60
 while any(p.poll()is None for p in ps):
  assert time.time()<deadline;time.sleep(.1)
 assert all(p.returncode==0 for p in ps)
 rows=[json.loads((Q/(str(i)+'.json')).read_text())for i in range(16)];total=sum(x['bytes']for x in rows);elapsed=max(x['end']for x in rows)-min(x['start']for x in rows)
 assert total/elapsed<=15*2**20 and len({x['sha256']for x in rows})==1
 out={'status':'REAL16_PROCESS_SHARED_LOCK_AGGREGATE_NAS_READ_15MIB_PER_SECOND_BOUND_PASS','validator_sha256':sha(V),'source':str(source),'source_sha256':rows[0]['sha256'],'total_bytes':total,'elapsed_seconds':elapsed,'aggregate_MiB_per_second':total/elapsed/2**20,'rows':rows,'GPU_runs':0,'source_KEEP':True}
 (Q/'QUALIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
 for i in range(16):(Q/(str(i)+'.xz')).unlink()
 (Q/'HOT_TEMP_CLEANUP.json').write_text(json.dumps({'released_temporary_verified_bytes':total,'source_KEEP':True})+'\n')
finally:
 for p in ps:
  if p.poll()is None:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
print(json.dumps(out))
