"""Independent per-cell terminal join; no dispatch or source-ledger API."""
import pathlib,json,re,csv,io,hashlib,importlib.util
N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2')
T=pathlib.Path('/root/data/dtc_main_20261023_v1/ae_fair_v1')
BASE=N/'DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6'
def need(x,s):
 if not x:raise ValueError(s)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(pathlib.Path(p).read_text())
def legacy():
 s=importlib.util.spec_from_file_location('unchanged_BA_pure_scientific',BASE/'ag6_strict.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def common(text,expected_options,spec,rows,m):
 names=re.findall(r'^kernel_name = (\S+)[ \t]*$',text,re.M)
 need(names==[r['kernel'] for r in rows],'whole ordered kernel population')
 need(text.count('GPGPU-Sim: *** exit detected ***')==1,'one natural exit marker')
 need(text.count('GPGPU-Sim: *** simulation thread exiting ***')==1,'one thread exit')
 need('performance model initialization complete.' in text,'model initialized')
 need(not re.search(m.FORBIDDEN,text,re.I),'forbidden failure signature')
 commands=[]
 for l in text.splitlines():
  if l.startswith('Processing kernel '):commands.append(l[len('Processing kernel '):].rsplit('/',1)[-1])
  elif l.startswith('launching memcpy command : '):commands.append(l[len('launching memcpy command : '):])
 need(commands==spec['expected_commands'],'full original commands and memcpy')
 need(re.findall(r'^Processing kernel (\S+)$',text,re.M)==[r['path'] for r in rows],'exact trace member path')
 options=m.echo(text);need(len(options)==270 and options==expected_options,'all270 effective options exact')
 block=text[text.index('kernel_name = '):];data=m.numeric(block)
 need(data['kernel_launch_uid']==1,'launch UID')
 need(data['gpu_sim_insn']==data['gpu_tot_sim_insn']==739246080,'whole active instructions')
 need(data['gpu_tot_issued_cta']==1024,'whole CTA')
 need(type(data['gpu_tot_sim_cycle']) is int and data['gpu_tot_sim_cycle']>0,'integer whole cycles')
 need('DTC_PROGRESSIVE_WAKE_V1' not in text and 'DTC_COLLECT_WB_PIPELINE_V1' not in text,'AD_AC_OFF')
 need(not re.search(r'^DTC_INVALIDATE_V1_(SNAPSHOT|SUMMARY)',text,re.M),'K1_OFF')
 return data,m.traffic(block)
def terminal(cohort):
 m=legacy();s=read(T/'control'/(cohort+'_SPEC.json'));intent=read(T/'control/qualification_ledger'/(cohort+'.INTENT.json'));done=read(T/'control/qualification_ledger'/(cohort+'.DONE.json'));out=pathlib.Path(intent['output'])
 need(done==read(out/'NATIVE_EXIT.json'),'exact DONE/native receipt join')
 need(done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'natural complete native process')
 need(sha(out/'raw.log')==done['raw_sha256'],'closed raw SHA')
 raw=(out/'raw.log').read_text();trace=(out/'actual_file_process_network.log').read_text()
 need('kernel-1.traceg' in trace and 'connect(' not in trace and '"/usr/bin/ssh"' not in trace and '"/bin/ssh"' not in trace,'actual trace open and no scientific SSH')
 launch=read(out/'NATIVE_LAUNCH.json');pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 need(launch['argv'][-len(s['native_simulator_argv']):]==s['native_simulator_argv'],'actual argv')
 need(pid['mnt_namespace']=='mnt:[4026535153]' and launch['host']['hostname']=='huangrulin-sshfs-174','native identity')
 need(s['core_commit'][:7] in raw and s['framework_commit'] in raw,'actual new source version echoes')
 for x in s['runtime_files']:need(sha(T/x['target'])==x['sha256'],'runtime still frozen')
 d=read(N/'control/DTC_ORIGINAL_INPUT_RUNTIME_IDENTITY.json')
 audit=(BASE/'identity_metadata/KERNEL_BODY_AUDIT.tsv').read_bytes();need(hashlib.sha256(audit).hexdigest()==m.AUDIT_SHA256,'input audit unchanged')
 rows=[r for r in csv.DictReader(io.StringIO(audit.decode()),delimiter='\t') if r['workload'].lower()=='gemm'];need(len(rows)==1 and rows[0]['sha256']=='fa70ba180d886dcfa313b0e6036da86c3cabadcbc6bf5b6499e0e6d74af1373d','full input identity')
 expected_options=json.loads(json.dumps(d['options']))
 for l in pathlib.Path(s['configs'][-1]['path']).read_text().splitlines():
  if l and not l.startswith('#'):
   key,*vals=l.split();expected_options[key]=vals
 final,traffic=common(raw,expected_options,d,rows,m)
 if s['cell'].startswith('D'):
  result=m.parse_full(raw,d,rows)
  m.pipeline_contract(raw,'AE' if s['cell']=='DH' else 'BASE',final)
  need(result['cycles']==final['gpu_tot_sim_cycle'],'unchanged DTC strict cycles')
 else:
  need('DTC_L1_mode = PAPER_BASE' in raw,'conventional mode')
  need(final['DTC_L1_pib_occupancy']==final['DTC_L1_lower_outstanding']==0,'conventional terminal drain')
  need(final['DTC_L1_pib_admits']==final['DTC_L1_pib_retires']>0,'conventional exactly-once PIB lifecycle')
  need(final['DTC_L1_lower_requests_acquired']==final['DTC_L1_lower_requests_released'],'conventional lower conservation')
  need(final['DTC_L1_baseline_mshr_entries']==512,'conventional finite MSHR')
 records=[json.loads(l) for l in (out/'progress.jsonl').read_text().splitlines()]
 need(records and records[-1]['end']=='NATURAL' and records[-1]['completed']==739246080,'full semantic terminal')
 need(all(r['pid']==pid['pid'] and r['start_ticks']==pid['start_ticks'] and r['generation']==done['uuid'] for r in records),'authenticated progress process/generation')
 decisions=[json.loads(l)['DTC_exact_original_policy']['decision'] for l in (out/'RESOURCE_SAMPLES.jsonl').read_text().splitlines() if 'DTC_exact_original_policy' in l]
 need(decisions and all(d['decision']!='STOP' for d in decisions),'original BA resource policy closed')
 return {'schema':'DTC_AEFAIR_COMPLETE_STRICT_TERMINAL_V1','cohort':cohort,'uuid':done['uuid'],'status':'PASS_FULL_NATIVE_STRICT_BOUNDED_MODEL','performance_accepted':True,'cycles':final['gpu_tot_sim_cycle'],'instructions':739246080,'CTA':1024,'kernel_count':1,'metrics':final,'traffic':traffic,'effective_options':expected_options,'raw_sha256':done['raw_sha256'],'core_commit':s['core_commit'],'framework_commit':s['framework_commit'],'runtime_source':str(T),'progress_records':len(records),'resource_decisions':len(decisions),'new_current_source':True,'native_values':'UNPROVEN','hardware_PPA':'UNPROVEN','SOURCE_KEEP':True}
if __name__=='__main__':
 import sys
 x=terminal(sys.argv[1]);out=pathlib.Path(read(T/'control/qualification_ledger'/(sys.argv[1]+'.INTENT.json'))['output']);p=out/'AEFAIR_STRICT.json'
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in x.items() if k not in ['metrics','traffic','effective_options']},indent=2))
