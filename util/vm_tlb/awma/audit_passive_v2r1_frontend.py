#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASELINE = Path('/root/awma_rtx4080_v1_baseline_promotion_v1_runtime/src/gpgpu-sim/src/gpgpu-sim/shader.cc')
MIXED_V2 = Path('/root/awma_passive_last_translation_result_forwarding_v2_runtime/src/gpgpu-sim/src/gpgpu-sim/shader.cc')
V2R1 = Path('/root/awma_passive_last_translation_result_forwarding_v2r1_runtime/src/gpgpu-sim/src/gpgpu-sim/shader.cc')
OUT = Path('/root/awma_passive_last_translation_result_forwarding_v2r1_runtime/frontend_source_audit.json')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordered(text: str, tokens: list[str]) -> bool:
    position = 0
    for token in tokens:
        found = text.find(token, position)
        if found < 0:
            return False
        position = found + len(token)
    return True


def block(text: str, start: str, end: str) -> str:
    first = text.index(start)
    last = text.index(end, first)
    return text[first:last]


def main() -> int:
    baseline = BASELINE.read_text()
    mixed = MIXED_V2.read_text()
    v2r1 = V2R1.read_text()
    baseline_block = block(
        baseline,
        'for (std::list<mem_access_t>::reverse_iterator it = entries.rbegin();',
        '  mem_access_t &access = inst.accessq_back();')
    v2r1_block = block(
        v2r1,
        'for (std::list<mem_access_t>::reverse_iterator it = entries.rbegin();',
        '  mem_access_t &access = inst.accessq_back();')
    critical = [
        'reverse_iterator it = entries.rbegin()',
        'it != entries.rend(); ++it',
        'mem_access_t &candidate = *it',
        'candidate.vm_translation_applied()',
        'transaction_crosses_page(candidate.get_sim_va()',
        'm_gpu->vm_translation()->translate(',
        'm_sid, 0, candidate.get_sim_va(), candidate.get_size()',
        'candidate.get_uid()',
        'ready_application_v2)',
        'prelaunch_result == vm_translation::READY',
        'vm_ready_application_prelaunch_ready',
        'if (ready_application_v2)',
        'apply_ready_translation(candidate, ignored_pa, ignored_source)',
        'vm_ready_application_ready_unapplied_observations',
    ]
    checks = {
        'frozen_v1_critical_order': ordered(baseline_block, critical),
        'v2r1_critical_order': ordered(v2r1_block, critical),
        'mixed_v2_contains_forbidden_break':
            'if (passive_last_result) break;' in mixed,
        'v2r1_forbidden_break_absent':
            'if (passive_last_result) break;' not in v2r1,
        'v2r1_reverse_scan_present':
            'reverse_iterator it = entries.rbegin()' in v2r1_block,
        'v2r1_ready_observation_nonconsuming_under_frozen_mode':
            'ready_application_v2)' in v2r1_block,
        'v2r1_share_only_suppression_guards_retained': (
            'AWMA_TRANSLATION_CANDIDATE_SAME_PAGE_SHARE' in v2r1_block and
            'nonblocking_opportunistic_share' in v2r1_block),
        'v2r1_accounting_has_no_translate_call': (
            'note_prelaunch_attempt(' in v2r1_block and
            v2r1_block.count('m_gpu->vm_translation()->translate(') == 1),
    }
    # The audited fallback block contains exactly one frozen V1 prelaunch
    # translate call. Accounting adds no second call.
    status = 'PASS' if all(checks.values()) else 'FAIL'
    result = {
        'status': status,
        'authority': 'AWMA_RTX4080_SIM_BASELINE_V1@8d1f14a32f5538660d74da86ccb03a2c504c5735',
        'files': {
            'frozen_v1_shader': {'path': str(BASELINE), 'sha256': sha(BASELINE)},
            'mixed_v2_shader': {'path': str(MIXED_V2), 'sha256': sha(MIXED_V2)},
            'v2r1_shader': {'path': str(V2R1), 'sha256': sha(V2R1)},
        },
        'blocks': {
            'frozen_v1_prelaunch_sha256': hashlib.sha256(
                baseline_block.encode()).hexdigest(),
            'v2r1_candidate_prelaunch_sha256': hashlib.sha256(
                v2r1_block.encode()).hexdigest(),
        },
        'checks': checks,
        'note': ('Whole-block hashes differ because V2R1 retains accepted C1 '
                 'code and adds observational accounting. The ordered '
                 'frozen-V1 fallback traversal and consume policy are audited '
                 'explicitly; passive mode has no skip/break.'),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
