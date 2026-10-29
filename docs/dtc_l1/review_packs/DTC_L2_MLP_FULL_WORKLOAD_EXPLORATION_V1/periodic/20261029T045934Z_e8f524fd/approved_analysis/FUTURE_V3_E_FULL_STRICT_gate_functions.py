# Included verbatim into new bpf_extra_strict.py; never changes V2 sources.
GATE_SCHEMA='DTC_BPF_FUTURE_V3_REAL_CANARY4_GATE_V1'
V2_EXTRA=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/strace_bpf_future_entry_v2/bpf_extra_strict.py')
V2_EXTRA_SHA='cbbddba1fe954a1e7dd411c89f9feff2480d5314781204b75fc8364159586711'
V2_BRIDGE_SHA='5c4ded4df0dee860015208b0af46d967e91a0bb2a2fc98e6830ed7b54db6ae9f'
CPU_OWNER=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/cpu_spare_memory_v2/cpu_owner.py')
CPU_OWNER_SHA='4945156fe11db69f75a6f1dc39e08a0f5c7b28ef43244525f570bebbf33cf080'
OLD_STRICT_SHA='f889b248adca6f466f8ee19fb2dc17986e355196132c716b7b6fc50ced333b59'
OLD_OUTBOX_SHA='d4b58b362a39c9d198a40e5c252f6eb07ba780e4707ffd79f6724569e349c4a5'
def load_pinned(path,expected,name):
 require(sha(path)==expected,'Pinned helper/source drift '+str(path))
 sp=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module);return module
def _require_existing_sidecars(result,out):
 proof=result['proof']
 for key in ['additional_cpu_spare_memory_admission_strict','additional_strace_bpf_observation_strict']:
  side=proof[key];path=P(side['sidecar_path']);require(path.parent==out and path.exists()and sha(path)==side['sidecar_sha256'],'Readonly prerequisite sidecar '+key)
 io=proof.get('additional_shared_json_io_strict')or proof.get('additional_future_memory_io_strict')
 require(io is not None and P(io['sidecar_path']).parent==out and sha(io['sidecar_path'])==io['sidecar_sha256'],'Readonly prerequisite IO sidecar')
