"""Whole-input matched-hash acceptance. No launcher or ledger mutation API."""
import pathlib,json,re,hashlib,importlib.util
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
BASE=N/'DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6'
def need(ok,why):
 if not ok:raise ValueError(why)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def legacy():
 s=importlib.util.spec_from_file_location('unchanged_BA_scientific',BASE/'ag6_strict.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def population(raw,s,d,m):
 matches=list(re.finditer(r'^kernel_name = (\S+)[ \t]*$',raw,re.M));rows=d['rows']
 need([x[1] for x in matches]==[r['kernel'] for r in rows],'whole ordered kernel names/count')
 need(raw.count('GPGPU-Sim: *** exit detected ***')==raw.count('GPGPU-Sim: *** simulation thread exiting ***')==1,'one natural model/thread exit')
 need('performance model initialization complete.' in raw and not re.search(m.FORBIDDEN,raw,re.I),'model init/no failure')
 commands=[]
 for line in raw.splitlines():
  if line.startswith('Processing kernel '):commands.append(line[len('Processing kernel '):].rsplit('/',1)[-1])
  elif line.startswith('launching memcpy command : '):commands.append(line[len('launching memcpy command : '):])
 need(commands==d['expected_commands'],'all original memcpy/kernel commands')
 need(re.findall(r'^Processing kernel (\S+)$',raw,re.M)==[r['path'] for r in rows],'every exact ordered trace member path')
 need(m.echo(raw)==s['expected_options'] and len(s['expected_options'])==270,'all270 effective options exact')
 need('DTC_PROGRESSIVE_WAKE_V1' not in raw and 'DTC_COLLECT_WB_PIPELINE_V1' not in raw and not re.search(r'^DTC_INVALIDATE_V1_(SNAPSHOT|SUMMARY)',raw,re.M),'AD/AC/K1_OFF')
 insns=ctas=0;metrics=[];kernels=[];blocks=[];previous_cycles=0
 for i,(match,row) in enumerate(zip(matches,rows),1):
  block=raw[match.start():matches[i].start() if i<len(matches) else len(raw)];x=m.numeric(block)
  insns+=int(row['active_thread_instructions']);ctas+=int(row['complete_ctas'])
  need(x['kernel_launch_uid']==i,'ordered kernel UID')
  need(x['gpu_sim_insn']==int(row['active_thread_instructions']) and x['gpu_tot_sim_insn']==insns and x['gpu_tot_issued_cta']==ctas,'per-kernel full instructions and cumulative CTA')
  need(type(x['gpu_tot_sim_cycle']) is int and x['gpu_tot_sim_cycle']>previous_cycles,'positive increasing cumulative cycles')
  if s['cell'].startswith('C'):
   need('DTC_L1_mode = PAPER_BASE' in block,'conventional mode per kernel')
   need(x['DTC_L1_pib_occupancy']==x['DTC_L1_lower_outstanding']==0,'conventional terminal drain per kernel')
   need(x['DTC_L1_pib_admits']==x['DTC_L1_pib_retires'],'conventional PIB exactly-once per kernel')
   need(x['DTC_L1_lower_requests_acquired']==x['DTC_L1_lower_requests_released'],'conventional lower conservation per kernel')
   need(x['DTC_L1_baseline_mshr_entries']==512,'conventional finite MSHR512')
  previous_cycles=x['gpu_tot_sim_cycle'];metrics.append(x);blocks.append(block)
  kernels.append({'ordinal':i,'kernel':row['kernel'],'cycles':x['gpu_sim_cycle'],'total_cycles':x['gpu_tot_sim_cycle'],'active_instructions':x['gpu_sim_insn'],'cumulative_CTA':ctas})
 need(insns==d['expected_instructions']==s['expected']['instructions'] and ctas==d['expected_CTA']==s['expected']['CTA'],'whole instructions/CTA')
 need(len(kernels)==s['expected']['kernels'],'whole kernel population')
 if s['cell'].startswith('D'):
  qualified=m.parse_full(raw,d,rows)
  m.pipeline_contract(raw,'AE' if s['cell']=='DH' else 'BASE',metrics[-1])
  need(qualified['cycles']==metrics[-1]['gpu_tot_sim_cycle'],'unchanged BA full DTC strict join')
 return {'cycles':metrics[-1]['gpu_tot_sim_cycle'],'instructions':insns,'CTA':ctas,'kernel_count':len(kernels),'kernels':kernels,'metrics':metrics[-1],'traffic':m.traffic(blocks[-1])}
def terminal(cohort):
 s=read(T/'control'/(cohort+'_SPEC.json'));req=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 need(sha(T/'control'/(cohort+'_SPEC.json'))==next(r['sha256'] for r in req['specs'] if r['cohort']==cohort),'spec frozen')
 need(sha(T/'control/INPUT_IDENTITIES.json')==req['input_identities_sha256'],'input manifest frozen')
 d=read(T/'control/INPUT_IDENTITIES.json')[s['workload']];m=legacy()
 intent=read(T/'control/qualification_ledger'/(cohort+'.INTENT.json'));done=read(T/'control/qualification_ledger'/(cohort+'.DONE.json'));out=P(intent['output'])
 need(done==read(out/'NATIVE_EXIT.json') and done['uuid']==intent['uuid'],'intent/DONE/native join')
 need(done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'natural native completion')
 need(sha(out/'raw.log')==done['raw_sha256'],'closed raw SHA')
 raw=(out/'raw.log').read_text();trace=(out/'actual_file_process_network.log').read_text()
 need('connect(' not in trace and '"/usr/bin/ssh"' not in trace and '"/bin/ssh"' not in trace,'no scientific SSH/network')
 for r in d['rows']:need(r['path'] in trace,'actual read every original trace member')
 launch=read(out/'NATIVE_LAUNCH.json');pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 need(launch['argv'][-len(s['native_simulator_argv']):]==s['native_simulator_argv'],'actual exact argv')
 need(pid['mnt_namespace']==s['execution_mnt_namespace'] and launch['host']['hostname']=='huangrulin-sshfs-174','native namespace/host')
 need(s['core_commit'][:7] in raw and s['framework_commit'] in raw,'actual source echoes')
 need(str(T/'DTC/bin/accel-sim.out') in pid['maps'],'actual mapped simulator')
 for r in s['runtime_files']:need(sha(T/r['target'])==r['sha256'],'runtime still frozen')
 result=population(raw,s,d,m)
 progress=[json.loads(l) for l in (out/'progress.jsonl').read_text().splitlines()]
 need(progress and progress[-1]['end']=='NATURAL' and progress[-1]['completed']==d['expected_instructions'],'whole-input authenticated semantic NATURAL')
 need(all(r['pid']==pid['pid'] and r['start_ticks']==pid['start_ticks'] and r['generation']==done['uuid'] for r in progress),'authenticated process/generation')
 samples=[json.loads(l) for l in (out/'RESOURCE_SAMPLES.jsonl').read_text().splitlines()]
 decisions=[r['DTC_exact_original_policy']['decision'] for r in samples if 'DTC_exact_original_policy' in r]
 need(decisions and all(r['decision']!='STOP' for r in decisions),'original BA resource policy per bound native process')
 result.update(schema='DTC_AEFAIR_SHORT3_WHOLE_INPUT_STRICT_V1',cohort=cohort,workload=s['workload'],cell=s['cell'],uuid=done['uuid'],status='PASS_FULL_NATIVE_STRICT_BOUNDED_MODEL',performance_accepted=True,raw_sha256=done['raw_sha256'],core_commit=s['core_commit'],framework_commit=s['framework_commit'],binary_sha256=s['binary_sha256'],progress_records=len(progress),resource_decisions=len(decisions),effective_options=s['expected_options'],native_values='UNPROVEN',hardware_PPA='UNPROVEN',SOURCE_KEEP=True)
 return result
