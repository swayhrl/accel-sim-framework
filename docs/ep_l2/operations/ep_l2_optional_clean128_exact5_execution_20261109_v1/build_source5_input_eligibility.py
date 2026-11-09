"""Join existing input evidence to Source5 engineering evidence, without a model run."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
SOURCE_Q = ROOT / 'documents/SOURCE_CPU_QUALIFICATION.json'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def checked(ref):
    need(sha(ref['path']) == ref['sha256'], 'input evidence reference drift')
    return json.loads(pathlib.Path(ref['path']).read_bytes())


def main():
    specs = [json.loads(path.read_bytes()) for path in sorted(ROOT.glob('cases/*/control/DRAFT_SPEC.json'))]
    need(len(specs) == 5, 'expected five drafts')
    sourceq = json.loads(SOURCE_Q.read_bytes())
    source = sourceq['source_identity']
    need(sourceq['status'] == 'PRODUCTION_CPU_BUILD_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED'
         and sourceq['application_acceptance_granted'] is False, 'Source5 engineering scope')
    groups = {}
    for spec in specs:
        program = spec['program']
        need(spec['source_identity'] == source and spec['mode'] == 'WV_ZERO_RO', 'draft Source or mode')
        binding = checked(spec['input_binding_ref'])
        historical = checked(spec['eligibility_ref'])
        need(binding['input_identity_sha256'] == historical['input_identity_sha256'] ==
             spec['input_identity_sha256'], 'input identity differs')
        need(binding['ordered_kernel_identity'] == historical['ordered_kernel_identity'],
             'kernel identity differs')
        need(historical['source_identity'] != source and
             historical['status'] == 'MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE',
             'historical input evidence scope changed')
        need(program == historical['program'] and 'WV_ZERO_RO' in historical['modes_qualified'],
             'historical input mode/program changed')
        row = {'schema': 'EP_L2_EXACT5_SOURCE5_INPUT_ELIGIBILITY_V1',
               'status': 'ENGINEERING_COMPLETE_INPUT_IDENTITY_ELIGIBLE_NOT_APP_ACCEPTED',
               'source_identity': source, 'source_qualification_ref':
                   {'path': str(SOURCE_Q), 'sha256': sha(SOURCE_Q)},
               'input_identity_sha256': spec['input_identity_sha256'],
               'input_binding_ref': spec['input_binding_ref'],
               'historical_input_only_ref': spec['eligibility_ref'],
               'historical_source_qualification_inherited': False,
               'old_application_acceptance_inherited': False,
               'ordered_kernel_identity': binding['ordered_kernel_identity'],
               'modes_qualified': ['WV_ZERO_RO'], 'program': program,
               'application_acceptance_granted': False}
        if program in groups:
            need(groups[program] == row, 'same program has different input/Source evidence')
        else:
            groups[program] = row
    need(set(groups) == {'GEMM', 'stencil'}, 'two program families required')
    for program, row in groups.items():
        path = ROOT / 'documents' / (f'SOURCE5_INPUT_ELIGIBILITY_{program.upper()}.json')
        with path.open('xb') as stream:
            stream.write((json.dumps(row, sort_keys=True, indent=2) + '\n').encode())
    print(json.dumps({'status': 'SOURCE5_INPUT_IDENTITY_ENGINEERING_JOIN_PASS_NO_LAUNCH',
                      'programs': sorted(groups), 'models_started': False}, sort_keys=True))


if __name__ == '__main__':
    main()
