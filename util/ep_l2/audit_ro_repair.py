#!/usr/bin/env python3
"""Bounded exact-parent static audit. Never a compiler/runtime/qualification gate."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

PARENT='62dc1d179b5516e68b21b695c7a9c5d0667e9671'
PUBLICATION='c93d900e1f968a3b69990dc29b78d50fc18f35ac'
FILES=['ep-l2-ft-cache.inc','ep-l2-ro-runtime.inc','ep-l2-ro-store-port.h',
       'ep-l2-ro-transactions.h','gpu-cache.h','l2cache.cc','gpu-sim.cc']


def section(text,start,end):return text.split(start,1)[1].split(end,1)[0]


def function(text,signature):
    """Extract a C++ function, masking comments/literals for brace counting."""
    start=text.index(signature)
    mask=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                lambda m:' '*len(m[0]),text)
    begin=mask.index('{',start);depth=0
    for n in range(begin,len(mask)):
        if mask[n]=='{':depth+=1
        elif mask[n]=='}':
            depth-=1
            if depth==0:return text[start:n+1]
    raise ValueError('unclosed source function: '+signature)


def normalize(text):return re.sub(r'\s+','',text)


def source_checks(files,parent):
    ft=files['ep-l2-ft-cache.inc'];rt=files['ep-l2-ro-runtime.inc'];cfg=files['gpu-cache.h']
    body=function(ft,'enum cache_request_status l2_cache::ft_access')
    clock=function(ft,'unsigned long long l2_cache::ft_physical_cycle')
    calls=re.findall(r'm_ep_l2_payload\.request\((.*?)\);',body,re.S)
    wrapper=function(ft,'void l2_cache::force_tag_access')
    warm=function(ft,'bool l2_cache::ft_try_force_tag_access')
    target=section(rt,'  bool target(','  bool new_request(')
    issues=section(rt,'  void issue(','  bool merge_existing(')
    returns=function(rt,'bool l2_cache::ro_return')
    guard='  if(m_ro && !m_ro->prefill_allowed())return false;\n'
    callback='  if(m_ro)m_ro->prefill_complete(index,handle,owner,mask);\n'
    common_warm=warm.replace(guard,'').replace(callback,'')
    gpu_copy=function(files['gpu-sim.cc'],'void gpgpu_sim::perf_memcpy_to_gpu')
    gpu_original=gpu_copy.replace('  if(m_ro_epoch_started)throw std::logic_error("host write inside certified whole-commandlist epoch");\n','')
    tx=files['ep-l2-ro-transactions.h']
    checks={
        'ft_bank_requests_use_physical_cycle':bool(calls) and all('physical_cycle' in c and not re.search(r'\btime\b',c) for c in calls),
        'shared_physical_clock_helper':'physical_cycle = ft_physical_cycle();' in body and 'return c.ft_physical_cycle();' in rt and 'm_gpu->gpu_sim_cycle + m_gpu->gpu_tot_sim_cycle' in clock,
        'ft_arbiter_monotonic_assert':'assert(cycle >= m_cycle' in cfg,
        'wb_and_wad_births_physical':all('time' not in v for v in re.findall(r'p\.born = (.*?);',body)) and 'std::make_pair(p.victim_address, physical_cycle)' in body,
        'native_tag_timestamp_retained':'data_cache::access(addr, mf, time, events)' in body,
        'ro_packet_timestamp_physical':'const uint64_t cycle=physical_cycle();' in issues and '32,false,cycle,' in issues and 'm_miss_queue_status,cycle' in issues,
        'ro_fill_bridge_checks_physical':'cycle!=m_ro->physical_cycle()' in returns,
        'ro_response_bridge_checks_physical':'if(cycle!=physical_cycle())throw' in section(rt,'  bool prepare(','  void commit('),
        'ro_wrapper_scope_guard':'if(m_ro)m_ro->prefill_begin();' in wrapper,
        'ro_try_prefill_guard_before_mutation':guard in warm and warm.index(guard)<warm.index('m_ep_l2_payload.release('),
        'ro_try_scope_never_reopens':'return !ever_open && !open && !selected && tx->drained();' in rt,
        'ro_warm_tag_owner_bank_check':all(s in rt for s in ['actual!=index','c.tag_payload_handle(index)!=h','h.payload_id%4!=index%4']),
        'ro_warm_generation_uses_existing_vector':'++generations[index];' in section(rt,'  void prefill_complete(','  bool demand('),
        'separate_default_off_bits':'m_ro_tag_detach = m_ro_line_mshr_bypass = false;' in cfg,
        'original_global_read_predicate':'m->get_access_type()==GLOBAL_ACC_R' in rt and '!m->isatomic()' in rt,
        'attached_tag_handle_not_completion_cam':'h=c.tag_payload_handle(i)' in target and 'for(' not in target,
        'detached_merge_uses_only_native_index':'return !c.m_config.m_ro_line_mshr_bypass &&' in target and 'lookup_ro_line' in target,
        'whole_commandlist_scope_retained':'"whole_commandlist"' in rt and '"TRACE_MODEL_CLOSED_WORLD"' in rt,
        'preserves_l1_try_prefill_checks':normalize(common_warm)==normalize(function(parent['ep-l2-ft-cache.inc'],'bool l2_cache::ft_try_force_tag_access')),
        'preserves_l1_physical_clock_helper':normalize(clock)==normalize(function(parent['ep-l2-ft-cache.inc'],'unsigned long long l2_cache::ft_physical_cycle')),
        'preserves_l1_partition_try_gate':normalize(function(files['l2cache.cc'],'bool memory_sub_partition::ft_try_force_l2_tag_update'))==normalize(function(parent['l2cache.cc'],'bool memory_sub_partition::ft_try_force_l2_tag_update')),
        'preserves_l1_partition_force_gate':normalize(function(files['l2cache.cc'],'void memory_sub_partition::force_l2_tag_update'))==normalize(function(parent['l2cache.cc'],'void memory_sub_partition::force_l2_tag_update')),
        'preserves_l1_full_width_partial_gpu_memcpy':normalize(gpu_original)==normalize(function(parent['gpu-sim.cc'],'void gpgpu_sim::perf_memcpy_to_gpu')),
        'detached_fill_has_no_tag_install':'if(e.attached){' in normalize(function(tx,'  bool fill(identity h, unsigned mask')),
        'completion_validates_payload_generation':'m_slots[h.payload_id].h == h' in tx and 'm_port.live(h, m_slots[h.payload_id].line)' in tx,
        'shared_D512_descriptor_admission':'shared.descriptor_pool_capacity() != 512' in tx and 'm_shared.reserve_ro_descriptor(' in tx,
        'response_commit_requires_granted_cycle':'fifo_accepted && e.prepared_cycle != cycle' in tx and 'm_shared.release_ro_descriptor(e.waiters[e.prepared_index].descriptor)' in tx,
    }
    return checks


def load(core):
    files={name:(core/'src/gpgpu-sim'/name).read_text() for name in FILES}
    parent={name:subprocess.check_output(['git','-C',str(core),'show',PARENT+':src/gpgpu-sim/'+name],text=True)
            for name in ['ep-l2-ft-cache.inc','l2cache.cc','gpu-sim.cc']}
    return files,parent


def audit(core):
    files,parent=load(core);checks=source_checks(files,parent)
    trees=[subprocess.check_output(['git','-C',str(core),'rev-parse',x+'^{tree}'],text=True).strip() for x in [PARENT,PUBLICATION]]
    checks['candidate_and_published_tree_equal']=trees[0]==trees[1]
    return dict(schema='LANE3_RO_EXACT_CANDIDATE_STATIC_AUDIT_R6',core_source_commit=subprocess.check_output(['git','-C',str(core),'rev-parse','HEAD'],text=True).strip(),
        exact_candidate_parent=PARENT,parent_publication=PUBLICATION,parent_tree=trees[0],
        status='STATIC_PASS_NOT_COMPILE_OR_RUNTIME_PASS' if all(checks.values()) else 'STATIC_FAIL',checks=checks,
        file_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in files.items()},
        compile_status='NOT_RUN_PRODUCTION_ADMISSION_UNCHANGED',runtime_status='NOT_RUN',independent_qualification=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();x=audit(a.core)
    with a.output.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
    print(json.dumps(x,indent=2))
    if x['status']=='STATIC_FAIL':raise SystemExit(1)


if __name__=='__main__':main()
