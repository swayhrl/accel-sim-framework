import pathlib,json,hashlib,subprocess,os,socket,time,importlib.util,ast,struct,datetime,gzip
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');R=T/'telemetry_v2';Q=R/'cpu_qualification';tests=[]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def test(name,v):assert v,name;tests.append({'test':name,'status':'PASS'})
def load(p):s=importlib.util.spec_from_file_location('isolated_cap1m_receiver_qualification',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
build=read(R/'BUILD_RESULT.json');assert build['compiled_simulator_executed'] is False and not Q.exists();Q.mkdir()
old_header=R/'framework/gpu-simulator/ag7_policyb_progress.h';header_parent=subprocess.check_output(['git','-C',str(R/'framework'),'show',build['framework_parent']+':gpu-simulator/ag7_policyb_progress.h'])
test('Framework_source_delta_is_exact_observational_record_constant_only',header_parent.replace(b'kMaximumRecords = 8192;',b'kMaximumRecords = 1048576;')==old_header.read_bytes())
oldreceiver=P(build['receiver']['original_source']);newreceiver=P(build['receiver']['new_source']);test('receiver_delta_changes_total_cap_and_preserves_original_drain8193',oldreceiver.read_text().replace('MAX_RECORDS = 8192','MAX_RECORDS = 1048576').replace('range(self.MAX_RECORDS + 1)','range(8192 + 1)')==newreceiver.read_text())
test('Core_and_original_runtime_bytes_unchanged',all(sha(P(p))==h for p,h in build['old_source_and_runtime_SHA_unchanged'].items()))
driver=Q/'producer_fixture.cc';driver.write_text('''#include "ag7_policyb_progress.h"
#include <cstdlib>
#include <unistd.h>
int main(int argc,char**argv){
 const int n=argc==2?std::atoi(argv[1]):0;
 if(n<8193||n>20000)return 41;
 dtc_ag7::ProgressProducer producer;
 if(!producer.enabled())return 42;
 for(int i=0;i<n;++i){
  const bool end=i==n-1;
  producer.observe(i==0?"INIT":end?"BOUNDARY":"SIMULATE",i,true,true,end?"NATURAL":"NONE");
  if(!producer.enabled())return 43;
  char ack=0;if(read(0,&ack,1)!=1||ack!='A')return 44;
 }
 return 0;
}
''')
binary=Q/'producer_fixture';argv=['/usr/bin/g++','-O3','-std=c++17','-I'+str(R/'framework/gpu-simulator'),str(driver),'-o',str(binary)]
with (Q/'compile.log').open('xb') as f:subprocess.run(['prlimit','--as='+str(2*1024**3),'--','taskset','-c','9',*argv],stdout=f,stderr=subprocess.STDOUT,check=True)
module=load(newreceiver);a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM);a.setblocking(False);b.setblocking(False);a.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
started=time.monotonic_ns();env=dict(os.environ,DTC_AG7_POLICY_B_PROGRESS='1',DTC_AG7_PROGRESS_FD=str(b.fileno()),DTC_AG7_GENERATION='CPU_ONLY_CAP1M_PROTOCOL_FIXTURE',DTC_AG7_INPUT_SHA='0'*64,DTC_AG7_ROI_SHA='1'*64)
count=8200;p=subprocess.Popen(['taskset','-c','9',str(binary),str(count)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,pass_fds=(b.fileno(),));b.close()
proc=P('/proc')/str(p.pid);ticks=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]);maps=(proc/'maps').read_text();test('CPU_fixture_maps_no_accelsim_or_Core_library','accel-sim.out' not in maps and 'libcudart.so' not in maps)
binding={'proven_actual_root':True,'pid':p.pid,'start_ticks':ticks,'generation':env['DTC_AG7_GENERATION'],'input':env['DTC_AG7_INPUT_SHA'],'roi':env['DTC_AG7_ROI_SHA']};receiver=module.TelemetryReceiver(a,binding,started_ns=started,opt_in=True);records=[];deadline=time.monotonic()+90
try:
 with gzip.open(Q/'AUTHENTICATED_CPU_FIXTURE_PACKETS.jsonl.gz','wt') as stream:
  while len(records)<count:
   if time.monotonic()>deadline:raise AssertionError('bounded CPU protocol fixture timeout')
   value=receiver.drain(time.monotonic_ns)
   if not value['records']:
    assert p.poll() is None,'CPU producer ended before declared packet count';time.sleep(0.0001);continue
   for record in value['records']:
    records.append(record);stream.write(json.dumps(record)+chr(10));p.stdin.write(b'A');p.stdin.flush()
 p.stdin.close();code=p.wait(timeout=5);assert code==0
