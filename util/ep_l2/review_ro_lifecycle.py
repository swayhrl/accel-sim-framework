#!/usr/bin/env python3
"""Focused immutable-source RO/native ownership review; never C++ execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from audit_ro_repair import function

PRIOR = '5ae8b06d58b61189140f571ab37b5f6d51228632'
PATH = 'src/gpgpu-sim/'


def read(core, source, name):
    return subprocess.check_output(['git', '-C', str(core), 'show', source + ':' + PATH + name], text=True)


def review(core, source):
    rt = read(core, source, 'ep-l2-ro-runtime.inc')
    ft = read(core, source, 'ep-l2-ft-cache.inc')
    cache = read(core, source, 'gpu-cache.cc')
    preview = function(rt, '  bool preview(')
    access = function(ft, 'enum cache_request_status l2_cache::ft_access')
    helper = function(rt, '  bool native_owner_conflict(') if '  bool native_owner_conflict(' in rt else ''
    # The old concrete path uses an issued RO sector and a non-RO texture read.
    # Its native descriptor is added, but only mark_ready queues that response.
    ready = function(cache, 'void mshr_table::ro_line_ready(')
    add = function(cache, 'void mshr_table::add(')
    send = function(cache, 'void baseline_cache::send_read_request(new_addr_type addr,\n                                       new_addr_type block_addr,\n                                       unsigned cache_index, mem_fetch *mf,\n                                       unsigned time, bool &do_miss, bool &wb,')
    guard = 'if(m_ro->native_owner_conflict(mf))return RESERVATION_FAIL;'
    preview_guard = 'if(native_owner_conflict(m))'
    checks = {
        'source_witness_native_add_has_no_ro_owner_exclusion': 'entry.m_list.push_back(mf)' in add and 'm_ro_line_owner' not in add,
        'source_witness_issued_sector_can_coalesce_without_lower': 'mshr_hit && mshr_avail && (!needs_lower_read || lower_issue_slot)' in send and send.index('m_mshrs.add(') < send.index('if (needs_lower_read)'),
        'source_witness_ro_ready_does_not_enqueue_native_response': 'm_ready_sectors |= mask' in ready and 'm_current_descriptor_response' not in ready,
        'eligible_original_read_not_reclassified': 'if(candidate(m))return false;' in helper,
        'commit_refuses_before_native_or_ro_mutation': guard in access and access.index(guard) < access.index('m_ro->merge_existing(') and access.index(guard) < access.index('m_tag_array->probe('),
        'preview_refuses_before_normal_fallback': preview_guard in preview and preview.index(preview_guard) < preview.index('if(!new_request(m))return false;') and 'p.probe_status=RESERVATION_FAIL;return true;' in preview.split('if(!new_request(m))', 1)[0],
        'guard_uses_existing_target_without_address_scan': bool(helper) and 'handle h;return target(m,h);' in helper and 'for(' not in helper,
    }
    unchanged = {}
    for name in ['ep-l2-ro-oracle.h', 'ep-l2-ro-sha256.h', 'ep-l2-ro-transactions.h', 'ep-l2-ro-store-port.h', 'gpu-cache.cc', 'gpu-cache.h', 'l2cache.cc', 'gpu-sim.cc']:
        a = read(core, PRIOR, name); b = read(core, source, name)
        unchanged[name] = {'unchanged': a == b, 'sha256': hashlib.sha256(b.encode()).hexdigest()}
    warm = 'bool l2_cache::ft_try_force_tag_access'
    checks['direct_host_epoch_guard_and_prefill_unchanged'] = function(ft, warm) == function(read(core, PRIOR, 'ep-l2-ft-cache.inc'), warm)
    checks['existing_target_index_unchanged'] = function(rt, '  bool target(') == function(read(core, PRIOR, 'ep-l2-ro-runtime.inc'), '  bool target(')
    passed = all(checks.values()) and all(row['unchanged'] for row in unchanged.values())
    return dict(schema='LANE3_RO_NATIVE_OWNERSHIP_SOURCE_REVIEW_R14',source=source,prior_source=PRIOR,
                status='SOURCE_GUARD_PRESENT_NOT_COMPILED_OR_QUALIFIED' if passed else 'MIXED_NATIVE_OWNERSHIP_SOURCE_GAP',
                checks=checks,preserved_source=unchanged,cpp_execution=False,independent_qualification=False,
                counterexample=['RO A/sector0 is lower-accepted with bypass=OFF, owning native line entry A',
                  'TEXTURE_ACC_R A/sector0 reaches native send_read_request; issued mask suppresses another lower packet',
                  'native add allocates a descriptor/pin on the RO-owned entry',
                  'RO return updates ro_line_ready but never queues that native descriptor',
                  'native response and its pin cannot drain without another native mark_ready event'],
                note='Counterexample is derived from source call edges, not an observed simulator execution.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core',type=Path,required=True);p.add_argument('--source',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();x=review(a.core,a.source)
    with a.output.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
    print(x['status'])
    return 0 if x['status']=='SOURCE_GUARD_PRESENT_NOT_COMPILED_OR_QUALIFIED' else 2


if __name__=='__main__':raise SystemExit(main())
