"""AA3 CPU-only preparation and authority STOP evidence. Never launches a simulator."""
from common import *
import stat
OLD=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-aa2-gaussian-factorial-174-v1/docs/dtc_l1/review_packs/DTC_LANE_AA2_GAUSSIAN_V1')
FROZEN={'X':'49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4','V':V_SHA,'Y2':'d085f98c10010d641ba4cfffa1f58fb8db3b56ee','Z2':'2b633a616dc59efb99973e94bdfa421e28c33fab','U':'16e56912cfd02f2311a1603a29415dee829fd495','Core':CANDIDATE_CORE}

def main():
    bindings=[]
    for lane,commit in FROZEN.items():
        repo=CORE_REPO if lane=='Core' else FW_REPO
        actual=git(repo,'rev-parse','refs/aa3-bindings/'+lane)
        assert actual==commit,(lane,actual)
        bindings.append(dict(lane=lane,frozen_commit=commit,fetch_back_ref='refs/aa3-bindings/'+lane,fetch_back_commit=actual,tree=git(repo,'rev-parse',commit+'^{tree}')))
    write(PACK/'SOURCE_BINDINGS.json',dict(utc=now(),bindings=bindings,AA_frozen=AA_SHA,AA2_frozen='fa7bd9ee7667ebb94e919295755311a2a2da4541'))
    files={
      'X':('DTC_LANE_X_OPTIN_INVALIDATION_V1',['SOURCE_AND_BINARY_IDENTITY.json','SOURCE_EVENT_AUDIT.json','CORNER_CASE_CHECKS.json','LATEST_REPORT.md','GIT_DELIVERY.json']),
      'V':('DTC_LANE_V_SEMANTIC_V1',['K1_SEMANTIC_CONTRACT.md','SOURCE_EVENT_MAP.md']),
      'Y2':('DTC_LANE_Y2_K1_REQUAL_V1',['VALIDATION_GATE_V2.json','K0_EQUIVALENCE.md','LATEST_REPORT.md','supplement_r1/FULL_DIFF_REVIEW.json','supplement_r1/BUILD_IDENTITY.json','supplement_r1/ABI_RECEIPTS.json']),
      'Z2':('DTC_LANE_Z2_U_EVIDENCE_V1',['K1_INTERPRETATION_V2.md','FORMULA_VALIDATION.json','LATEST_REPORT.md']),
      'U':('DTC_T1C_HOLDOUT_V1',['LATEST_REPORT.md','FULL_MATRIX.tsv'])}
    provenance=[]
    for lane,(pack,names) in files.items():
        for name in names:provenance.append(copy_blob(FW_REPO,FROZEN[lane],'docs/dtc_l1/review_packs/'+pack+'/'+name,PACK/'inputs'/lane/name))
    for name in ['AUTHORITY_DECISION.md','LATEST_REPORT.md','DECISION.json','SOURCE_SHA256.tsv']:
        provenance.append(copy_blob(FW_REPO,'59a2bf0bfee404965ce56736333bbbf6b0d95259','docs/dtc_l1/review_packs/DTC_LANE_AB_OLD_DISPATCH_AUTHORITY_AUDIT_V1/'+name,PACK/'inputs/AB'/name))
    write(PACK/'INPUT_DOCUMENT_PROVENANCE.json',provenance)
    gate=json.loads((PACK/'inputs/Y2/VALIDATION_GATE_V2.json').read_text())
    assert gate['core_commit']==CANDIDATE_CORE if 'core_commit' in gate else CANDIDATE_CORE in json.dumps(gate)
    assert 'PASS_K1_OO_MODEL_SCOPE' in json.dumps(gate)
    identity=json.loads((PACK/'inputs/X/SOURCE_AND_BINARY_IDENTITY.json').read_text())
    artifacts=[]
    for a in identity['binaries']:
        assert sha(a['path'])==a['sha256'];artifacts.append(dict(**a,AA3_rehash='PASS'))
    spec0=json.loads((OLD/'specs/K0_32x4.json').read_text())
    env={'PATH':'/usr/bin:/bin','LANG':'C','LD_LIBRARY_PATH':str(Path(spec0['runtime_library_path']).parent)}
    ldd=subprocess.run(['/usr/bin/ldd',spec0['runtime_path']],env=env,capture_output=True,text=True)
    assert ldd.returncode==0 and spec0['runtime_library_path'] in ldd.stdout and 'not found' not in ldd.stdout
    write(ROOT/'LDD_CPU.json',dict(command=['/usr/bin/ldd',spec0['runtime_path']],environment=env,exit_code=ldd.returncode,stdout=ldd.stdout,stderr=ldd.stderr))
    write(PACK/'RUNTIME_IDENTITY.json',dict(artifacts=artifacts,loader_pin=env,ldd_receipt_sha256=sha(ROOT/'LDD_CPU.json'),actual_simulator_maps='UNAVAILABLE_NO_SIMULATOR_STARTED',build_Framework=spec0['build_Framework'],review_Framework=FROZEN['X'],current_orchestration_Framework='AA3_OWN_COMMIT_AT_DELIVERY'))
    # Exact immutable old Gaussian manifest, not the combined 511-member cohort.
    accepted=git_json(FW_REPO,T_SHA,T_PACK+'/inputs/Gaussian_OO128_SPEC.json')
    members=accepted['members'];assert len(members)==510
    listpath=Path(spec0['trace_list']);assert sha(listpath)==spec0['trace_list_sha256']
    before=time.monotonic();nbytes=0;checks=[]
    for m in members:
        p=Path(m['path']);h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):
                h.update(b);nbytes+=len(b)
                delay=nbytes/(32*1024**2)-(time.monotonic()-before)
                if delay>0:time.sleep(delay)
        assert p.stat().st_size==m['bytes'] and h.hexdigest()==m['sha256'],str(p)
        checks.append(dict(path=str(p),bytes=m['bytes'],sha256=h.hexdigest()))
    write(ROOT/'INPUT_MEMBER_REHASH.json',dict(utc=now(),members=checks,member_count=len(checks),bytes=nbytes,bandwidth_ceiling_MiB_s=32))
    ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text())
    assert len(ordered)==510 and sum(x['active_instructions'] for x in ordered)==283685120 and sum(x['complete_ctas'] for x in ordered)==65790
    assert [x['member_sha256'] for x in ordered]==[x['sha256'] for x in members]
    write(PACK/'INPUT_PREFLIGHT.json',dict(status='PASS_CPU_ORIGINAL_510_IDENTITIES',original_accepted_commit=T_SHA,original_spec_path=T_PACK+'/inputs/Gaussian_OO128_SPEC.json',Gaussian_member_count=510,combined_GEMM_plus_Gaussian_not_Gaussian=511,list_sha256=sha(listpath),ordered_kernel_sha256=sha(PACK/'ORDERED_KERNELS.json'),member_manifest_sha256=sha(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv'),rehash_receipt_sha256=sha(ROOT/'INPUT_MEMBER_REHASH.json'),active_instructions=283685120,complete_CTAs=65790,ROI='FULL_513_COMMAND_LIST_510_KERNELS',address_reuse_and_values='UNAVAILABLE_NOT_BODY_SCANNED'))
    # All existing receipt metadata; no full stdout/body scans and no old writes.
    examined=[];conflicts=[]
    uuids={r[1] for r in POINTS}
    roots=sorted(p for p in Path('/workspace').iterdir() if p.is_dir() and p.name.startswith(('dtc-','fast64-')))
    for root in roots:
        for directory,dirs,filenames in os.walk(root):
            dirs[:]=[n for n in dirs if not n.startswith(('.git','build','source','CMakeFiles')) and n not in ['__pycache__','binaries','lib','include']]
            for n in filenames:
                if n not in ['RUN_START.json','RUN_START.tsv','RUN_TERMINAL.json','RUN_TERMINAL.tsv','PID.json','RUN_MANIFEST.tsv']:continue
                p=Path(directory)/n
                if not p.is_file() or p.stat().st_size>1024**2:continue
                raw=p.read_bytes();record=dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw));examined.append(record)
                if any(u in str(p) or u.encode() in raw for u in uuids):conflicts.append(record)
    assert not conflicts,conflicts
    write(PACK/'UUID_START_CONFLICT_AUDIT.json',dict(utc=now(),roots=list(map(str,roots)),scope='all current DTC/FAST64 raw-root receipt metadata, visible original174 filesystem; no disconnected host claim',examined=examined,conflicts=conflicts,actual_AA_AA2_AA3_starts=0,maximum_total_actual_starts=4))
    # CPU parser probe from published independent Y2. Never run accel-sim.out.
    probe=ROOT/'options_cpu_probe';shutil.copy2('/workspace/dtc-lane-y2-k1-requal-174-v1/options_cpu_probe_final',probe)
    assert sha(probe)=='f9e84e74d37fa5fbbb03b67bc21d0daa6b9390a8cd4b89d3f0bbe0d8225c4437'
    def echo(txt):
        out={}
        for line in txt.splitlines():
            if re.match(r'^-[A-Za-z_]',line):
                p=line.split('#',1)[0].split(None,1)
                if len(p)==2:out[p[0]]=p[1].strip().split()
        return out
    records=[]
    defaults=subprocess.run([str(probe)],env=env,capture_output=True,text=True);assert defaults.returncode==0
    default_options=echo(defaults.stdout);assert len(default_options)==230 and default_options[K_OPTION]==['0']
    (ROOT/'CPU_OPTIONS_DEFAULTS.stdout').write_text(defaults.stdout)
    profiles={};rows=[]
    for point,uid,k,sets,ways,cal in POINTS:
        spec=json.loads((OLD/'specs'/f'{point}.json').read_text())
        expected=spec['expected_full_default_and_config_echo'];assert len(expected)==267
        for suffix,omit in [('explicit',False)]+([('omitted',True)] if k==0 else []):
            args=[str(probe)]
            for key,value in spec['expected_effective_options'].items():
                if key in default_options and not(omit and key==K_OPTION):args.extend([key,' '.join(value)])
            r=subprocess.run(args,env=env,capture_output=True,text=True);assert r.returncode==0
            actual=echo(r.stdout);assert len(actual)==230 and all(actual[n]==expected[n] for n in actual)
            p=ROOT/f'CPU_OPTIONS_{point}_{suffix}.stdout';p.write_text(r.stdout)
            records.append(dict(point=point,mode=suffix,argv=args,exit_code=r.returncode,sha256=sha(p),all_230_match=True,other_37_fields='SOURCE_BOUND_INHERITED_ACCEPTED_ECHO'))
        for cfg in spec['configs']:
            cfg['path']=str(PACK/'config'/Path(cfg['path']).name);assert sha(cfg['path'])==cfg['sha256']
        spec.update(status='STOP_AUTHORITY_NOT_EXECUTABLE_PREREGISTRATION',accepted_core=CANDIDATE_CORE,event_observer_contract='K1_ONLY_EVENT_TELEMETRY_ACCEPTED_AS_NONCOMPARATIVE_DIAGNOSTIC',Y2_published_commit=FROZEN['Y2'],global_AA_plus_AA2_plus_AA3_start_limit=4,production_runner_sha256='UNAVAILABLE_NOT_RELEASED_DUE_AUTHORITY_STOP',execution_guard_sha256=sha(PACK/'scripts/execution_guard.py'),full_execution_admitted=False,launch_admitted=False)
        write(PACK/'specs'/f'{point}.json',spec);profiles[point]=expected
        rows.append(dict(priority=spec['priority'],point=point,uuid=uid,K=k,tag_sets=sets,tag_ways=ways,spec_sha256=sha(PACK/'specs'/f'{point}.json'),Core=CANDIDATE_CORE,runtime_sha256=spec['runtime_sha256'],library_sha256=spec['runtime_library_sha256'],ordered_kernels=510,active_instructions=283685120,CTAs=65790,calibration_cycles=cal,timeout_seconds=7200,max_actual_starts=1,status='STOP_AUTHORITY_NOT_RELEASED',executable_preregistration=False))
    table(PACK/'PRE_REGISTRATION.tsv',rows)
    write(PACK/'CPU_OPTIONS_RECHECK.json',dict(default_OFF=True,Core_measured_option_count=230,full_profiles=267,records=records,omitted_equals_explicit_zero=True,actual_simulator_runs=0))
    deltas=[]
    for key in sorted(profiles['K0_32x4']):
        values=[profiles[p][key] for p,*_ in POINTS]
        if len({json.dumps(v) for v in values})>1:
            assert key in [K_OPTION,'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'],key
            deltas.append(dict(option=key,**{p:json.dumps(profiles[p][key]) for p,*_ in POINTS}))
    table(PACK/'CONTROLLED_DELTA.tsv',deltas)
    print('CPU-only fixed sources, inputs and option checks PASS; authority STOP, no new performance.')

if __name__=='__main__':main()
