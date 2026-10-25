"""CPU-only producer/parser/receiver regression; never launches a simulator."""
import pathlib,subprocess,json,socket,struct,time,os,argparse,hashlib,importlib.util,types,lzma
P=pathlib.Path
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--build-dir',required=True);ap.add_argument('--receiver-source',required=True);ap.add_argument('--runtime-policy-source',required=True);ap.add_argument('--cuda-include',required=True);a=ap.parse_args();root=P(__file__).resolve().parents[1];build=P(a.build_dir);build.mkdir(parents=True,exist_ok=True);tests=[]
 cmd=['/usr/bin/g++','-O2','-std=c++17','-pthread','-I'+a.cuda_include,'-I'+str(root.parent/'util/tracer_nvbit/tracer_tool'),str(root/'tests/ag7_cooperative_progress_fixture.cc'),str(root/'trace-parser/trace_parser.cc'),'-lzstd','-o',str(build/'fixture')];c=subprocess.run(cmd,capture_output=True,text=True);(build/'compile.log').write_text(c.stdout+c.stderr);assert c.returncode==0,c.stderr
 receiver=load('real_qualified_receiver',a.receiver_source);policy=load('real_qualified_policy',a.runtime_policy_source)
 body='#BEGIN_TB\nthread block = 0,0,0\nwarp = 0\ninsts = 1\n0 3 1 R1 LDG.E.32 0 4 1 1000 4 0\n#END_TB\n';(build/'cpu.traceg').write_text(body);(build/'cpu.traceg.xz').write_bytes(lzma.compress(body.encode()))
 def run(mode,opt=True):
  rx,tx=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM);rx.setblocking(False);tx.setblocking(False);rx.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1);began=time.monotonic_ns();env=dict(os.environ,DTC_AG7_POLICY_B_PROGRESS='1'if opt else'0',DTC_AG7_PROGRESS_FD=str(tx.fileno()),DTC_AG7_GENERATION='CPU_ONLY_REPAIR',DTC_AG7_INPUT_SHA='0'*64,DTC_AG7_ROI_SHA='1'*64);p=subprocess.Popen([str(build/'fixture'),mode,str(build)],env=env,pass_fds=(tx.fileno(),),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);tx.close();records=[];r=None;end=time.monotonic()+45
  if mode=='broken':rx.close()
  try:
   while p.poll()is None or mode!='broken':
    assert time.monotonic()<end,'CPU fixture deadline'
    if mode!='broken':
     if r is None:
      try:data,ancillary,flags,_=rx.recvmsg(1024,socket.CMSG_SPACE(struct.calcsize('3i')),socket.MSG_DONTWAIT)
      except BlockingIOError:data=None
      if data:
       first=json.loads(data);binding={k:first[k]for k in receiver.BINDING_KEYS};binding['proven_actual_root']=True;r=receiver.TelemetryReceiver(rx,binding,started_ns=began,opt_in=True);records.append(r._accept(data,ancillary,flags,time.monotonic_ns()))
     else:records.extend(r.drain(time.monotonic_ns)['records'])
    if p.poll()is not None:break
    time.sleep(.002)
   if r is not None:records.extend(r.drain(time.monotonic_ns)['records'])
   stdout,stderr=p.communicate(timeout=3);assert p.returncode==0,(mode,stdout,stderr);summary=json.loads(stdout.splitlines()[-1]);(build/(mode+('_on'if opt else'_off')+'.stdout')).write_text(stdout);(build/(mode+('_on'if opt else'_off')+'.records.json')).write_text(json.dumps(records,indent=2)+'\n');assert [x['seq']for x in records]==list(range(1,len(records)+1));return records,summary,r
  finally:
   if p.poll()is None:p.terminate();p.wait(timeout=3)
   if mode!='broken':rx.close()
 def ok(name,details):tests.append({'name':name,'PASS':True,'details':details})
 records,s,r=run('cap');assert len(records)==8196 and records[-1]['end']=='NATURAL';ok('more_than_8192_exact_authenticated_records',{'records':len(records)})
 on,ons,_=run('formats');off,offs,_=run('formats',False);assert not off and ons['checksum']==offs['checksum']==5*(0x1000+0x1004);assert [x['phase']for x in on]==['INIT','PARSE','BOUNDARY']and on[-1]['end']=='NATURAL';ok('text_xz_tracez_and_all_memory_address_decoders_off_on_identical',{'checksum':ons['checksum'],'records':len(on),'background_thread_isolated':True,'no_late_packets_after_terminal':True,'scope_restored':True})
 err,_,_=run('error');assert err[-1]['end']=='ERROR'and not any(x['end']=='NATURAL'for x in err);ok('exception_unwind_scope_and_error_terminal_no_fake_natural',{'records':len(err)})
 _,broken,_=run('broken');assert not broken['enabled'];ok('broken_socket_disables_producer_without_reconnect',broken)
 records,summary,r=run('long');assert summary['iterations']>0 and all(x['completed']==17 for x in records)and records[-1]['end']=='NATURAL';gaps=[(b['mono_ns']-a['mono_ns'])/1e9 for a,b in zip(records,records[1:])];assert max(gaps)<15 and (records[-1]['mono_ns']-records[0]['mono_ns'])/1e9>32;ok('real_33_second_parser_window_fresh_without_retirement',{'records':len(records),'max_gap_seconds':max(gaps),'all_completed':17,'decoded_iterations':summary['iterations']})
 empty,empty_sender=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM);empty.setblocking(False);empty.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
 binding=dict(r.binding,proven_actual_root=True);stale=receiver.TelemetryReceiver(empty,binding,started_ns=1,opt_in=True);stale.last=dict(records[-1]);stale.last_sequence=records[-1]['seq'];last=records[-1]['mono_ns'];stale.last_consumer_ns=last
 try:stale.drain(last+30_000_000_001);raise AssertionError('stale accepted')
 except receiver.TelemetryError as e:assert str(e)=='MISSING_OR_STALE_PRODUCER'
 try:stale.drain(last+30_000_000_002);raise AssertionError('failed receiver revived')
 except receiver.TelemetryError as e:assert str(e)=='MISSING_OR_STALE_PRODUCER'
 ok('freshness_30s_still_STOP_and_failure_latches',{'reason':stale.failed})
 empty.close();empty_sender.close()
 class Domain:
  def observe(self,*x):return dict(decision='CONTINUE',stop_reasons=[],warnings=[])
 class Runtime:
  def __init__(self,baseline,output):self.first=baseline;self.host=Domain();self.cgroup=Domain()
  def _project(self,sample):return sample
 baseline={'output_filesystem_device':1,'host_oom_kill':0};p=policy.RuntimePolicyB(baseline,build,resource_module=types.SimpleNamespace(Runtime=Runtime),started_ns=1,opt_in=True);safety={k:True for k in policy.SAFETY_KEYS}
 for second in range(10,601,10):
  now=1+second*10**9;sample=dict(baseline,monotonic_ns=now,disk_free_bytes=10*1024**3,cgroup_pressure_parsed={'io':{'full':{'avg10':0}}},pressure={'io':{'full':{'avg10':0}}});decision=p.observe(sample,0,0,progress={'mono_ns':now,'completed':17,'end':'NONE'},safety_checks=safety,io_impact={'known_scope':True,'harm_detected':False,'conservative_host_episode_profile_accepted':True});assert decision['decision']==('STOP'if second==600 else'CONTINUE')
 assert 'NO_SEMANTIC_RETIREMENT_600S'in decision['stop_reasons'];ok('same_value_fresh_packets_cannot_renew_600s_retirement_cap',decision)
 result={'status':'PASS','CPU_only':True,'scientific_models_started':0,'compiler_argv':cmd,'tests':tests,'receiver_source_sha256':hashlib.sha256(P(a.receiver_source).read_bytes()).hexdigest(),'runtime_policy_source_sha256':hashlib.sha256(P(a.runtime_policy_source).read_bytes()).hexdigest(),'production_policy_modified':False};(build/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','tests':len(tests),'result':str(build/'RESULT.json')}))
if __name__=='__main__':main()
