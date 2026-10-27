"""Create immutable read-only certificate for B's future CPU qualification only."""
import collections,copy,datetime,hashlib,json,math,pathlib,re
P=pathlib.Path;G=1024**3;M=1024**2
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/padding_only_admission_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
TARGETS={'-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size'}
BASE=(192,4,32,64)
ALLOWED={BASE}|{tuple(v if i==j else BASE[i]for i in range(4))for j,values in enumerate([(384,768),(8,16),(64,128),(128,256)])for v in values}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def stable(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def params(options):
    text=options['-gpgpu_cache:dl2'][0]
    m=re.fullmatch(r'S:128:128:16,L:B:m:L:L,A:(\d+):(\d+),(\d+):0,32',text)
    if not m:raise ValueError('L2_GEOMETRY_OR_MASKED_SCOPE_MISMATCH')
    p=tuple(map(int,m.groups()))+(int(options['-gpgpu_frfcfs_dram_sched_queue_size'][0]),)
    if p not in ALLOWED:raise ValueError('COMBINATION_OR_EXTENSION_NOT_ELIGIBLE')
    return p
def freeze(path,value):
    b=(json.dumps(value,indent=2,sort_keys=True)+'\n').encode();path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==b,'IMMUTABLE_CERTIFICATE_ALREADY_EXISTS_DIFFERENT'
    else:
        with path.open('xb')as h:h.write(b)
def main():
    qp=A/'QUANTIFICATION.json';x=read(qp);frozen=A/'frozen_inputs'/('QUANTIFICATION.'+sha(qp)+'.json')
    frozen.parent.mkdir(exist_ok=True)
    if not frozen.exists():frozen.write_bytes(qp.read_bytes())
    q=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][REQ]
    observer=read(R/'control/RESOURCE_OBSERVER.json');initial=read(R/'control/RESOURCE_FORECASTS_INITIAL.json')
    policy=read(R/'control/RESOURCE_POLICY.json');certs=[];rejected=[];now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for row in x['rows']:
        c=row['cohort']
        if not row['grade'].startswith('A_'):continue
        try:
            value=q['consumed'][c]
            if 'execution_receipt'in value:raise ValueError('NO_LONGER_RUNNING_NATURAL_CLOSED')
            sp=R/'control/specs'/(c+'.json');s=read(sp);ssha=sha(sp)
            if ssha!=q['admitted_specs'][c]:raise ValueError('CURRENT_SPEC_REGISTRY_SHA_MISMATCH')
            if s['estimated_peak_model_RAM_bytes']!=row['current_prediction_bytes']:raise ValueError('CANONICAL_PREDICTION_CHANGED')
            opts=s['expected_options'];current_target=params(opts);non={k:v for k,v in opts.items()if k not in TARGETS};non_sha=stable(non)
            pins=[]
            def pin(path,role):
                path=P(path)
                if not path.exists():raise ValueError('MISSING_PINNED_EVIDENCE_'+role)
                p=dict(path=str(path),sha256=sha(path),role=role)
                if p not in pins:pins.append(p)
                return p
            pin(sp,'CURRENT_CANONICAL_SPEC');pin(R/'control'/(c+'_SPEC.json'),'CURRENT_CANONICAL_ALIAS')
            binding=P(s.get('input_binding_path',str(R/'control/input_bindings'/(s['input_digest']+'.json'))))
            if sha(binding)!=s['input_binding_sha256']:raise ValueError('CURRENT_INPUT_BINDING_SHA_MISMATCH')
            pin(binding,'CURRENT_FULL_INPUT_BINDING')
            out=R/'DTC/run/results'/value['uuid'];ip=R/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip)
            if sha(ip)!=value['intent_sha256']or intent['uuid']!=value['uuid']:raise ValueError('CURRENT_INTENT_UUID_SHA_MISMATCH')
            pin(ip,'CURRENT_INTENT');db=out/'DISPATCH_BINDING.json';dispatch=read(db)
            resolved=copy.deepcopy(s);resolved['host_cpu']=dispatch['host_cpu']
            resolved_sha=hashlib.sha256((json.dumps(resolved,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
            if dispatch['canonical_spec_sha256']!=ssha or intent['dispatch_binding_sha256']!=sha(db)or intent['spec_sha256']!=ssha or dispatch['resolved_spec_sha256']!=resolved_sha:
                raise ValueError('DISPATCH_CANONICAL_BINDING_MISMATCH')
            pin(db,'CURRENT_DISPATCH_BINDING');launch=out/'NATIVE_LAUNCH.json';pin(launch,'CURRENT_NATIVE_LAUNCH')
            observed=[v for v in observer['observed_models']if dispatch['host_cpu']in v['cpus']]
            if len(observed)!=1:raise ValueError('CURRENT_NATIVE_GENERATION_NOT_UNIQUE')
            process=observed[0];pid=process['pid'];proc=P('/proc')/str(pid)
            stat=proc.joinpath('stat').read_text().rsplit(')',1)[1].split();start=int(stat[19])
            status=proc.joinpath('status').read_text();rss=int(re.search(r'^VmRSS:\s+(\d+)',status,re.M).group(1))*1024
            env=dict(part.split('=',1)for part in proc.joinpath('environ').read_bytes().decode(errors='replace').split('\0')if'='in part)
            if env.get('DTC_AG7_GENERATION')!=value['uuid']or env.get('DTC_AG7_INPUT_SHA')!=s['input_digest']:raise ValueError('CURRENT_MODEL_GENERATION_ENV_MISMATCH')
            cmd=proc.joinpath('cmdline').read_bytes().split(b'\0');cmd=[a.decode(errors='replace')for a in cmd if a]
            if s['native_simulator_argv'][0]not in cmd or s['native_simulator_argv'][2]not in cmd:raise ValueError('CURRENT_MODEL_NATIVE_CMD_MISMATCH')
            # Observed model list is produced by actual model ELF classification;
            # environment + exact input/argv + PID start recheck binds this snapshot.
            if int(proc.joinpath('stat').read_text().rsplit(')',1)[1].split()[19])!=start:raise ValueError('PID_START_RACE')
            ep=[];exact_profile=[]
            for source in row['evidence']:
                if not source['strict_design']:continue
                hs=read(source['spec_path'])
                try:history_target=params(hs['expected_options'])
                except (ValueError,KeyError):continue
                hn={k:v for k,v in hs['expected_options'].items()if k not in TARGETS}
                if stable(hn)!=non_sha:continue
                root=P(source['receipt_path']).parent.parent.parent;hc=source['cohort'];done=read(source['receipt_path']);v=read(source['result_path']);proof=v['proof']
                hp=root/'control/qualification_ledger'/(hc+'.INTENT.json')
                hi=read(hp)
                if hi['uuid']!=done['uuid']or v['uuid']!=done['uuid']or proof['uuid']!=done['uuid']:raise ValueError('HISTORICAL_INTENT_UUID_MISMATCH')
                hpins=[pin(source['spec_path'],'HISTORY_SPEC'),pin(source['receipt_path'],'HISTORY_NATURAL_DONE'),pin(hp,'HISTORY_INTENT'),pin(source['result_path'],'HISTORY_STRICT_AND_NATIVE_RESTORE_RESULT')]
                archive=root/'control'/(hc+'_ARCHIVE_RECEIPT.json')
                if archive.exists():hpins.append(pin(archive,'HISTORY_ARCHIVE_NATIVE_RESTORE_RECEIPT'))
                # Full strict proof and independent restored-entry verification are
                # retained at these immutable source-specific JSON pointers.
                evidence=dict(cohort=hc,uuid=done['uuid'],input_digest=hs['input_digest'],input_binding_sha256=hs['input_binding_sha256'],
                    core_commit=hs['core_commit'],framework_commit=hs['framework_commit'],binary_sha256=hs['binary_sha256'],cell=hs['cell'],
                    spec_path=source['spec_path'],spec_sha256=source['spec_sha256'],intent_path=str(hp),intent_sha256=sha(hp),
                    DONE_path=source['receipt_path'],DONE_sha256=source['receipt_sha256'],strict_path=source['result_path'],strict_sha256=source['result_sha256'],strict_json_pointer='/proof',
                    archive_evidence_path=source['result_path'],archive_evidence_sha256=source['result_sha256'],archive_json_pointer='/archive',
                    full_population=hs['expected'],strict_population=dict(instructions=proof['instructions'],CTA=proof['CTA'],kernels=proof['kernel_count']),
                    natural_done=True,certified_peak_RSS_bytes=done['peak_observed_rss_bytes'],history_non_target_sha256=stable(hn),
                    history_effective_options_sha256=stable(hs['expected_options']),history_target_values=history_target,
                    exact_full_effective_options_equal=hs['expected_options']==opts,proof_kind=source['proof_kind'],pinned_files=hpins)
                ep.append(evidence)
                if evidence['exact_full_effective_options_equal']:exact_profile.append(evidence)
            if not ep:raise ValueError('NO_ALLOWED_INITIAL_RANGE_SAME_DESIGN_FULL_EVIDENCE')
            peak=max(e['certified_peak_RSS_bytes']for e in ep);basis=row['formula_basis'];Pold=basis['registered_historical_peak_bytes'];Pnew=basis['peak_used_not_lowered_bytes']
            if rss>peak:raise ValueError('CURRENT_RSS_EXCEEDS_CERTIFIED_SAME_DESIGN_PEAK')
            if Pnew<max(Pold,peak):raise ValueError('APPROVED_P_WOULD_LOWER_REGISTERED_OR_CERTIFIED_PEAK')
            provenance_source=basis['source']
            if provenance_source=='LAST_REGISTERED_RESOURCE_AMENDMENT':
                pp=R/'control/resource_spec_history'/c/(ssha+'.AMENDMENT.json');pointer='/forecast'
            elif provenance_source=='INITIAL_REGISTERED_FORECAST':
                pp=R/'control/RESOURCE_FORECASTS_INITIAL.json';pointer='/'+str(next(i for i,v in enumerate(initial)if v['cohort']==c))
            else:
                pp=A/'frozen_inputs'/(c+'.READONLY_FORECAST_BASIS.json');freeze(pp,dict(cohort=c,historical_peak_bytes=Pold,source_row=basis));pointer='/'
            pin(pp,'ORIGINAL_PADDING_FORMULA_PROVENANCE')
            if max(policy['minimum_prediction_bytes'],math.ceil(Pold*1.2)+256*M)+policy['candidate_l2_metadata_margin_bytes']!=s['estimated_peak_model_RAM_bytes']:
                raise ValueError('ORIGINAL_FORMULA_NOT_EXACT')
            new_est=max(policy['minimum_prediction_bytes'],math.ceil(Pnew*1.1)+128*M)+policy['candidate_l2_metadata_margin_bytes']
            new_est=min(new_est,s['estimated_peak_model_RAM_bytes'])
            if new_est!=row['proposed_prediction_bytes']:raise ValueError('APPROVED_NEW_ESTIMATE_MISMATCH')
            proc_proof=A/'frozen_inputs'/(c+'.'+str(pid)+'.'+str(start)+'.PID_PROOF.json')
            freeze(proc_proof,dict(UTC=now,cohort=c,uuid=value['uuid'],pid=pid,start_ticks=start,
                input_digest=s['input_digest'],boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip(),
                generation_environment_verified=True,input_environment_verified=True,native_argv_verified=True,
                observed_RSS_bytes=rss,source='read-only /proc stat/status/environ/cmdline twice-start checked'))
            pin(proc_proof,'FROZEN_ACTUAL_PID_GENERATION_OBSERVATION')
            certs.append(dict(actual_cohort=c,uuid=value['uuid'],pid=pid,start_ticks=start,
                canonical_spec_path=str(sp),canonical_spec_sha256=ssha,input_digest=s['input_digest'],input_binding_sha256=s['input_binding_sha256'],
                core_commit=s['core_commit'],framework_commit=s['framework_commit'],binary_sha256=s['binary_sha256'],cell=s['cell'],profile=s['profile'],
                expected_population=s['expected'],normalized_non_target_options=non,normalized_non_target_options_sha256=non_sha,
                effective_options_sha256=stable(opts),masked_target_options={k:opts[k]for k in TARGETS},current_target_values=current_target,
                eligibility_class='A_SAME_DESIGN_TARGET_FIELD_MASKED_FORECAST_TRANSFER',
                scope='INITIAL9_SINGLE_FACTOR_ONLY_NOT_FULL_OPTIONS_EQUIVALENCE',
                old_peak_provenance_P=Pold,old_peak_provenance=dict(path=str(pp),sha256=sha(pp),json_pointer=pointer,source=provenance_source),
                certified_sameDesign_peak_P=peak,approved_new_formula_input_P=Pnew,
                minimum_prediction_bytes=policy['minimum_prediction_bytes'],metadata_margin_bytes=policy['candidate_l2_metadata_margin_bytes'],
                old_estimated_peak_bytes=s['estimated_peak_model_RAM_bytes'],approved_new_estimated_peak_bytes=new_est,
                hard_cap_bytes=s['limits']['max_process_tree_rss_bytes'],max_prediction_reduction_bytes=s['estimated_peak_model_RAM_bytes']-new_est,
                snapshot_max_future_discount_bytes=row['strict_A_saving_bytes'],snapshot_current_RSS_bytes=row['current_RSS_bytes'],
                current_pid_proof_RSS_bytes=rss,current_RSS_below_certified_sameDesign_peak=True,
                exact_profile_only_evidence_count=len(exact_profile),exact_profile_only_max_peak=max([e['certified_peak_RSS_bytes']for e in exact_profile]+[0]),
                evidence=ep,pinned_files=pins))
        except (OSError,ValueError,KeyError,StopIteration,AttributeError)as exc:rejected.append(dict(cohort=c,reason=str(exc)))
    manifest=dict(schema='DTC_PADDING_A_ONLY_ELIGIBILITY_CERTIFICATE_V1',created_UTC=now,
        quantification_path=str(frozen),quantification_sha256=sha(frozen),original_policy_sha256=sha(R/'control/RESOURCE_POLICY.json'),
        expected_policy_host_floor_bytes=policy['min_host_headroom_bytes'],expected_policy_cgroup_floor_bytes=policy['min_cgroup_headroom_bytes'],
        certificates=certs,rejected_A_snapshot_rows=rejected,
        max_snapshot_discount_bytes=sum(c['snapshot_max_future_discount_bytes']for c in certs),
        exact_profile_only_snapshot_discount_bytes=sum(c['snapshot_max_future_discount_bytes']for c in certs if c['exact_profile_only_evidence_count']),
        hash_algorithm='sha256(json.dumps(value,sort_keys=True,separators=(comma,colon)).encode(UTF8))',
        target_keys=sorted(TARGETS),allowed_initial_target_vectors=[list(v)for v in sorted(ALLOWED)],
        target_transfer_not_exact_configuration=True,metadata_margin_is_empirical_not_mathematical_upper_bound=True,
        candidate_claim_foreign_unknown_failed_rows_unchanged=True,not_a_runtime_constant=True,
        runtime_revalidation='every current PID/start/spec/binding/source pin; discount=min(snapshotcap, actual oldenv-newenv), zero if current RSS>certified same-design peak; preserve .10 RSS envelope and hardcaps',
        model_launches=0,signals_sent=0,production_changes=0)
    path=A/'A_ONLY_ELIGIBILITY_CERTIFICATE_V1.json'
    if path.exists():
        old=read(path)
        if old['certificates']==[] and all(v['reason']in('DISPATCH_CANONICAL_BINDING_MISMATCH','NO_LONGER_RUNNING_NATURAL_CLOSED')for v in old['rejected_A_snapshot_rows']):
            saved=A/'draft_preimages'/(path.name+'.'+sha(path));saved.parent.mkdir(exist_ok=True);path.rename(saved)
    freeze(path,manifest)
    print(json.dumps(dict(path=str(path),sha256=sha(path),eligible=len(certs),rejected=rejected,
        maximum_snapshot_savings_GiB=manifest['max_snapshot_discount_bytes']/G,
        exact_profile_only_savings_GiB=manifest['exact_profile_only_snapshot_discount_bytes']/G),indent=2))

if __name__=='__main__':main()