finally:
 a.close()
 if p.poll() is None:p.terminate();p.wait(timeout=5)
test('actual_CPP_and_kernel_credential_receiver_cross8192_without_disabling',len(records)==8200 and records[8192]['seq']==8193 and records[-1]['seq']==8200)
test('actual_contiguous_authentication_and_counter_scope_retained',all(r['seq']==i+1 and r['pid']==p.pid and r['start_ticks']==ticks and r['generation']==binding['generation'] and r['input']==binding['input'] and r['roi']==binding['roi'] and r['completed']==i for i,r in enumerate(records)))
test('actual_CPU_protocol_terminal_is_NATURAL_but_not_scientific_acceptance',records[-1]['end']=='NATURAL' and records[-1]['phase']=='BOUNDARY' and receiver.terminal=='NATURAL' and value['scientific_acceptance'] is False)
# Declared synthetic overflow/CPU-budget fixtures;never a native simulator packet.
class FakeChannel:
 family=socket.AF_UNIX
 def getblocking(self):return False
 def getsockopt(self,level,option):return socket.SOCK_DGRAM if option==socket.SO_TYPE else 1
fake=module.TelemetryReceiver(FakeChannel(),binding,started_ns=started,opt_in=True);fake.last_sequence=1048576
record=dict(records[-1],seq=1048577,end='NONE');anc=[(socket.SOL_SOCKET,socket.SCM_CREDENTIALS,struct.pack('3i',p.pid,0,0))]
try:fake._accept(json.dumps(record).encode(),anc,0,time.monotonic_ns())
except module.TelemetryError as e:test('finite_total_cap_overflow_still_rejected',str(e)=='LOST_DUPLICATE_OR_REVERSED_SEQUENCE')
else:raise AssertionError('cap overflow accepted')
class DrainBudget(FakeChannel):
 def __init__(self):self.calls=0
 def recvmsg(self,*args):self.calls+=1;return b'x',[],0,None
channel=DrainBudget();r=module.TelemetryReceiver(channel,binding,started_ns=started,opt_in=True);r._accept=lambda *args:{}
try:r.drain(time.monotonic_ns)
except module.TelemetryError as e:test('per_drain_bound_remains_exact_original8193',str(e)=='TELEMETRY_DRAIN_BOUND_EXCEEDED' and channel.calls==8193)
else:raise AssertionError('drain not bounded')
test('new_build_and_original_sources_still_match_pins',sha(P(build['framework_binary']['path']))==build['framework_binary']['sha256'] and sha(newreceiver)==build['receiver']['new_sha256'] and all(sha(P(p))==h for p,h in build['old_source_and_runtime_SHA_unchanged'].items()))
proof={'status':'PASS_OBSERVATIONAL_CAP1M_CPU_PROTOCOL_NOT_SCIENTIFIC_MODEL','test_count':len(tests),'tests':tests,'new_framework_commit':build['framework_commit'],'framework_binary_sha256':build['framework_binary']['sha256'],'new_receiver_sha256':sha(newreceiver),'fixture_compile_argv':argv,'fixture_binary_sha256':sha(binary),'actual_CPU_process_binding':binding,'actual_authenticated_packet_count':len(records),'actual_last_seq':records[-1]['seq'],'packet_stream_sha256':sha(Q/'AUTHENTICATED_CPU_FIXTURE_PACKETS.jsonl.gz'),'real_socket_kernel_credentials':True,'synthetic_fixtures':['total_cap_overflow1048577','per_drain_CPU_budget8193'],'actual_model_starts':0,'extra_scientific_canaries':0,'old_attempt_retries':0,'Core_and_config_and_input_changed':False,'compiled_simulator_executed':False,'receiver_freshness_credentials_schema_sequence_other_source_exact':True,'next_action':'Prepare precise versioned specs/runtime/guard/strict/profile and finite continuation for original UNUSED cells. Preserve all old105spent outputs,including telemetry capSTOPs;no reruns/refunds. Native source/config/270options and full-input populations must be independently checked for each future point.','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (R/'CPU_PROTOCOL_QUALIFICATION.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
with (T/'analysis/OBSERVATIONAL_CAP1M_CPU_QUALIFICATION.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print(json.dumps(proof,indent=2))
