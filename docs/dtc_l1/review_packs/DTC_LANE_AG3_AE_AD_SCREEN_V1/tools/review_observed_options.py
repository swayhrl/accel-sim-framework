"""Inspect existing stdout only; no target execution and no strict promotion."""
from common import *
from strict_screen import echo


def main():
    rows=[]
    manifest=json.loads((PACK/'EXECUTABLE_PREREGISTRATION.json').read_text())
    for name in manifest['ordered_specs'][:2]:
        spec=json.loads((PACK/name).read_text());run=RAW/'attempts'/(spec['point']+'_'+spec['attempt_uuid'])
        output=run/'simulator.stdout';text=output.read_text();actual=echo(text)
        expected=spec['expected_full_effective_options']
        assert actual==expected
        core=spec['expected_embedded_core_version'] in text
        framework=spec['expected_embedded_framework_version'] in text
        assert core and framework
        strict=json.loads((run/'STRICT.json').read_text())
        rows.append(dict(point=spec['point'],attempt_uuid=spec['attempt_uuid'],stdout_sha256=sha(output),stderr_sha256=sha(run/'simulator.stderr'),effective_option_count=len(actual),actual_effective_options=actual,all_options_exact=True,expected_core_version=spec['expected_embedded_core_version'],expected_framework_version=spec['expected_embedded_framework_version'],embedded_versions_observed=True,strict_status_unchanged=strict['status'],performance_accepted_unchanged=strict['performance_accepted'],Gaussian_failure_not_overridden=True))
    write(PACK/'ACTUAL_OPTIONS_IDENTITY_REVIEW.json',dict(status='OBSERVED_OPTIONS_AND_EMBEDDED_BUILD_BINDING_ONLY',rows=rows,actual_lifecycle_authority_is_separate=True,no_new_target_start=True))
    print(json.dumps([dict(point=r['point'],options=r['effective_option_count'],match=r['all_options_exact'],strict=r['strict_status_unchanged']) for r in rows]))


if __name__=='__main__':main()
