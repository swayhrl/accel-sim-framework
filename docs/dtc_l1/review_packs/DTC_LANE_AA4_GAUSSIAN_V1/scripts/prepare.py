"""Frozen Git-only identity preparation; CPU parser only, no simulator invocation."""
from common import *
AA3='dab43027467d577291aabd6a5d2812d601219188';AA3P='docs/dtc_l1/review_packs/DTC_LANE_AA3_GAUSSIAN_V1'
FROZEN={'AA3':AA3,'Core':CANDIDATE_CORE,'X':'49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4','V':V_SHA,'Y2':'d085f98c10010d641ba4cfffa1f58fb8db3b56ee','Z2':'2b633a616dc59efb99973e94bdfa421e28c33fab','U':'16e56912cfd02f2311a1603a29415dee829fd495'}

def main():
    bindings=[]
    for lane,commit in FROZEN.items():
        repo=CORE_REPO if lane=='Core' else FW_REPO
        assert git(repo,'rev-parse','refs/aa4-bindings/'+lane)==commit
        bindings.append(dict(lane=lane,commit=commit,tree=git(repo,'rev-parse',commit+'^{tree}'),fetch_back_ref='refs/aa4-bindings/'+lane))
    zpath='docs/dtc_l1/review_packs/DTC_LANE_Z2_U_EVIDENCE_V1/K1_INTERPRETATION_V2.md'
    z=blob(FW_REPO,FROZEN['Z2'],zpath);assert z==blob(FW_REPO,'35ff4bc3660dc7653be5d9a3d5a166b610effcf9',zpath)
    write(PACK/'SOURCE_BINDINGS.json',dict(bindings=bindings,Z2_original_binding='35ff4bc3660dc7653be5d9a3d5a166b610effcf9',Z2_V2_blob=git(FW_REPO,'rev-parse',FROZEN['Z2']+':'+zpath),Z2_V2_sha256=hashlib.sha256(z).hexdigest()))
    paths=git(FW_REPO,'ls-tree','-r','--name-only',AA3,AA3P).splitlines()
    copied=[]
    for path in paths:
        rel=path[len(AA3P)+1:]
        if rel.startswith(('config/','effective_options/','inputs/X/','inputs/V/','inputs/Y2/','inputs/Z2/')) or rel in ['METRIC_DICTIONARY.tsv','ORDERED_KERNELS.json','GAUSSIAN_MEMBERS_SHA256.tsv','PHYSICAL_CONSERVATION_DELTA.md','COMPARISON_FORMULAS.md','CORE_SOURCE_DELTA.json','OPTION_ECHO_CLASSIFICATION.json']:
            dest=PACK/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob(FW_REPO,AA3,path));copied.append(dict(path=rel,source_commit=AA3,source_blob=git(FW_REPO,'rev-parse',AA3+':'+path),sha256=sha(dest)))
    write(PACK/'FROZEN_INPUT_DOCUMENTS.json',copied)
    gate=json.loads((PACK/'inputs/Y2/VALIDATION_GATE_V2.json').read_text());assert 'PASS_K1_OO_MODEL_SCOPE' in json.dumps(gate) and CANDIDATE_CORE in json.dumps(gate)
    identity=json.loads((PACK/'inputs/X/SOURCE_AND_BINARY_IDENTITY.json').read_text())
    runtime=ROOT/'immutable-runtime';runtime.mkdir(exist_ok=False)
    for record in identity['binaries']:
        if Path(record['path']).name not in ['accel-sim.out','libcudart.so']:continue
        assert sha(record['path'])==record['sha256'];dest=runtime/Path(record['path']).name;shutil.copy2(record['path'],dest);dest.chmod(0o555);assert sha(dest)==record['sha256']
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','LD_LIBRARY_PATH':str(runtime)}
    ldd=subprocess.run(['/usr/bin/ldd',str(runtime/'accel-sim.out')],env=env,capture_output=True,text=True);assert ldd.returncode==0 and 'not found' not in ldd.stdout and str(runtime/'libcudart.so') in ldd.stdout
    deps=[]
    for name in re.findall(r'(?:=>\s+)?(/[\w/+.\-]+)',ldd.stdout):
        p=Path(name)
        if p.is_file() and str(p) not in [r['path'] for r in deps]:deps.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    write(PACK/'EXACT_BINARY_AND_CONFIG_SHA.json',dict(Core=CANDIDATE_CORE,build_Framework='0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc',review_Framework=FROZEN['X'],executable=dict(path=str(runtime/'accel-sim.out'),sha256=sha(runtime/'accel-sim.out')),libcudart=dict(path=str(runtime/'libcudart.so'),sha256=sha(runtime/'libcudart.so')),environment=env,loader_dependencies=deps,ldd=ldd.stdout,actual_loaded_process_maps='MUST_VERIFY_FOR_EACH_ACTUAL_START'))
    # Reuse AA3's freshly verified member SHA evidence, with no post-hash mutation.
    accepted=git_json(FW_REPO,T_SHA,T_PACK+'/inputs/Gaussian_OO128_SPEC.json');members=accepted['members'];assert len(members)==510
    rehash_path=Path('/workspace/dtc-lane-aa3-gaussian-174-v1/INPUT_MEMBER_REHASH.json')
    rawmanifest=git_json(FW_REPO,AA3,AA3P+'/INPUT_PREFLIGHT.json');assert sha(rehash_path)==rawmanifest['rehash_receipt_sha256']
    receipt=json.loads(rehash_path.read_text());assert receipt['members']==[dict(path=m['path'],bytes=m['bytes'],sha256=m['sha256']) for m in members]
    epoch=datetime.fromisoformat(receipt['utc']).timestamp();memberstats=[]
    for m in members:
        st=Path(m['path']).stat();assert st.st_size==m['bytes'] and st.st_mtime<=epoch and st.st_ctime<=epoch
        memberstats.append(dict(**m,device=st.st_dev,inode=st.st_ino,mtime_ns=st.st_mtime_ns,ctime_ns=st.st_ctime_ns))
    write(PACK/'INPUT_STAT_IDENTITY.json',dict(status='PASS_AA3_MEMBER_SHA_REUSED_NO_POST_HASH_MUTATION',AA3_raw_rehash_receipt_sha256=sha(rehash_path),hash_time_utc=receipt['utc'],accepted_T_commit=T_SHA,members=memberstats,body_rescanned=False))
    ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text());assert len(ordered)==510 and sum(x['complete_ctas'] for x in ordered)==65790 and sum(x['active_instructions'] for x in ordered)==283685120
    oldspecs={p:git_json(FW_REPO,AA3,AA3P+'/specs/'+p+'.json') for p,*_ in POINTS}
    trace=oldspecs['K0_32x4']['trace_list'];assert sha(trace)=='6dc7caba6733657293e8c517467bac28890ae4eb97c732ffd245d7fd1c479fb9'
    commands=Path(trace).read_text().splitlines();assert len(commands)==513
    probe=ROOT/'options_cpu_probe';shutil.copy2('/workspace/dtc-lane-y2-k1-requal-174-v1/options_cpu_probe_final',probe);assert sha(probe)=='f9e84e74d37fa5fbbb03b67bc21d0daa6b9390a8cd4b89d3f0bbe0d8225c4437'
    def echo(text):
        out={}
        for line in text.splitlines():
            if re.match(r'^-[A-Za-z_]',line):
                a=line.split('#',1)[0].split(None,1)
                if len(a)==2:out[a[0]]=a[1].strip().split()
        return out
    defs=subprocess.run([str(probe)],env=env,capture_output=True,text=True);assert defs.returncode==0
    defaults=echo(defs.stdout);assert len(defaults)==230 and defaults[K_OPTION]==['0']
    cpu=[]
    for point,uid,k,sets,ways,cal in POINTS:
        s=oldspecs[point]
        for omit in ([False,True] if k==0 else [False]):
            args=[str(probe)]
            for key,value in s['expected_effective_options'].items():
                if key in defaults and not(omit and key==K_OPTION):args.extend([key,' '.join(value)])
            r=subprocess.run(args,env=env,capture_output=True,text=True);assert r.returncode==0
            actual=echo(r.stdout);assert len(actual)==230 and all(v==s['expected_full_default_and_config_echo'][key] for key,v in actual.items())
            dest=ROOT/f'CPU_OPTIONS_{point}_{"omitted" if omit else "explicit"}.stdout';dest.write_text(r.stdout);cpu.append(dict(point=point,omitted=omit,sha256=sha(dest),all230_match=True))
        for cfg in s['configs']:
            cfg['path']=str(PACK/'config'/Path(cfg['path']).name);assert sha(cfg['path'])==cfg['sha256']
        for key in ['production_runner_sha256','execution_guard_sha256','launch_admitted','full_execution_admitted','global_AA_plus_AA2_start_limit','global_AA_plus_AA2_plus_AA3_start_limit']:s.pop(key,None)
        s.update(status='CPU_DRAFT_STOP_TELEMETRY_NO_EXECUTABLE_RELEASE',lane='AA4',runtime_path=str(runtime/'accel-sim.out'),runtime_library_path=str(runtime/'libcudart.so'),Y2_published_commit=FROZEN['Y2'],max_AA_AA2_AA3_AA4_actual_starts=4,production_runner_sha256='UNAVAILABLE_SCIENTIFIC_STOP_BEFORE_RELEASE',strict_collector_sha256='UNAVAILABLE_SCIENTIFIC_STOP_BEFORE_RELEASE',execution_guard_sha256=sha(PACK/'scripts/run_matrix.py'),strict_guard_sha256=sha(PACK/'scripts/strict.py'),runtime_environment=env,member_stat_identity_sha256=sha(PACK/'INPUT_STAT_IDENTITY.json'),observer_supplement_commit=AA3,observer_supplement_sha256=sha(PACK/'inputs/AA3/OBSERVER_SUPPLEMENT_V1.md'),source_event_metric_dictionary_sha256=sha(PACK/'METRIC_DICTIONARY.tsv'))
        write(PACK/'specs'/f'{point}.json',s)
    write(PACK/'CPU_OPTIONS_CHECK.json',dict(default_OFF=True,Core_options_measured=230,full_effective_profile_count=267,inherited_other37='FROZEN_AA3_SOURCE_OWNERSHIP_PROOF',omitted_K0_equals_explicit0=True,records=cpu,simulator_starts=0))
    table(PACK/'PRE_REGISTRATION.tsv',[dict(order=i,point=point,uuid=uid,K=k,sets=sets,ways=ways,spec_sha256=sha(PACK/'specs'/f'{point}.json'),calibration_cycles=cal,timeout_seconds=7200,actual_start_limit=1,runner_sha256='UNAVAILABLE_NOT_RELEASED',strict_sha256='UNAVAILABLE_NOT_RELEASED',status='STOP_TELEMETRY_NOT_EXECUTABLE_REGISTRATION') for i,(point,uid,k,sets,ways,cal) in enumerate(POINTS,1)])
    expected=[oldspecs[p]['expected_full_default_and_config_echo'] for p,*_ in POINTS]
    deltas=[]
    for key in expected[0]:
        if len({json.dumps(e[key]) for e in expected})>1:
            assert key in [K_OPTION,'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'];deltas.append(dict(option=key,**{p:json.dumps(e[key]) for (p,*_),e in zip(POINTS,expected)}))
    assert len(deltas)==3;table(PACK/'CONTROLLED_DELTA.tsv',deltas)
    print('PASS CPU-only: fixed fetch-back, actual unique runtime/dependencies, AA3 unchanged 510 member identities,267 options and four identified CPU draft specs. Scientific telemetry STOP, no production runner or simulation released.')

if __name__=='__main__':main()
