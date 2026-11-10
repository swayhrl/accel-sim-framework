"""Exact5 resource adapter for terminal legacy rows unknown to V3.

Keep the V3 accounting and every advertised write commitment. Clear only
its stale unmapped-RAM diagnostics after a fresh, bounded terminal audit.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
REG = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH = Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')
FAMILY = 'gemm' if 'host_gemm_bound_v2' in __file__ else 'stencil'
REQUESTS = {'gemm': 'EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
            'stencil': 'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1'}
OWN = REQUESTS[FAMILY]
PEER = REQUESTS['stencil' if FAMILY == 'gemm' else 'gemm']
M = 1024**2
ORIGINAL = Path(__file__).with_name('resources_b1.py')
PIN = {'gemm': 'a7bd990569f2f2ea025a1e7063b18a3f6b0fa0f5aa611d56d838d0e1838dfd81',
       'stencil': '589d2d8944de8737d9eaa7d1b33624d8b8fdbaf4d06e9db0d92cd835aa24ba26'}[FAMILY]
EP_CLOSED = {
    'EP_L2_PFV4_A1_STENCIL_SOURCE78_850_L100_V1',
    'EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1',
    'EP_L2_PFV4_A3_TRANSPOSE_SOURCE78_850_L100_V1',
    'EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1',
    'EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1',
    'EP_L2_UMT1_CONV3072_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1',
    'EP_L2_UMT1_SCAN_CF8D1C4D_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1',
    'EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104',
}
DTC_TERMINAL = {
    'DTC_ORACLE_INITIAL8_20261106_V1',
    'DTC_ORACLE_REMAINING24_20261106_V1',
    'DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1',
    'DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1',
    'DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1',
    'DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1',
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def original():
    if sha(ORIGINAL) != PIN:
        raise ValueError('pinned original resource adapter drift')
    spec = importlib.util.spec_from_file_location('exact5_original_resources_' + FAMILY, ORIGINAL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot():
    # The V3 snapshot can map this shared claims file only once.  Map the
    # peer carrier and claims below; add the peer to SCOPES only in admit(),
    # where the restore de-duplication checks request identity.
    s = original().snapshot()
    raw = REG.read_bytes()
    epoch = json.loads(EPOCH.read_bytes())
    if hashlib.sha256(raw).hexdigest() != s.get('registry_sha256') or epoch['native_registry_sha256'] != s['registry_sha256']:
        s['foreign_metadata_errors'].append('exact5 registry/epoch changed during snapshot')
        return s
    reg = json.loads(raw)['registered_future_requests']
    claim_path = ROOT / 'control/DISPATCH_CLAIMS.json'
    before = sha(claim_path)
    claims = json.loads(claim_path.read_bytes())['claims']
    if any(row.get('request') not in (OWN, PEER) or row.get('cohort') != case
           for case, row in claims.items()):
        s['foreign_metadata_errors'].append('unknown exact5 shared claim owner/cohort')
        return s
    own_claims = {c: r for c, r in claims.items() if r['request'] == OWN}
    peer_claims = {c: r for c, r in claims.items() if r['request'] == PEER}
    for case, row in claims.items():
        spec_path = ROOT / 'cases' / case / 'control/FROZEN_SPEC.json'
        if not spec_path.exists() or sha(spec_path) != row.get('spec_sha256') or reg[row['request']]['admitted_specs'].get(case) != row['spec_sha256']:
            s['foreign_metadata_errors'].append('exact5 shared claim/spec mismatch ' + case)
            return s
    if sha(claim_path) != before:
        s['foreign_metadata_errors'].append('exact5 shared claims changed during snapshot')
        return s
    s['EP_CPU_claims'] = [dict(request=r['request'], cohort=c, cpu=r['host_cpu'], state=r['state'])
                          for c, r in claims.items()]
    s['occupied_model_or_claim_cpus'] = sorted(set(s['occupied_model_or_claim_cpus']) |
                                              {r['host_cpu'] for r in claims.values()})
    s['current_own_restore_window_bytes'] = 128*M if own_claims else 0
    s['foreign_claims_pins'][PEER] = dict(path=str(claim_path), sha256=before, claims=len(peer_claims))
    peer_carrier = reg[PEER]['reserved_write_bytes']
    own_carrier = reg[OWN]['reserved_write_bytes']
    if own_claims and own_carrier < sum(max(0,r['remaining_write_bytes']) for r in own_claims.values())+130*M:
        s['foreign_metadata_errors'].append('own exact5 active claims/carrier underbound')
        return s
    if own_carrier and not own_claims and own_carrier < reg[OWN]['remaining']*64*M+130*M:
        s['foreign_metadata_errors'].append('own exact5 registered carrier lacks 128MiB restore guarantee')
        return s
    peer_rows = [r for r in s['foreign_write_entries'] if r.get('request') == PEER]
    if peer_carrier:
        if (len(peer_rows) > 1 or (peer_rows and peer_rows[0]['bytes'] != peer_carrier) or
                peer_carrier < 130*M or
                (not peer_claims and peer_carrier < reg[PEER]['remaining']*64*M+130*M)):
            s['foreign_metadata_errors'].append('peer exact5 carrier cannot cover 128MiB global restore')
            return s
        if peer_rows:
            s['foreign_write_entries'].remove(peer_rows[0])
        s['foreign_write_entries'] += [
            dict(request=PEER, kind='EXACT5_PEER_REMAINING_OUTPUT', bytes=peer_carrier-130*M),
            dict(request=PEER, kind='ONE_SHARED_RESTORE_WINDOW_AND_2M_METADATA', bytes=130*M),
        ]
    elif peer_rows and any(r['bytes'] for r in peer_rows):
        s['foreign_metadata_errors'].append('peer exact5 zero carrier mismatch')
        return s
    if peer_claims and peer_carrier < sum(max(0,r['remaining_write_bytes']) for r in peer_claims.values())+130*M:
        s['foreign_metadata_errors'].append('peer exact5 active claims/carrier mismatch')
        return s
    for case, row in peer_claims.items():
        if row['state'] not in ('CLAIMED','RUNNING','TERMINAL_PENDING_VALIDATION'):
            s['foreign_metadata_errors'].append('unknown peer exact5 claim state ' + case)
            return s
        rss = 0
        if row.get('model_pid'):
            proc = Path('/proc') / str(row['model_pid'])
            try:
                parts = (proc/'stat').read_text().rsplit(')',1)[1].split()
                if int(parts[19]) != row['model_start_ticks'] or parts[0] in ('Z','X'):
                    raise ValueError('peer model PID generation changed')
                rss = int(next(line.split()[1] for line in (proc/'status').read_text().splitlines()
                               if line.startswith('VmRSS:')))*1024
            except (OSError, ValueError, StopIteration, KeyError):
                if row['state'] == 'RUNNING':
                    s['foreign_metadata_errors'].append('unverified live peer exact5 model ' + case)
                    return s
        if not any(x.get('request') == PEER and x.get('cohort') == case
                   for x in s['foreign_RAM_entries']):
            s['foreign_RAM_entries'].append(dict(request=PEER, cohort=case,
                additional_RAM_bytes=max(0,row['estimated_peak_RAM_bytes']-rss),
                RSS_bytes=rss, kind='VERIFIED_EXACT5_PEER_CLAIM'))
    s['foreign_additional_RAM_bytes'] = sum(x['additional_RAM_bytes'] for x in s['foreign_RAM_entries'])
    s['foreign_remaining_write_bytes'] = sum(x['bytes'] for x in s['foreign_write_entries'])
    before = s.get('foreign_metadata_errors', [])
    if not before:
        return s
    live = s.get('actual_loader_aware_models', [])
    mapped = {(r['model_pid'], r['model_start_ticks']) for r in claims.values()
              if r.get('model_pid') and r.get('model_start_ticks')}
    mapped.update((r['pid'], r['start_ticks']) for r in s['foreign_RAM_entries']
                  if r.get('pid') and r.get('start_ticks'))
    mapped.update((r['pid'], r['start_ticks'])
                  for r in s.get('DTC48_accounting', {}).get('models', []))
    if any((r['pid'], r['start_ticks']) not in mapped for r in live):
        s['foreign_metadata_errors'].append('unmapped live model during exact5 terminal audit')
        return s
    active_peer = {case for case, row in reg[PEER].get('consumed', {}).items()
                   if row.get('state') in ('CONSUMED_BEFORE_FORK', 'RUNNING')}
    if not active_peer.issubset(peer_claims) or any(
            peer_claims[case].get('uuid') != reg[PEER]['consumed'][case].get('uuid')
            for case in active_peer):
        s['foreign_metadata_errors'].append('active peer consumed row lacks matching claim/UUID')
        return s
    cleared = []
    for name in EP_CLOSED | DTC_TERMINAL:
        q = reg[name]
        rows = q.get('consumed')
        if not isinstance(rows, dict) or q.get('remaining') != 0 or len(rows) != q.get('budget'):
            return s
        if name in EP_CLOSED:
            if q.get('state') != 'CLOSED_COMPLETED' or q.get('reserved_write_bytes') != 0 or any(
                    row.get('state') not in ('CLOSED_ACCEPTED', 'CLOSED_UNACCEPTED') for row in rows.values()):
                return s
        else:
            if q.get('state') != 'RUNNING' or any(not isinstance(row.get('execution_receipt'), dict)
                    or row.get('charged') != 1 for row in rows.values()):
                return s
        cleared.append('unmapped active foreign RAM owner ' + name)
    if active_peer:
        cleared.append('unmapped active foreign RAM owner ' + PEER)
    if not set(cleared).issubset(before):
        return s
    s['foreign_metadata_errors'] = [e for e in before if e not in cleared]
    s['exact5_terminal_legacy_reconciliation'] = {
        'cleared_errors': sorted(cleared), 'registry_sha256': s['registry_sha256'],
        'DTC_advertised_write_commitments_retained': True,
        'live_models_mapped_to_verified_claims_or_owner_accounting': True,
        'live_model_pid_generations': [(r['pid'], r['start_ticks']) for r in live],
    }
    return s


def admit(s, additional, writes, policy):
    v3 = original().impl()
    v3.SCOPES[PEER] = ROOT
    return v3.admit(s, additional, writes, policy)
