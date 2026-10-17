"""Read all Core defaults/options using Y2's published CPU-only parser probe.

Copies the checked probe to AA2 and pins the exact X runtime library. This
program never executes accel-sim.out, initializes a GPU, or loads a trace.
Unmeasured runtime/Framework fields inherit the accepted echo with unchanged
registration source; classify_inherited_options.py binds their exact owners.
"""
from common import *


def echo(text):
    result={}
    for line in text.splitlines():
        if re.match(r'^-[A-Za-z_]',line):
            p=line.split('#',1)[0].split(None,1)
            if len(p)==2:result[p[0]]=p[1].strip().split()
    return result


def main():
    y=json.loads((PACK/'Y2_GATE_BINDING.json').read_text())
    assert y['accepted_PASS_K1_OO_MODEL_SCOPE'] and y['accepted_K0_equivalence']
    build=json.loads((PACK/'inputs/Y2/BUILD_RECEIPTS.json').read_text())
    binary=next(b for b in build['binaries'] if b['name']=='options_cpu_probe_final')
    assert sha(binary['path'])==binary['sha256']
    local=ROOT/'cpu_options_probe';shutil.copy2(binary['path'],local)
    assert sha(local)==binary['sha256']
    pub=json.loads((PACK/'PUBLISHED_BINDINGS.json').read_text())
    library=next(b for b in pub['candidate_artifacts'] if b['path'].endswith('libcudart.so'))
    assert sha(library['path'])==library['sha256']
    env={'PATH':'/usr/bin:/bin','LANG':'C','LD_LIBRARY_PATH':str(Path(library['path']).parent)}
    commands=[]
    def run(label,args):
        p=subprocess.run(args,capture_output=True,text=True,env=env,cwd=ROOT)
        (ROOT/(label+'.stdout')).write_text(p.stdout);(ROOT/(label+'.stderr')).write_text(p.stderr)
        commands.append(dict(label=label,argv=args,exit_code=p.returncode,
             stdout_sha256=sha(ROOT/(label+'.stdout')),stderr_sha256=sha(ROOT/(label+'.stderr'))))
        assert p.returncode==0,p.stderr
        return p.stdout
    ldd=run('cpu_options_ldd',['/usr/bin/ldd',str(local)])
    m=re.search(r'libcudart\.so\s+=>\s+(\S+)',ldd)
    assert m and Path(m[1]).resolve()==Path(library['path']).resolve()
    defaults=echo(run('cpu_options_defaults',[str(local)]))
    assert defaults[K_OPTION]==['0']
    table(PACK/'CORE_DEFAULT_OPTIONS_CPU.tsv',[dict(option=k,value=json.dumps(v)) for k,v in sorted(defaults.items())])
    assert git(FW_REPO,'rev-parse',T_SHA+':gpu-simulator')==pub['Framework_code_trees']['gpu-simulator']
    closure=[]
    outputs={}
    for name,uid,k,sets,ways,*_ in POINTS:
        spec=json.loads((PACK/'specs'/f'{name}.json').read_text())
        args=[str(local)]
        for key,value in spec['expected_effective_options'].items():
            if key in defaults:args.extend([key,' '.join(value)])
        actual=echo(run('cpu_options_'+name,args));outputs[name]=actual
        expected=spec['expected_full_default_and_config_echo']
        differences={key:dict(expected=expected.get(key),actual=actual.get(key))
                     for key in actual if actual.get(key)!=expected.get(key)}
        assert not differences,(name,differences)
        assert set(actual)==set(defaults)
        frame={key:expected[key] for key in expected.keys()-actual.keys()}
        combined={**actual,**frame}
        assert combined==expected
        table(PACK/'effective_options'/f'{name}.tsv',[
             dict(option=key,value=json.dumps(value),proof='EXACT_X_LIBRARY_CPU_PARSER' if key in actual else
                  'ACCEPTED_ECHO_INHERITED_RUNTIME_OR_FRAMEWORK_REGISTRATION_REQUIRES_OWNER_BINDING')
             for key,value in sorted(combined.items())])
        closure.append(dict(point=name,uuid=uid,Core_options_measured=len(actual),
                  runtime_and_Framework_fields_inherited=len(frame),total_effective_fields=len(combined),
                  profile_sha256=sha(PACK/'effective_options'/f'{name}.tsv'),differences=differences))
    spec=json.loads((PACK/'specs/K0_32x4.json').read_text())
    omitted=[str(local)]
    for key,value in spec['expected_effective_options'].items():
        if key in defaults and key!=K_OPTION:omitted.extend([key,' '.join(value)])
    assert echo(run('cpu_options_omitted_K0_32x4',omitted))==outputs['K0_32x4']
    source_provenance=copy_blob(FW_REPO,y['published_fetch_back_commit'],
        'docs/dtc_l1/review_packs/DTC_LANE_Y2_K1_REQUAL_V1/scripts/options_cpu_probe.cc',
        PACK/'inputs/Y2/options_cpu_probe.cc')
    write(PACK/'EFFECTIVE_OPTIONS_CLOSURE.json',dict(status='PASS_CPU_CORE_DEFAULT_AND_CONFIG_PROFILE_CLOSURE',
        source_Core=CANDIDATE_CORE,exact_X_library=library,probe_binary=binary,
        probe_source=source_provenance,environment=env,commands=commands,points=closure,
        omitted_K0_equals_explicit_zero=True,all_four_defaults_and_config_differences_only_K_and_Tag=True,
        inherited_defaults='REUSED_ACCEPTED_ECHO_RUNTIME_AND_FRAMEWORK; EXACT_REGISTRATION_OWNERS_IN_CLASSIFICATION_RECEIPT',
        actual_full_simulator_echo='NOT_RUN_REQUIRED_AGAIN_IN_FULL_RUN_STRICT',
        full_simulator_starts=0,no_GPU_initialization_or_trace_loading=True))
    print('Core default/config CPU profiles closed for four draft points; no full simulation started.')


if __name__=='__main__':main()
