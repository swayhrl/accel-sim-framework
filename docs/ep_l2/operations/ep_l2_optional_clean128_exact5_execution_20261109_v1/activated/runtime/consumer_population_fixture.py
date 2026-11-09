"""Bounded 64-slice ABI fixture; no model, budget, or acceptance writes."""
import copy
import json
import pathlib
import re
import tempfile

import exact5_consumer as consumer

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
CPU = pathlib.Path('/root/share/mnt164/huangrulin/ep_l2_next_cost_aware_20261107_v1/agent_a')
PREFIXES = ('EPL2TVDV2|SUMMARY|', 'EPL2TVDV3|METADATA_COST|',
            'EPL2TVDX1|SEGMENT|', 'EPL2TVDX1|CONTROL|')


def expect_rejected(fn, label):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('invalid evidence accepted: ' + label)


def raw_slice(mode):
    rows = [line for line in (CPU / f'CPU_FROZEN3D3887_mode{mode}.log').read_text().splitlines()
            if line.startswith(PREFIXES)]
    expected = 2 if mode == 0 else 4
    consumer.need(len(rows) == expected, 'CPU fixture record population drift')
    return rows


def population(mode):
    return [re.sub(r'\|slice=0(?=\||$)', f'|slice={sid}', line, count=1) + '\n'
            for sid in range(64) for line in raw_slice(mode)]


def main():
    shell = consumer.isolated(consumer.SHELL, 'exact5_fixture_shell', consumer.SHELL_SHA)
    abi = json.loads(consumer.ABI.read_bytes())
    checks = []
    with tempfile.TemporaryDirectory(prefix='ep_l2_exact5_abi_') as directory:
        raw = pathlib.Path(directory) / 'bounded.log'
        for mode in (0, 1, 2):
            rows = population(mode)
            raw.write_text('gpu_tot_sim_cycle = 17\n' + ''.join(rows))
            final, clock = consumer.final_cost_frame(raw)
            consumer.need(clock == 17 and len(final) == len(rows), 'final cost frame lost records')
            parsed = shell.validate_final_frame(final, mode, abi)
            consumer.need(len(parsed['rows']) == 64, '64-slice fixture not closed')
            checks.append(f'mode{mode}_64_slice_population')
            # A later native clock must replace the earlier cost frame.
            raw.write_text('gpu_tot_sim_cycle = 16\n' + ''.join(rows) +
                           'gpu_tot_sim_cycle = 17\n' + ''.join(rows))
            final, clock = consumer.final_cost_frame(raw)
            consumer.need(clock == 17 and len(final) == len(rows), 'final clock selection changed')
            shell.validate_final_frame(final, mode, abi)
            checks.append(f'mode{mode}_latest_clock')
            expect_rejected(lambda: shell.validate_final_frame(rows[:-1], mode, abi),
                            f'mode{mode}_missing_last_slice_record')
            if mode:
                corrupt = copy.copy(rows)
                segment_index = next(i for i, line in enumerate(corrupt)
                                     if line.startswith('EPL2TVDX1|SEGMENT|'))
                corrupt[segment_index] = re.sub(r'\|ext_live=\d+', '|ext_live=999',
                                                corrupt[segment_index], count=1)
                expect_rejected(lambda: shell.validate_final_frame(corrupt, mode, abi),
                                f'mode{mode}_bad_extension_capacity')
            raw.write_text('gpu_tot_sim_cycle = 17\n' + ''.join(rows) +
                           'gpu_tot_sim_cycle = 18\n' + ''.join(rows[:-1]))
            final, unused = consumer.final_cost_frame(raw)
            expect_rejected(lambda: shell.validate_final_frame(final, mode, abi),
                            f'mode{mode}_incomplete_later_clock')
    print(json.dumps({'status': 'BOUNDED_64_SLICE_ABI_FIXTURE_PASS', 'checks': checks,
                      'full_application_validated': False, 'models_started': False}, sort_keys=True))


if __name__ == '__main__':
    main()
