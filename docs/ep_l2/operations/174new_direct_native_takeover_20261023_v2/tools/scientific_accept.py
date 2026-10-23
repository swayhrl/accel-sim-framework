"""Independent native migration terminal join, never a scientific launcher.

Reuses unchanged E terminal and BA pure scientific validators. Original cohort
UUID/old-parent guard receipts are never forged for a new native run. Native
identity/authority/exit/resource evidence is joined separately and explicitly.
This tool cannot change the original Source registry or refund any attempt.
"""
import pathlib,json,hashlib,importlib.util,sys,re,csv,io,os
P=pathlib.Path;R=P('/root/data/ep_l2_dtc_l1_native_v2');sys.dont_write_bytecode=True
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError(msg)
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def exclusive(p,x):
 b=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
 if p.exists():need(p.read_bytes()==b,'existing qualification proof collision')
 else:
  with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def accepted(cohort):
 need(cohort in ['EP_NATIVE_MIGRATION_Q1','EP_NATIVE_MIGRATION_Q2','DTC_NATIVE_MIGRATION_Q1'],'unsupported cohort');s=read(R/'control'/(cohort+'_SPEC.json'));intent=read(R/'control/qualification_ledger'/(cohort+'.INTENT.json'));done=read(R/'control/qualification_ledger'/(cohort+'.DONE.json'));root=P(intent['output']);need(done==read(root/'NATIVE_EXIT.json'),'native DONE/receipt mismatch')
 need(done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'not a natural native complete exit; retain unqualified')
 n=read(root/'NATIVE_SIMULATOR_PID_AND_MAPS.json');launch=read(root/'NATIVE_LAUNCH.json');need(n['mnt_namespace']=='mnt:[4026535153]' and launch['host']['hostname']=='huangrulin-sshfs-174','not genuine native target process')
 need(sha(root/'raw.log')==done['raw_sha256'],'closed output SHA mismatch');raw=(root/'raw.log').read_text(errors='strict');trace=(root/'actual_file_process_network.log').read_text(errors='strict')
 need('kernel-1.traceg' in trace and 'connect(' not in trace and '"/usr/bin/ssh"' not in trace and '"/bin/ssh"' not in trace,'actual trace open/no network evidence missing')
 need(launch['argv'][-len(s['native_simulator_argv']):]==s['native_simulator_argv'],'actual simulation argv differs from frozen source/config/trace scope')
 need(sha(P(s['native_simulator_argv'][0]))==s['binary_sha256'],'actual native binary SHA drift')
 ctx={'schema':'NATIVE_MIGRATION_INDEPENDENT_TERMINAL_JOIN_V1','cohort':cohort,'uuid':done['uuid'],'native_PID':n['pid'],'native_mnt_namespace':n['mnt_namespace'],'original_source_EP_starts':57,'original_source_DTC_starts':2,'native_start_consumed':1,'automatic_retry':False,'numeric_SASS_output_validation':'Not newly claimed; frozen original trace-model scientific scope only','SOURCE_KEEP':True,'scientific_source_input_config_identity':'Exact original bindings and current closed-full-SHA trace receipts','native_exit_receipt_sha256':sha(root/'NATIVE_EXIT.json'),'native_launcher_sha256':launch.get('finite_native_launcher_sha256'),'actual_trace_and_file_evidence_sha256':sha(root/'actual_file_process_network.log')}
 if s['project']=='EP':
  sys.path[:0]=[str(R/'EP/src/owner-control/util/ep_l2/mechanism_e'),str(R/'EP/src/owner-control/util/ep_l2/ft_lane5')]
  parser=module('exact_native_EP_terminal',R/'EP/control/parse_main_terminal.py');summary=parser.parse(root/'raw.log',s['source_input_spec'],s['owner_qualification']['qualification']);reference=read(R/'control/EP_ACCEPTED_REFERENCE_CTA_AND_KERNEL.json')
  cta=re.findall(r'^gpu_tot_issued_cta\s*=\s*(\d+)\s*$',raw,re.M);kernels=re.findall(r'^kernel_name\s*=\s*(\S+)\s*$',raw,re.M)
  need(summary['cycles']==73696 and summary['instructions']==56000000 and summary['slices']==64 and summary['hardware_drained'],'EP exact cycle/instruction/slice/drain equivalence')
  need(cta and int(cta[-1])==reference['last_cumulative_fields']['gpu_tot_issued_cta']==15625 and kernels==reference['kernel_names'],'EP full CTA/kernel identity')
  ctx.update(status='EP_SCIENCE_QUALIFIED',cycles=summary['cycles'],instructions=summary['instructions'],CTA=int(cta[-1]),kernel_count=len(kernels),slices=64,hardware_drained=True,qualification_authority='Existing exact E qualification and unchanged terminal decoder plus explicit user-approved native cohort; no old application reacceptance')
 else:
  base=R/'DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6';legacy=module('native_exact_BA_scientific',base/'ag6_strict.py');baseline=read(R/'control/DTC_ACCEPTED_STRICT_BASELINE.json');d=read(R/'control/DTC_ORIGINAL_INPUT_RUNTIME_IDENTITY.json')
  audit=(base/'identity_metadata/KERNEL_BODY_AUDIT.tsv').read_bytes();need(hashlib.sha256(audit).hexdigest()==legacy.AUDIT_SHA256,'old exact body audit changed');rows=[x for x in csv.DictReader(io.StringIO(audit.decode()),delimiter='\t') if x['workload'].lower()=='gemm'];need(len(rows)==1 and rows[0]['sha256']=='fa70ba180d886dcfa313b0e6036da86c3cabadcbc6bf5b6499e0e6d74af1373d','historical exact full member identity not bound')
  need(d['expected_embedded_core_version'] in raw and d['expected_embedded_framework_version'] in raw,'actual DTC Core/Framework version')
  parsed=legacy.parse_full(raw,d,rows);need(len(parsed['effective_options'])==270 and parsed['effective_options']==baseline['effective_options'],'all270 effective options differ');pipeline=legacy.pipeline_contract(raw,'AD',parsed['final_metrics']);need((parsed['cycles'],parsed['active_instructions'],parsed['CTA'],parsed['kernel_count'])==(1044499,739246080,1024,1),'DTC full application baseline equivalence')
  records=[json.loads(x) for x in (root/'progress.jsonl').read_text().splitlines()];need(records and records[-1]['end']=='NATURAL' and records[-1]['completed']==739246080 and all(x['pid']==n['pid'] and x['generation']==done['uuid'] for x in records),'authenticated native whole-input natural progress identity')
  decisions=[json.loads(x)['DTC_exact_original_policy']['decision'] for x in (root/'RESOURCE_SAMPLES.jsonl').read_text().splitlines() if 'DTC_exact_original_policy' in x];need(decisions and all(x['decision']!='STOP' for x in decisions),'original BA runtime safety closure missing')
  summary={'parse_full':parsed,'AD_pipeline':pipeline,'actual_native_guard':'Separate local PID/SCM_CREDENTIALS/resource/wait evidence, never substituted old AG8R1 UUID or old-parent receipts','original_BA_strict_comparison':{'path':baseline.get('receipt_sha256'),'old_attempt_uuid':baseline['attempt_uuid'],'all_270_options_exact':True}}
  ctx.update(status='DTC_SCIENCE_QUALIFIED',cycles=parsed['cycles'],instructions=parsed['active_instructions'],CTA=parsed['CTA'],kernel_count=parsed['kernel_count'],strict_scientific_checks='Unchanged BA parse_full and pipeline_contract, original terminal ownership/credit/finite population checks; new native authority identity joined separately',authenticated_progress_records=len(records),original_runtime_resource_decisions=len(decisions))
 exclusive(root/'INDEPENDENT_NATIVE_SCIENTIFIC_TERMINAL.json',summary);ctx['terminal_summary_sha256']=sha(root/'INDEPENDENT_NATIVE_SCIENTIFIC_TERMINAL.json');proof=R/s['project']/'control'/('SCIENCE_QUALIFICATION_'+cohort+'.json');exclusive(proof,ctx)
 # Current pointer evolves only after a new independently complete proof. Old
 # failed qualification JSON is retained verbatim as its own cohort artifact.
 current=R/s['project']/'control/SCIENCE_QUALIFICATION.json'
 if current.exists() and read(current).get('status')!=ctx['status']:
  previous=current.with_name('SCIENCE_QUALIFICATION_PREVIOUS_'+sha(current)+'.json')
  if not previous.exists():previous.write_bytes(current.read_bytes())
 tmp=current.with_name('.SCIENCE_QUALIFICATION_'+done['uuid']+'.writing');tmp.write_bytes(proof.read_bytes());os.replace(tmp,current)
 return ctx
if __name__=='__main__':
 try:print(json.dumps(accepted(sys.argv[1]),indent=2))
 except (RuntimeError,ValueError,KeyError,OSError) as e:print(json.dumps({'status':'HOLD_UNQUALIFIED','reason':str(e),'automatic_retry':False}),file=sys.stderr);sys.exit(2)
