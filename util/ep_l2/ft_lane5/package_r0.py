"""Publish immutable compact review packs from completed R0 pairs; no simulations."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
from datetime import datetime, timezone

from registry import Registry, write_json

REPO = Path(__file__).resolve().parents[3]


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_checksums(pack):
    (pack / 'SHA256SUMS').write_text(''.join(checksum(p) + '  ' + str(p.relative_to(pack)) + '\n'
        for p in sorted(pack.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS'))


def package_pair(source):
    receipt = json.loads((source / 'PAIR_RECEIPT.json').read_text())
    if receipt['status'] != 'COMPLETE_VALID':
        return None
    workload = receipt['workload']
    pack = REPO / 'docs/ep_l2/review_packs' / ('FT20261016_LANE5_R0_' + workload.upper() + '_PAIR_r1')
    if pack.exists():
        # Never rewrite a frozen pair, even if an upstream collector later changes.
        for line in (pack / 'SHA256SUMS').read_text().splitlines():
            expected, name = line.split('  ', 1)
            if checksum(pack / name) != expected:
                raise ValueError('frozen pack changed: ' + str(pack))
        return pack
    pack.mkdir()
    for path in source.iterdir():
        if path.is_file():
            shutil.copyfile(path, pack / path.name)
    rows = list(csv.DictReader((source / 'RESULTS.csv').open()))
    for filename, row in zip(('BASELINE_RESULTS.csv', 'MECHANISM_RESULTS.csv'), rows):
        with (pack / filename).open('x', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=list(row), lineterminator='\n')
            writer.writeheader()
            writer.writerow(row)
    manifests = []
    raw_index = []
    for row in rows:
        directory = Path('/workspace/results/ep_l2_ft20261016') / row['run_key']
        manifests.append({'mode': row['mode'], 'run_key': row['run_key'],
            'identity': json.loads((directory / 'input_spec.json').read_text())['identity'],
            'input_audit': json.loads((directory / 'input_audit.json').read_text()),
            'hardware_terminal': json.loads((directory / 'terminal_summary.json').read_text())})
        raw_index.append({'workload': workload, 'mode': row['mode'], 'run_key': row['run_key'],
            'raw_log': str(directory / 'raw.log'), 'sha256': row['raw_log_sha256'],
            'bytes': (directory / 'raw.log').stat().st_size, 'status': row['status']})
    write_json(pack / 'SOURCE_MANIFEST.json', {'runs': manifests,
        'qualification_publication_commit': '2fc7cdcf18afb98c5e8434b87c4ef36316644098',
        'review_coordination_commit': 'aec01450d3c527524ee09ee59242f582fafe5354',
        'scope': 'R0 primary 1168-slot/128B common-copy-latch matched pair; not R1 ideal'})
    hold = REPO / 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/SCIENTIFIC_HOLD.json'
    if hold.is_file():
        shutil.copyfile(hold, pack / 'SCIENTIFIC_ACCEPTANCE.json')
    with (pack / 'RAW_LOG_INDEX.csv').open('x', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(raw_index[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(raw_index)
    comparison = json.loads((source / 'COMPARISON.json').read_text())
    (pack / 'README.md').write_text(
        '# Frozen R0 ' + workload + ' full-application pair\n\n'
        'Status: COMPLETE_VALID hardware terminal, one exact matched pair; no suite average.\n\n'
        + ('Scientific acceptance SUSPENDED: memcpy clock violates physical bank service.\n'
           'Numbers below are retained observations, not accepted primary performance.\n'
           'See SCIENTIFIC_ACCEPTANCE.json and the superseding clock-correction pack.\n\n'
           if hold.is_file() else '') +
        f"B16 cycles {rows[0]['cycles']}; U_WB16 cycles {rows[1]['cycles']}; "
        f"B16/U_WB16 speedup {comparison['speedup_B16_over_U_WB16']:.9f}x.\n\n"
        'Both arms use Core 126394be / producing Framework 37dec04d and the same\n'
        '0b504f55... R0 binary, full trace/epoch and primary system configuration.\n'
        'Exact hashes, feature/ideal vectors and hardware closures are in manifests.\n'
        'Numerical dataless-SASS output is unavailable; independent qualification\n'
        'covers sector versions and production request/resource lifecycles.\n\n'
        'RESOURCE_MOVEMENT reports WB creation/accept/completion, full/retry events,\n'
        'copy service, staged peak and mean, role transfers, bank waits, WAD/lower\n'
        'pressure and real source-emitted lower read/write bytes. Events summed\n'
        'over slices are not whole-GPU elapsed cycles. Peak is max of per-slice\n'
        'peaks; occupancy mean divides summed slot-cycle integrals by summed\n'
        'slice observation cycles. Borrow-role transfer counts alone do not prove\n'
        'capacity relief. A causal capacity claim needs stronger static redivision\n'
        'and copy attribution. Preserve ties/regressions. TVD/RO/ideals remain OFF.\n')
    freeze_checksums(pack)
    return pack


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', type=Path, required=True)
    args = parser.parse_args()
    packs = []
    for source in sorted(args.stage.glob('pair_*')):
        if (source / 'PAIR_RECEIPT.json').is_file():
            result = package_pair(source)
            if result:
                packs.append(str(result.relative_to(REPO)))
    base = REPO / 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'
    registry = Registry().snapshot()
    write_json(base / 'RUN_REGISTRY_SNAPSHOT.json', registry)
    receipt = json.loads((base / 'RECEIPT.json').read_text())
    receipt['active_runs'] = [r for r in registry['runs'].values()
        if r['owner'] == 'lane5' and r['status'] in ('RESERVED', 'RUNNING')]
    receipt['formal_campaign']['completed_pairs'] = len(packs)
    receipt['formal_campaign']['running_workloads'] = sorted({r['identity']['workload']
        for r in receipt['active_runs']})
    receipt['formal_campaign'].pop('running_workload', None)
    receipt['formal_campaign']['completed_pair_packs'] = packs
    receipt['validation']['R0_formal_valid_runs'] = len(packs) * 2
    receipt['validation']['new_formal_runs'] = len(packs) * 2
    receipt['updated_at'] = datetime.now(timezone.utc).isoformat()
    receipt['status'] = 'R0_FIVE_PAIRS_COMPLETE_VALID' if len(packs) == 5 else 'R0_ROLLING_PAIRS_IN_PROGRESS'
    if (base / 'SCIENTIFIC_HOLD.json').is_file():
        receipt['status'] = 'APPLICATION_QUALIFICATION_SUSPENDED_CLOCK_REPAIR_READY'
        receipt['validation']['scientifically_accepted_R0_application_runs'] = 0
    receipt['artifacts'] = list(dict.fromkeys(receipt['artifacts'] + packs))
    write_json(base / 'RECEIPT.json', receipt)
    print(json.dumps({'packs': packs, 'active_runs': len(receipt['active_runs'])}, indent=2))


if __name__ == '__main__':
    main()
