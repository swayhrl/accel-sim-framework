"""Small read-only checks for the Source5 consumer before formal Host binding."""
import json
import pathlib
import copy

import exact5_consumer as consumer

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
CPU = pathlib.Path('/root/share/mnt164/huangrulin/ep_l2_next_cost_aware_20261107_v1/agent_a')


def actual_cpu_slice(shell, mode):
    path = CPU / f'CPU_FROZEN3D3887_mode{mode}.log'
    records = {}
    for line in path.read_text().splitlines():
        if line.startswith(('EPL2TVDV2|SUMMARY|', 'EPL2TVDV3|METADATA_COST|',
                            'EPL2TVDX1|SEGMENT|', 'EPL2TVDX1|CONTROL|')):
            kind, row = shell.parse_line(line)
            shell.need(row['slice'] == 0 and kind not in records,
                       'actual bounded CPU record population changed')
            records[kind] = row
    expected = {('EPL2TVDV2', 'SUMMARY'), ('EPL2TVDV3', 'METADATA_COST')}
    if mode:
        expected |= {('EPL2TVDX1', 'SEGMENT'), ('EPL2TVDX1', 'CONTROL')}
    shell.need(set(records) == expected, 'actual bounded CPU kinds changed')
    row = shell.validate_slice(records['EPL2TVDV2', 'SUMMARY'],
                               records['EPL2TVDV3', 'METADATA_COST'],
                               records.get(('EPL2TVDX1', 'SEGMENT')),
                               records.get(('EPL2TVDX1', 'CONTROL')), mode)
    return records, row


def main():
    frozen = consumer.isolated(consumer.FROZEN, 'exact5_preflight_frozen', consumer.FROZEN_SHA)
    shell = consumer.isolated(consumer.SHELL, 'exact5_preflight_shell', consumer.SHELL_SHA)
    abi = json.loads(consumer.ABI.read_bytes())
    parse, receipt = frozen.numeric_math()
    consumer.need(callable(parse) and receipt['numeric_body_sha256'] == abi['old_math_body_sha256'],
                  'frozen numeric math changed')
    consumer.need(callable(consumer.adapted_scan(frozen)), 'scanner not compilable')
    points = []
    for path in sorted(ROOT.glob('cases/*/control/DRAFT_SPEC.json')):
        s = json.loads(path.read_bytes())
        consumer.need(s['source_identity'] == consumer.SOURCE5, 'draft Source drift')
        consumer.need(len(s['expected_effective_options']) == 283, 'draft options count')
        frozen.history_for(s)
        points.append(s['proposal_point_id'])
    consumer.need(len(points) == 5 and len(set(points)) == 5, 'five unique drafts required')
    sourceq = json.loads((ROOT / 'documents/SOURCE_CPU_QUALIFICATION.json').read_bytes())
    consumer.need(sourceq['source_identity'] == consumer.SOURCE5 and
                  sourceq['status'] == 'PRODUCTION_CPU_BUILD_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED' and
                  sourceq['application_acceptance_granted'] is False,
                  'Source qualification scope changed')
    for ref in sourceq['evidence_refs'].values():
        consumer.need(consumer.sha(ref['path']) == ref['sha256'], 'Source evidence drift')
    cpu_rows = []
    for mode in (0, 1, 2):
        records, row = actual_cpu_slice(shell, mode)
        cpu_rows.append({'mode': mode, 'role_tvd_global': row['role_tvd_global'],
                         'base_live': row['base_raw_summary']['live'],
                         'extension_live': (row['extension_raw_segment'] or {}).get('ext_live', 0)})
    records, unused = actual_cpu_slice(shell, 2)
    corrupt = copy.deepcopy(records['EPL2TVDV2', 'SUMMARY'])
    corrupt['role_tvd'] -= 1
    try:
        shell.validate_slice(corrupt, records['EPL2TVDV3', 'METADATA_COST'],
                             records['EPL2TVDX1', 'SEGMENT'],
                             records['EPL2TVDX1', 'CONTROL'], 2)
    except ValueError:
        pass
    else:
        raise AssertionError('mutated Base/Ext role join accepted')
    # One-slice CPU fixtures check the actual Source5 ABI and a counterexample.
    # They do not substitute for any whole-application record population.
    print(json.dumps({'status': 'READ_ONLY_CONSUMER_COMPONENT_PREFLIGHT_PASS',
                      'draft_points': points,
                      'bounded_cpu_rows': cpu_rows,
                      'numeric_body_sha256': receipt['numeric_body_sha256'],
                      'whole_application_validated': False,
                      'budget_registered': False,
                      'models_started': False}, sort_keys=True))


if __name__ == '__main__':
    main()
