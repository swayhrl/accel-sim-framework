"""Create reviewable Source5 Spec candidates; never grants release or starts models."""
import copy
import hashlib
import json
import pathlib

import exact5_mode_contract as contract

ROOT = contract.ROOT


def ref(path):
    return {'path': str(path), 'sha256': contract.sha(path)}


def main():
    files = sorted(ROOT.glob('cases/*/control/DRAFT_SPEC.json'))
    contract.need(len(files) == 5, 'five drafts required')
    results = []
    for path in files:
        draft = contract.read(path)
        contract.validate_static(draft, candidate=True)
        spec = copy.deepcopy(draft)
        inputq = ROOT / 'documents' / ('SOURCE5_INPUT_ELIGIBILITY_' +
                                       spec['program'].upper() + '.json')
        spec['source_qualification_ref'] = ref(contract.SOURCE_Q)
        spec['eligibility_ref'] = ref(inputq)
        spec['mode_contract_ref'] = ref(ROOT / 'runtime/exact5_mode_contract.py')
        spec['validation_module_ref'] = ref(ROOT / 'runtime/exact5_consumer.py')
        spec['scientific_option_contract'].pop('complete_282', None)
        spec['scientific_option_contract']['complete_283'] = True
        spec['scientific_option_contract']['CPU_mode_qualification_ref'] = ref(contract.SOURCE_Q)
        spec['status'] = 'SOURCE5_BOUND_CANDIDATE_HOST_NATIVE_UNBOUND_NO_LAUNCH'
        spec['launch_permission'] = False
        spec['scientific_launch_permission'] = False
        spec['scientific_scope_activated'] = False
        contract.validate_static(spec)
        target = path.with_name('BOUND_SPEC_CANDIDATE.json')
        with target.open('xb') as stream:
            stream.write((json.dumps(spec, sort_keys=True, indent=2) + '\n').encode())
        results.append({'point_id': spec['proposal_point_id'], 'cohort': spec['cohort'],
                        'candidate_ref': ref(target), 'host_bound': False,
                        'Native_route_installed': False})
    print(json.dumps({'status': 'FIVE_SOURCE5_BOUND_CANDIDATES_NO_RELEASE',
                      'points': results, 'models_started': False}, sort_keys=True))


if __name__ == '__main__':
    main()
