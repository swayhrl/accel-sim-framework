"""Separate real options from old trace headers; bind inherited registration owners.

An uncommitted pre-performance draft correction, with original draft evidence
archived. No old AA/T evidence, input, config, library or runtime is changed.
"""
from common import *
from close_options_cpu import echo


def save_json(p,data):
    Path(p).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')


def main():
    metadata={'-binary','-block','-cuda','-grid','-kernel','-nregs','-shmem'}
    old=json.loads((PACK/'EFFECTIVE_OPTIONS_CLOSURE.json').read_text())
    write(ROOT/'INITIAL_OPTION_PROFILE_BEFORE_CLASSIFICATION.json',old)
    sources=[];runtime_text=''
    for path in ['src/cuda-sim/cuda-sim.cc','src/cuda-sim/ptx_loader.cc','src/gpgpu-sim/icnt_wrapper.cc']:
        candidate=blob(CORE_REPO,CANDIDATE_CORE,path);original=blob(CORE_REPO,BASE_CORE,path)
        assert candidate==original
        runtime_text+=candidate.decode()
        sources.append(dict(scope='CORE_RUNTIME_REGISTRATION',path=path,candidate_Core=CANDIDATE_CORE,
            frozen_Core=BASE_CORE,byte_identical=True,sha256=hashlib.sha256(candidate).hexdigest()))
    fwbuild=json.loads((PACK/'PUBLISHED_BINDINGS.json').read_text())['Framework_build_source']
    frame_text=''
    for path in ['gpu-simulator/accel-sim.cc','gpu-simulator/trace-driven/trace_driven.cc']:
        new=blob(FW_REPO,fwbuild,path);accepted=blob(FW_REPO,T_SHA,path);assert new==accepted
        frame_text+=new.decode()
        sources.append(dict(scope='FRAMEWORK_TRACE_REGISTRATION',path=path,
            build_Framework=fwbuild,accepted_T_commit=T_SHA,byte_identical=True,
            sha256=hashlib.sha256(new).hexdigest()))
    closures=[];removed=[];plans=list(csv.DictReader((PACK/'PRE_REGISTRATION.tsv').open(),delimiter='\t'))
    for point in POINTS:
        name=point[0];specpath=PACK/'specs'/f'{name}.json'
        spec=json.loads(specpath.read_text());profile=spec['expected_full_default_and_config_echo']
        removed.append(dict(point=name,removed_trace_metadata={k:profile[k] for k in metadata if k in profile}))
        profile={k:v for k,v in profile.items() if k not in metadata}
        spec['expected_full_default_and_config_echo']=profile
        spec['trace_header_metadata_is_not_runtime_options']=sorted(metadata)
        save_json(specpath,spec)
        actual=echo((ROOT/('cpu_options_'+name+'.stdout')).read_text())
        assert all(profile[k]==v for k,v in actual.items())
        rows=[];counts={'CORE_CPU_PARSER':0,'CORE_RUNTIME_INHERITED':0,'FRAMEWORK_TRACE_INHERITED':0}
        for key,value in sorted(profile.items()):
            if key in actual:
                owner='CORE_CPU_PARSER';proof='EXACT_X_LIBRARY_ACTUAL_CPU_PARSER_ECHO'
            elif key.startswith('-trace'):
                assert key=='-trace' or key.startswith('-trace_opcode_latency_initiation_')
                owner='FRAMEWORK_TRACE_INHERITED';proof='ACCEPTED_ECHO_PLUS_BYTE_IDENTICAL_FRAMEWORK_TRACE_REGISTRATION'
            else:
                assert key in runtime_text,key
                owner='CORE_RUNTIME_INHERITED';proof='ACCEPTED_ECHO_PLUS_BYTE_IDENTICAL_CORE_RUNTIME_REGISTRATION'
            counts[owner]+=1
            rows.append(dict(option=key,value=json.dumps(value),owner=owner,proof=proof))
        with (PACK/'effective_options'/f'{name}.tsv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
        closures.append(dict(point=name,total_actual_options=len(rows),counts=counts,
               profile_sha256=sha(PACK/'effective_options'/f'{name}.tsv'),trace_headers_excluded=True))
        for row in plans:
            if row['point']==name:row['spec_sha256']=sha(specpath)
    with (PACK/'PRE_REGISTRATION.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(plans[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(plans)
    old['points']=closures
    old['inherited_registration_owners']=sources
    old['inherited_defaults']='CORE_RUNTIME_AND_FRAMEWORK_SEPARATELY_BOUND_TO_BYTE_IDENTICAL_REGISTRATION_SOURCE'
    old.pop('Framework_only_defaults',None)
    old['trace_metadata_excluded']=sorted(metadata)
    old['initial_draft_archive_sha256']=sha(ROOT/'INITIAL_OPTION_PROFILE_BEFORE_CLASSIFICATION.json')
    old['status']='PASS_CPU_OPTIONS_CLOSED_WITH_SOURCE_BOUND_INHERITED_REGISTRATION'
    save_json(PACK/'EFFECTIVE_OPTIONS_CLOSURE.json',old)
    write(PACK/'OPTION_ECHO_CLASSIFICATION.json',dict(utc=now(),status='PASS_PRE_PERFORMANCE_METADATA_AND_REGISTRATION_CLASSIFICATION',
         legacy_template_provenance=T_SHA,legacy_parser_issue='Broad leading-hyphen matching also captured7 trace header keys',
         removed_metadata=removed,registration_sources=sources,
         original_AA_and_T_files_changed=False,configs_or_runtime_changed=False,
         simulator_starts=0,UUIDs_changed=False,profiles=closures))
    print('Corrected option classification:',closures[0]['counts'],'total',closures[0]['total_actual_options'])


if __name__=='__main__':main()