def replay_v2_canary(cohort,authority):
 """Actual standalone readonly replay of the same old physics+CPU2+IO+V2 chain.

 Existing sidecars are mandatory before terminal helpers execute, so replay
 cannot mint missing strict evidence. No authority writer may call this.
 """
 require(sha(MAIN_EXCLUSION_PATH)==MAIN_EXCLUSION_SHA,'Main exact4 contract drift')
 exclusion=read(MAIN_EXCLUSION_PATH);require(cohort in exclusion['scope_cohorts'],'Not exact engineering4')
 rp=PRODUCTION_ROOT/'analysis'/(cohort+'.RESULT.json');value=read(rp)
 require(value['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and value['scientific_role']=='ENGINEERING_OBSERVATION_CANARY'and value['primary_statistics_excluded']is True and value['validated_union_authorized']is False,'Not a real accepted engineering RESULT')
 require(read(PRODUCTION_ROOT/'analysis/engineering_results'/(cohort+'.RESULT.json'))==value,'Engineering mirror changed')
 intent=read(PRODUCTION_ROOT/'control/qualification_ledger'/(cohort+'.INTENT.json'));out=P(intent['output'])
 _require_existing_sidecars(value,out)
 original=load_pinned(PRODUCTION_ROOT/'tools/l2_strict.py',OLD_STRICT_SHA,'v3_gate_original_strict')
 base=original.terminal(cohort)
 owner=load_pinned(CPU_OWNER,CPU_OWNER_SHA,'v3_gate_historical_CPU2_owner')
 historical=owner.historical_extra(intent,out)
 proof=historical.terminal(cohort,base)
 v2=load_pinned(V2_EXTRA,V2_EXTRA_SHA,'v3_gate_V2_strict')
 contract=v2.normalize_contract(exclusion,PRODUCTION_ROOT,MAIN_EXCLUSION_SHA,False)
 observed=v2.terminal(cohort,proof,PRODUCTION_ROOT,contract,authority,readonly=True)
 require(observed==value['proof'],'Readonly original/CPU2/IO/V2 strict changed')
 outbox=load_pinned(PRODUCTION_ROOT/'tools/l2_outbox.py',OLD_OUTBOX_SHA,'v3_gate_original_outbox')
 archive=outbox.verify(cohort)
 require(archive=={k:v for k,v in value['archive'].items()if k!='additional_strace_bpf_archive_verification'},'Readonly original full archive changed')
 require(v2.verify_archive(cohort,archive,PRODUCTION_ROOT,contract)==value['archive']['additional_strace_bpf_archive_verification'],'Readonly observation/native restore changed')
 return value
def _gate_row(cohort,value):
 proof=value['proof'];extra=proof[KEY]
 return dict(cohort=cohort,RESULT_sha256=sha(PRODUCTION_ROOT/'analysis'/(cohort+'.RESULT.json')),
  uuid=proof['uuid'],cycles=proof['cycles'],mode=extra['mode'],
  counts={k:proof[k]for k in ['CTA','instructions','kernel_count']},
  archive_manifest_sha256=value['archive']['additional_strace_bpf_archive_verification']['manifest_sha256'],
  archive_sha256=value['archive']['additional_strace_bpf_archive_verification']['archive_sha256'])
def capture_release_prerequisite(frame,main,path):
 """Explicit same-Main-owner receipt writer, not invoked on import/installation.

 It requires the actual current V2 bridge, never an injected fake callback.
 Actual model experiments and grant writes are not performed by this method.
 """
 import os,threading,datetime
 require(threading.current_thread()is threading.main_thread()and os.getpid()==1498278,'Actual Main owner required')
 require(int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783,'Main PID generation changed')
 marker=main.DTC_STRACE_BPF_PRIVATE_CONSUMER_V2
 require(marker['frame']is frame and marker['consumer']is frame.f_locals['consumer']and marker['consumer'].safe_finish is marker['wrapper'],'Actual V2 bridge route required')
 require(marker['source_sha256']==V2_BRIDGE_SHA and not marker['cfg']['qualification_only'],'Production V2 generation only')
 require(sha(marker['bridge']['readonly_replay'].__code__.co_filename)==V2_BRIDGE_SHA,'V2 replay source drift')
 engine=frame.f_locals['engine'];engine.assert_parent_lease()
 q=engine.registered()[2];rows=[]
 for cohort in sorted(read(MAIN_EXCLUSION_PATH)['scope_cohorts']):
  actual=marker['bridge']['readonly_replay'](cohort)
  require(actual==replay_v2_canary(cohort,q),'Actual bridge and standalone readonly replay differ')
  rows.append(_gate_row(cohort,actual))
 result=dict(schema=GATE_SCHEMA,kind='ACTUAL_SAME_OWNER_V2_FULL_READONLY_REPLAY',qualification_only=False,
  capture_source_sha256=sha(__file__),V2_bridge_sha256=V2_BRIDGE_SHA,V2_extra_sha256=V2_EXTRA_SHA,
  exclusion_contract_sha256=MAIN_EXCLUSION_SHA,canaries=rows,
  UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_owner_pid=os.getpid(),actual_owner_start_ticks=977758783)
 path=P(path);require(not path.exists(),'Prerequisite receipt immutable; do not overwrite')
 producer_path=marker['cfg']['source_paths']['producer'];producer=load_pinned(producer_path,marker['cfg']['qualified_sources']['producer'],'v3_gate_atomic_writer')
 producer.atomic_exclusive(path,result)
 return dict(path=str(path),sha256=sha(path),receipt=result)
def verify_release_prerequisite(cfg,authority):
 """Full replay before any V3 selected INTENT; never call under authority EX."""
 path=P(cfg['canary4_prerequisite_path']);require(sha(path)==cfg['canary4_prerequisite_sha256'],'Canary4 prerequisite SHA')
 gate=read(path);require(gate['schema']==GATE_SCHEMA,'Wrong prerequisite generation')
 qualification=cfg.get('qualification_only')is True and authority.get('qualification_only')is True and P(cfg['root']).resolve()!=PRODUCTION_ROOT.resolve()
 if qualification:
  require(gate['kind']=='CPU_ONLY_PREREQUISITE_STANDIN_NOT_ACTUAL_CANARY'and gate['qualification_only']is True,'Explicit CPU-only quorum fixture required')
  return dict(status='CPU_ONLY_GATE_QUALIFIED_NOT_PRODUCTION_RELEASE',production_release_eligible=False,prerequisite_sha256=sha(path))
 require(P(cfg['root'])==PRODUCTION_ROOT and cfg.get('qualification_only')is False and gate['qualification_only']is False,'CPU gate cannot release production')
 require(gate['kind']=='ACTUAL_SAME_OWNER_V2_FULL_READONLY_REPLAY'and gate['capture_source_sha256']==sha(__file__),'Real full-replay source-bound prerequisite required')
 require(gate['V2_bridge_sha256']==V2_BRIDGE_SHA and gate['V2_extra_sha256']==V2_EXTRA_SHA and gate['exclusion_contract_sha256']==MAIN_EXCLUSION_SHA,'Prerequisite old-source chain')
 require(gate['actual_owner_pid']==1498278 and gate['actual_owner_start_ticks']==977758783,'Prerequisite owner generation')
 rows={r['cohort']:r for r in gate['canaries']};required=set(read(MAIN_EXCLUSION_PATH)['scope_cohorts'])
 require(len(rows)==len(gate['canaries'])==4 and set(rows)==required,'Exact four actual accepted prerequisites')
 for cohort in sorted(required):require(rows[cohort]==_gate_row(cohort,replay_v2_canary(cohort,authority)),'Real prerequisite replay changed '+cohort)
 return dict(status='ACTUAL_CANARY4_GATE_VERIFIED',production_release_eligible=True,prerequisite_sha256=sha(path),actual_canary_cohorts=sorted(required))
