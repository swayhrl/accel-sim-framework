#!/usr/bin/env python3
"""Bounded static RO repair audit. PASS is source inspection, never C++/runtime qualification."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def section(text,start,end):return text.split(start,1)[1].split(end,1)[0]


def audit(core):
    files={name:(core/'src/gpgpu-sim'/name).read_text() for name in
        ['ep-l2-ft-cache.inc','ep-l2-ro-runtime.inc','ep-l2-ro-store-port.h','gpu-cache.h']}
    ft=files['ep-l2-ft-cache.inc'];rt=files['ep-l2-ro-runtime.inc'];cfg=files['gpu-cache.h']
    body=section(ft,'enum cache_request_status l2_cache::ft_access','void l2_cache::send_write_request')
    calls=re.findall(r'm_ep_l2_payload\.request\((.*?)\);',body,re.S)
    warm=section(ft,'void l2_cache::force_tag_access','void l2_cache::descriptor_admitted')
    target=section(rt,'  bool target(','  bool new_request(')
    issues=section(rt,'  void issue(','  bool merge_existing(')
    returns=section(rt,'bool l2_cache::ro_return','void l2_cache::ro_print')
    checks={
        'ft_bank_requests_use_physical_cycle':bool(calls) and all('physical_cycle' in c and not re.search(r'\btime\b',c) for c in calls),
        'ft_gpu_clock_source':'m_gpu->gpu_sim_cycle + m_gpu->gpu_tot_sim_cycle' in body,
        'ft_arbiter_monotonic_assert':'assert(cycle >= m_cycle' in cfg,
        'wb_and_wad_births_physical':all('time' not in v for v in re.findall(r'p\.born = (.*?);',body)) and 'std::make_pair(p.victim_address, physical_cycle)' in body,
        'native_tag_timestamp_retained':'data_cache::access(addr, mf, time, events)' in body,
        'ro_packet_timestamp_physical':'const uint64_t cycle=physical_cycle();' in issues and '32,false,cycle,' in issues and 'm_miss_queue_status,cycle' in issues,
        'ro_fill_bridge_checks_physical':'cycle!=m_ro->physical_cycle()' in returns,
        'ro_response_bridge_checks_physical':'if(cycle!=physical_cycle())throw' in section(rt,'  bool prepare(','  void commit('),
        'ro_host_prefill_guard':'if(m_ro)m_ro->prefill_begin();' in warm and 'ever_open || open || selected || !tx->drained()' in rt,
        'ro_warm_tag_owner_bank_check':all(s in rt for s in ['actual!=index','c.tag_payload_handle(index)!=h','h.payload_id%4!=index%4']),
        'ro_warm_generation_uses_existing_vector':'++generations[index];' in section(rt,'  void prefill_complete(','  bool demand('),
        'separate_default_off_bits':'m_ro_tag_detach = m_ro_line_mshr_bypass = false;' in cfg,
        'original_global_read_predicate':'m->get_access_type()==GLOBAL_ACC_R' in rt and '!m->isatomic()' in rt,
        'attached_tag_handle_not_completion_cam':'h=c.tag_payload_handle(i)' in target and 'for(' not in target,
        'detached_merge_uses_only_native_index':'return !c.m_config.m_ro_line_mshr_bypass &&' in target and 'lookup_ro_line' in target,
        'whole_commandlist_scope_retained':'"whole_commandlist"' in rt and '"TRACE_MODEL_CLOSED_WORLD"' in rt,
    }
    return dict(schema='LANE3_RO_REPAIR_STATIC_AUDIT_R5',core_source_commit=subprocess.check_output(['git','-C',str(core),'rev-parse','HEAD'],text=True).strip(),
        status='STATIC_PASS_NOT_COMPILE_OR_RUNTIME_PASS' if all(checks.values()) else 'STATIC_FAIL',
        checks=checks,file_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in files.items()},
        compile_status='NOT_RUN_RESOURCE_HOLD',runtime_status='NOT_RUN',independent_qualification=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();x=audit(a.core)
    with a.output.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
    print(json.dumps(x,indent=2))
    if x['status']=='STATIC_FAIL':raise SystemExit(1)


if __name__=='__main__':main()
