import pathlib,json,socket,subprocess,time,os,importlib.util,hashlib,datetime,shutil,sys
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');sys.path.insert(0,str(T/'tools'));Q=T/'telemetry_v2/guard_cpu_qualification';Q.mkdir(exist_ok=True);assert not (Q/'RESULT.json').exists();read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('qualified_combined_cap1m_guard',T/'tools/sweep_guard_cap1m.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM);a.setblocking(False);b.setblocking(False);a.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1);started=time.monotonic_ns();env=dict(os.environ,DTC_AG7_POLICY_B_PROGRESS='1',DTC_AG7_PROGRESS_FD=str(b.fileno()),DTC_AG7_GENERATION='CPU_ONLY_COMBINED_CAP1M_WALL90_GUARD',DTC_AG7_INPUT_SHA='0'*64,DTC_AG7_ROI_SHA='1'*64)
p=subprocess.Popen(['taskset','-c','9',str(T/'telemetry_v2/cpu_qualification/producer_fixture'),'8200'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,pass_fds=(b.fileno(),));b.close();proc=P('/proc')/str(p.pid);ticks=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]);assert 'libcudart.so' not in (proc/'maps').read_text()
binding={'proven_actual_root':True,'pid':p.pid,'start_ticks':ticks,'generation':env['DTC_AG7_GENERATION'],'input':env['DTC_AG7_INPUT_SHA'],'roi':env['DTC_AG7_ROI_SHA']};guard=m.NativeDTCGuard(a,binding,Q,started);count=0;last=None;deadline=time.monotonic()+90
try:
 while count<8200:
  assert time.monotonic()<deadline;value=guard.drain()
  if not value['records']:assert p.poll() is None;time.sleep(0.0001);continue
  for row in value['records']:count+=1;last=row;p.stdin.write(b'A');p.stdin.flush()
 safety={k:True for k in m.wall.SAFETY_KEYS};impact={'known_scope':True,'harm_detected':False,'conservative_host_episode_profile_accepted':True};sample=guard.sample(Q,safety,impact,0)
 assert count==8200 and last['seq']==8200 and last['end']=='NATURAL' and sample['decision']['decision']!='STOP' and sample['decision']['profile']['wall_deadline_s']==7776000 and guard.receiver.MAX_RECORDS==1048576
 p.stdin.close();assert p.wait(timeout=5)==0
finally:
 a.close()
 if p.poll() is None:p.terminate();p.wait(timeout=5)
proof={'status':'PASS_CPU_ONLY_COMBINED_GUARD_PROTOCOL','CPU_fixture_binding':binding,'actual_authenticated_packets':count,'last_seq':last['seq'],'receiver_total_cap':guard.receiver.MAX_RECORDS,'resource_decision':sample['decision'],'actual_clock_used':True,'scientific_starts':0,'extra_scientific_canaries':0,'no_Core_or_accelsim_model_loaded':True,'all_safety_flags_are_declared_CPU_fixture_inputs_not_a_model_proof':True,'guard_source_sha256':sha(T/'tools/sweep_guard_cap1m.py'),'receiver_source_sha256':sha(T/'telemetry_v2/telemetry_receiver_cap1m.py'),'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (Q/'RESULT.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
master=T/'control/CONTINUATION_R5_ZERO_MODEL_QUALIFICATION.json';qual=read(master);pre=T/'control/draft_preimages/R5_ZERO_QUAL_BEFORE_COMBINED_GUARD.json';assert not pre.exists();shutil.copyfile(master,pre);qual['tests']+= [{'test':'actual_CPU8200packet_combined_receiver_and_policy_guard_passes_beyond_oldcap','status':'PASS'},{'test':'actual_combined_guard_reports90day_policy_and_preserves_original_decision_methods','status':'PASS'}];qual['test_count']=len(qual['tests']);qual['combined_guard_CPU_qualification_sha256']=sha(Q/'RESULT.json');qual['observed_utc']=proof['observed_utc'];tmp=master.with_suffix('.writing');tmp.write_text(json.dumps(qual,indent=2)+chr(10));os.replace(tmp,master)
print('R5_COMBINED_GUARD_REAL_CPU8200_PACKET_PASS_TOTAL_ZERO_MODEL_CHECKS',qual['test_count'],sample['decision']['decision'])
