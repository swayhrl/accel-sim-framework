"""Strict normal-boundary cumulative snapshot parser; never sum snapshots."""
import json
import re
from pathlib import Path

SENTINEL = (1 << 64) - 1
BEGIN = 'DTC_INVALIDATE_V1_SNAPSHOT_BEGIN'
END = 'DTC_INVALIDATE_V1_SNAPSHOT_END'
ROW = 'DTC_INVALIDATE_V1_SUMMARY'
FIELDS = set(('sm requests idle membar config unspecified ordinary_commits changed '
              'retained_at_event reclaimed_at_event no_op_requests first_request_cycle '
              'last_request_cycle first_ordinary_commit_cycle last_ordinary_commit_cycle '
              'pending_first_request pending_last_request event_records_omitted').split())


def numbers(line, prefix, fields):
    if not line.startswith(prefix + ' '):
        raise ValueError('invalid record prefix')
    result = {}
    for token in line[len(prefix) + 1:].split():
        if not re.fullmatch(r'[a-z_]+=[0-9]+', token):
            raise ValueError('invalid/truncated unsigned field')
        key, value = token.split('=')
        if key in result:
            raise ValueError('duplicate field')
        result[key] = int(value)
        if result[key] > SENTINEL:
            raise ValueError('uint64 overflow')
    if result.keys() != fields:
        raise ValueError('missing or unknown fields')
    return result


def validate_row(row, cycle):
    req, commits = row['requests'], row['ordinary_commits']
    if sum(row[k] for k in ('idle', 'membar', 'config', 'unspecified')) != req:
        raise ValueError('source/request mismatch')
    if row['changed'] != row['retained_at_event'] + row['reclaimed_at_event']:
        raise ValueError('mapping transition mismatch')
    if row['no_op_requests'] > req or commits > req:
        raise ValueError('counter bound violation')
    for count, first, last in [
        (req, 'first_request_cycle', 'last_request_cycle'),
        (commits, 'first_ordinary_commit_cycle', 'last_ordinary_commit_cycle')]:
        if count == 0:
            if row[first] != SENTINEL or row[last] != SENTINEL:
                raise ValueError('missing explicit no-event sentinel')
        elif not (row[first] != SENTINEL and row[first] <= row[last] <= cycle):
            raise ValueError('invalid event cycle range')
    a, b = row['pending_first_request'], row['pending_last_request']
    if not (a == b == 0 or 1 <= a <= b <= req):
        raise ValueError('invalid pending request sequence range')
    if req == 0 and any(row[k] for k in (
        'changed', 'retained_at_event', 'reclaimed_at_event', 'no_op_requests',
        'pending_first_request', 'pending_last_request', 'event_records_omitted')):
        raise ValueError('nonzero no-event state')


def parse_normal_export(text, *, k1, sms=64):
    snapshots, current = [], None
    for line in text.splitlines():
        if line.startswith(BEGIN):
            if current is not None:
                raise ValueError('nested/truncated snapshot')
            meta = numbers(line, BEGIN, {'version', 'sms', 'cycle', 'no_event_cycle_sentinel'})
            if meta['version'] != 1 or meta['sms'] != sms or meta['no_event_cycle_sentinel'] != SENTINEL:
                raise ValueError('snapshot contract mismatch')
            current = {'cycle': meta['cycle'], 'rows': {}}
        elif line.startswith(ROW):
            if current is None:
                raise ValueError('unframed/private-path summary')
            row = numbers(line, ROW, FIELDS)
            if row['sm'] not in range(sms) or row['sm'] in current['rows']:
                raise ValueError('duplicate or out-of-range SM')
            validate_row(row, current['cycle'])
            current['rows'][row['sm']] = row
        elif line.startswith(END):
            if current is None:
                raise ValueError('end without begin')
            meta = numbers(line, END, {'version', 'sms', 'cycle'})
            if meta != {'version': 1, 'sms': sms, 'cycle': current['cycle']}:
                raise ValueError('end metadata mismatch')
            if set(current['rows']) != set(range(sms)):
                raise ValueError('missing SM or incomplete snapshot')
            snapshots.append(current)
            current = None
        elif current is not None:
            raise ValueError('interleaved/unknown record inside snapshot')
    if current is not None:
        raise ValueError('truncated snapshot: missing END')
    if snapshots and not text.endswith('\n'):
        raise ValueError('truncated final output line')
    if not k1:
        if snapshots:
            raise ValueError('K0 must not export K1 summaries')
        return {'available': False, 'reason': 'K0_EVENT_TELEMETRY_UNAVAILABLE', 'snapshots': 0}
    if not snapshots:
        raise ValueError('K1 normal export missing')
    # Last whole boundary: no summing and no mixing SMs from separate frames.
    final = snapshots[-1]
    return {'available': True, 'snapshots': len(snapshots), 'cycle': final['cycle'],
            'rows': [final['rows'][sm] for sm in range(sms)]}


if __name__ == '__main__':
    import argparse
    cli = argparse.ArgumentParser()
    cli.add_argument('path', type=Path)
    cli.add_argument('--k1', choices=('0', '1'), required=True)
    cli.add_argument('--sms', type=int, default=64)
    args = cli.parse_args()
    print(json.dumps(parse_normal_export(args.path.read_text(), k1=args.k1 == '1', sms=args.sms), indent=2))
