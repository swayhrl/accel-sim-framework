"""Strict OPT-COLLECT V1 normal snapshot parser; no workload-terminal claim."""
import re
from pathlib import Path

PREFIX = 'DTC_COLLECT_WB_V1_'
U64 = (1 << 64) - 1
FIELDS = set(('sm samples first_cycle last_cycle eligible_ready_sum eligible_ready_cycles '
 'collect_idle_eligible_cycles overlap_cycles result_occupancy_samples '
 'collecting_occupancy_samples result_backpressure_cycles wb_arbitration_blocked_cycles '
 'wb_attempts wb_denied_attempts collected_sectors retires cacheable_retires sidecar_retires '
 'collecting_valid result_valid collecting_uid result_uid buffered_sectors '
 'peak_buffered_sectors bank_capacity_bytes total_buffer_capacity_bytes '
 'sector_cycles_0 sector_cycles_1 sector_cycles_2 sector_cycles_3 sector_cycles_4 '
 'retire_cycles_0 retire_cycles_1 last_cycle_sectors last_cycle_retires').split())
FRAME = re.compile(r'DTC_COLLECT_WB_V1_SNAPSHOT_(BEGIN|END) version=1 sms=(\d+) cycle=(\d+)')


def parse(text, *, enabled=True, sms=64, require_drained=True):
    if not text.endswith('\n'):
        raise ValueError('truncated final line')
    if not enabled:
        if PREFIX in text:
            raise ValueError('OFF exported pipeline telemetry')
        return {'status': 'UNAVAILABLE_OFF', 'snapshots': 0, 'rows': None}
    current = None
    frames = []
    for line in text.splitlines():
        if not line.startswith(PREFIX):
            if current is not None:
                raise ValueError('interleaved or damaged row')
            continue
        match = FRAME.fullmatch(line)
        if match:
            kind, population, cycle = match.groups()
            population, cycle = int(population), int(cycle)
            if population != sms or cycle > U64:
                raise ValueError('population/cycle outside contract')
            if kind == 'BEGIN':
                if current is not None:
                    raise ValueError('nested begin')
                if frames and cycle < frames[-1]['cycle']:
                    raise ValueError('snapshot clock regressed')
                current = {'cycle': cycle, 'rows': {}}
            else:
                if current is None or current['cycle'] != cycle:
                    raise ValueError('unmatched end')
                if set(current['rows']) != set(range(sms)):
                    raise ValueError('missing SM')
                frames.append(current)
                current = None
            continue
        if not line.startswith(PREFIX + 'SUMMARY ') or current is None:
            raise ValueError('unframed/unknown export')
        row = {}
        for field in line.split()[1:]:
            if not re.fullmatch(r'[a-z_0-9]+=\d+', field):
                raise ValueError('malformed field')
            key, value = field.split('=')
            if key in row or int(value) > U64:
                raise ValueError('duplicate/oversize field')
            row[key] = int(value)
        if set(row) != FIELDS:
            raise ValueError('missing/extra field')
        sm = row['sm']
        if sm not in range(sms) or sm in current['rows']:
            raise ValueError('invalid/duplicate SM')
        n = row['samples']
        if n:
            if not 0 <= row['first_cycle'] <= row['last_cycle'] <= current['cycle']:
                raise ValueError('sample clock range')
        elif row['first_cycle'] != U64 or row['last_cycle'] != U64:
            raise ValueError('no-sample sentinel')
        if sum(row[f'sector_cycles_{i}'] for i in range(5)) != n:
            raise ValueError('sector sample conservation')
        if sum(i * row[f'sector_cycles_{i}'] for i in range(5)) != row['collected_sectors']:
            raise ValueError('sector flow conservation')
        if row['retire_cycles_0'] + row['retire_cycles_1'] != n or row['retire_cycles_1'] != row['retires']:
            raise ValueError('retire quota/bin conservation')
        if row['retires'] != row['cacheable_retires'] + row['sidecar_retires']:
            raise ValueError('retire class conservation')
        if row['wb_attempts'] != row['wb_denied_attempts'] + row['cacheable_retires']:
            raise ValueError('WB grant/denial conservation')
        for key in ['eligible_ready_cycles', 'collect_idle_eligible_cycles', 'overlap_cycles',
                    'result_occupancy_samples', 'collecting_occupancy_samples',
                    'result_backpressure_cycles', 'wb_arbitration_blocked_cycles', 'wb_attempts']:
            if row[key] > n:
                raise ValueError('cycle or attempt count exceeds samples')
        if row['overlap_cycles'] > row['cacheable_retires']:
            raise ValueError('overlap lacks retirement')
        if row['last_cycle_sectors'] > 4 or row['last_cycle_retires'] > 1:
            raise ValueError('absolute cycle quota exceeded')
        if row['bank_capacity_bytes'] == 0 or row['bank_capacity_bytes'] % 128 or row['total_buffer_capacity_bytes'] != 2 * row['bank_capacity_bytes']:
            raise ValueError('finite bank capacity contract')
        if row['buffered_sectors'] * 32 > row['total_buffer_capacity_bytes'] or row['peak_buffered_sectors'] * 32 > row['total_buffer_capacity_bytes']:
            raise ValueError('data bank capacity exceeded')
        for stage in ['collecting', 'result']:
            if row[stage + '_valid'] not in (0, 1) or bool(row[stage + '_uid']) != bool(row[stage + '_valid']):
                raise ValueError('stage owner validity')
        if row['result_valid'] and row['collecting_uid'] == row['result_uid']:
            raise ValueError('same owner in both stages')
        current['rows'][sm] = row
    if current is not None or not frames:
        raise ValueError('missing/truncated final export; no fallback')
    last = frames[-1]
    if require_drained and any(r['collecting_valid'] or r['result_valid'] or r['buffered_sectors'] for r in last['rows'].values()):
        raise ValueError('last export is not stage drained')
    return {'status': 'PASS_LAST_WHOLE_SNAPSHOT_ONLY', 'snapshots': len(frames),
            'cycle': last['cycle'], 'rows': last['rows'], 'summed_snapshots': False}


if __name__ == '__main__':
    import argparse, json
    p = argparse.ArgumentParser(); p.add_argument('log', type=Path)
    p.add_argument('--sms', type=int, default=64); p.add_argument('--off', action='store_true')
    a = p.parse_args(); print(json.dumps(parse(a.log.read_text(), enabled=not a.off, sms=a.sms), indent=2))
