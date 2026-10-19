"""Read retained logs and test an E-only parser proposal; never accepts an app."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a = p.parse_args()
    spec = json.loads(a.spec.read_text())
    for path,digest in spec['control_bindings'].items():
        assert sha(path)==digest
    old = module(spec['old_function'],'original_E_runtime_metrics')
    new = module(spec['new_function'],'proposed_E_runtime_metrics')
    expected = json.loads(Path(spec['S_input_spec']).read_text())['profile_semantics']['effective_options']
    rows = []
    try:
        old.runtime_metrics(spec['S_raw'],expected)
    except ValueError as error:
        assert 'effective native L2' in str(error)
        rows.append(dict(case='REAL_RETAINED_S_OLD_RED',expected_rejection=True,error=str(error)))
    else:
        raise AssertionError('actual original Efunction did not reproduce parser failure')
    parsed = new.runtime_metrics(spec['S_raw'],expected)
    assert parsed == {'cycle':292932,'insn':714547200}
    rows.append(dict(case='REAL_RETAINED_S_NEW_GREEN',metrics=parsed,control_only=True))
    failed_expected=json.loads(Path(spec['F_input_spec']).read_text())['profile_semantics']['effective_options']
    try:
        new.runtime_metrics(spec['F_raw'],failed_expected)
    except ValueError as error:
        assert 'native exit/counters' in str(error)
        rows.append(dict(case='REAL_CRASHED_F_REMAINS_REJECTED',expected_rejection=True,error=str(error)))
    else:
        raise AssertionError('crashed application log accepted')
    ep='-gpgpu_ep_l2_ft_mode'
    geo='-gpgpu_cache:dl2'
    geometry='S:64:128:16,L:B:m:L:P,A:128:1,128:0,32'
    end='gpu_tot_sim_cycle = 100\ngpu_tot_sim_insn = 10\nGPGPU-Sim: *** exit detected ***\n'
    cases=[
        ('plain_dump',f'{ep} 1\n',{ep:'1'},True),
        ('comments_and_colon_geometry',f'{ep} 1 # FT mode\n{geo} {geometry} # L2 geometry\n',{ep:'1',geo:geometry},True),
        ('wrong_research_value',f'{ep} 2 # FT mode\n',{ep:'1'},False),
        ('wrong_geometry',f'{ep} 1 # FT mode\n{geo} S:1:128:1 # invalid geometry\n',{ep:'1',geo:geometry},False),
        ('missing_geometry',f'{ep} 1 # FT mode\n',{ep:'1',geo:geometry},False),
        ('missing_research_option',f'{geo} {geometry} # L2 geometry\n',{ep:'1',geo:geometry},False),
        ('conflicting_duplicate',f'{ep} 2 # first\n{ep} 1 # second\n',{ep:'1'},False),
        ('identical_duplicate',f'{ep} 1 # first\n{ep} 1 # second\n',{ep:'1'},True),
        ('literal_hash_path','-gpgpu_ep_l2_ro_manifest /some/input#name # file\n',{'-gpgpu_ep_l2_ro_manifest':'/some/input#name'},True),
        ('literal_space_hash_path','-gpgpu_ep_l2_ro_manifest /some/input # name # file\n',{'-gpgpu_ep_l2_ro_manifest':'/some/input # name'},True)]
    for name,text,opts,ok in cases:
        raw = a.out.parent/(name+'.control.log')
        assert not raw.exists()
        raw.write_text(text+end)
        try:
            got = new.runtime_metrics(raw,opts)
        except ValueError as error:
            assert not ok,(name,error)
            row=dict(case=name,expected_rejection=True,error=str(error))
        else:
            assert ok and got=={'cycle':100,'insn':10},name
            row=dict(case=name,expected_acceptance_of_control_syntax=True)
        row.update(control_log=str(raw),sha256=sha(raw))
        rows.append(row)
    for path,digest in spec['control_bindings'].items():
        assert sha(path)==digest
    result=dict(status='PROPOSED_E_PARSER_CONTROLS_PASS_NOT_APPLICATION_ACCEPTANCE',
        old_E_function_is_verbatim=True,actual_retained_old_red=True,
        proposed_parser_real_log_green=True,controls=len(rows),cases=rows,
        live_E_source_edited=False,central_science_ledger_edited=False,
        accepted_application_result=False,new_simulator_executions=0,
        retained_logs_and_status_unchanged=True,
        warning='E alone must publish/rebind/review. Old67fd source qualifications remain held; no old result reinstated or crossbinary pairing.')
    assert not a.out.exists()
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],len(rows))


if __name__=='__main__':
    main()
