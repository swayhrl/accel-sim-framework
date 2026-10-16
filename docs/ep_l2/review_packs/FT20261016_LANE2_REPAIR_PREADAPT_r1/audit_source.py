"""Source-only boundary audit. Never implies compilation or runtime PASS."""
from pathlib import Path
import hashlib, json, re, subprocess

CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane2-repair-r3')
OUT=Path('/workspace/results/ep_l2_ft20261016/lane2/review_r3_repair_adaptation')
def body(text, signature):
    start=text.index(signature); first=text.index('{',start); depth=1; end=first+1
    while depth:
        if text[end]=='{':depth+=1
        if text[end]=='}':depth-=1
        end+=1
    return text[first+1:end-1]
def calls(text, name):
    result=[]; at=0
    while True:
        at=text.find(name+'(',at)
        if at<0:return result
        begin=at+len(name); end=begin+1; depth=1
        while depth:
            if text[end]=='(':depth+=1
            if text[end]==')':depth-=1
            end+=1
        result.append(' '.join(text[at:end].split()));at=end

ft=(CORE/'src/gpgpu-sim/ep-l2-ft-cache.inc').read_text()
tvd=(CORE/'src/gpgpu-sim/ep-l2-tvd-cache.inc').read_text()
cache=(CORE/'src/gpgpu-sim/gpu-cache.h').read_text()
partition=(CORE/'src/gpgpu-sim/l2cache.cc').read_text()
access=body(ft,'enum cache_request_status l2_cache::ft_access(')
promotion=body(tvd,'bool l2_cache::tvd_promote(')
host=body(ft,'void l2_cache::force_tag_access(')
results=[]
def check(name, condition, evidence):
    assert condition,name
    results.append({'boundary':name,'status':'SOURCE_CHECK_PASS_NOT_RUNTIME','evidence':evidence})
reqs=calls(access,'m_ep_l2_payload.request')
check('FT_bank_calls',len(reqs)==4 and all('physical_cycle' in c for c in reqs),reqs)
check('FT_physical_clock_source','physical_cycle = m_gpu->gpu_sim_cycle + m_gpu->gpu_tot_sim_cycle' in access,'actual gpu_sim_cycle + gpu_tot_sim_cycle, no memcpy offset')
life=calls(access,'tvd_install_victim')+calls(access,'tvd_reclaim_one')+calls(access,'ft_rollback')
check('FT_directory_lifetime_and_rollback',len(life)==4 and all('physical_cycle' in c for c in life),life)
life=calls(promotion,'m_tvd->commit_dirty_promotion')+calls(promotion,'m_tvd->promote')
check('TVD_promotion_lifetime',len(life)==2 and all('physical_cycle' in c for c in life) and 'p.born = physical_cycle' in promotion,life)
check('native_Tag_timestamps_preserved','data_cache::access(addr, mf, time, events)' in access and 'm_tag_array->tvd_bind(index, address, time, old.valid_sectors)' in promotion and 'baseline_cache::force_tag_access(addr, time, mask)' in host,'native access, promotion bind and host fill continue using Tag timestamp')
check('frontend_physical_clock','const auto now = m_gpu->gpu_sim_cycle + m_gpu->gpu_tot_sim_cycle;' in partition and 'tvd_frontend(mf, now,' in partition and 'tvd_response_commit(mf, now)' in partition,'actual cache_cycle call site')
check('monotonic_bank_guard','cycle >= m_cycle && "FT bank clock must be physical and monotonic"' in cache,'consumed exact Lane5 clock-only delta')
check('host_no_GPU_bank_service',not calls(host,'m_ep_l2_payload.request'),'untimed metadata initialization has no bank operation')
first_edit=min(host.index('m_tvd->reclaim('),host.index('m_ep_l2_payload.release(handle)'))
check('host_checks_before_metadata_edit',all(host.index(t)<first_edit for t in ['ft_drained()','ep_l2_wad_occupancy() == 0','!m_tvd_lookup && !m_tvd_read','!m_tag_array->block_is_modified(index)','old.pending_sector_mask.none()','m_tvd->at(alias.index).reclaimable()']), 'drain/mandatory/lease/dirty/pending/alias assertions precede first reclaim/release')
check('host_actual_chosen_Tag','actual_index == index' in host and 'slot.ready_sector_mask |= mask' in host and 'if (mask.test(sector)) slot.versions[sector] = 0' in host,'same-index postfill assert; preserve other sectors, initialize only declared mask')
check('host_bank_class','landing % 4 == index % 4' in host,'existing sole-allocator bank mapping')
sp=(CORE/'src/gpgpu-sim/l2cache.h').read_text()
prefill=body(sp,'void force_l2_tag_update(')
check('host_active_frontend_rejected',prefill.index('!busy()')<prefill.index('m_L2cache->force_tag_access'),'actual subpartition request tracker guard precedes host hook')
check('served_metric_scope','served_sector_bytes' in tvd and 'avoided_lower_bytes' not in tvd,'production summary emits served bytes; no saved-byte alias')
for path in ['src/gpgpu-sim/ep-l2-ft-cache.inc','src/gpgpu-sim/ep-l2-tvd-cache.inc','src/gpgpu-sim/gpu-cache.h','src/gpgpu-sim/l2cache.h','tests/ep_l2/test_tvd_production.cc']:
    assert not re.search(r'^(<<<<<<<|=======|>>>>>>>)', (CORE/path).read_text(),re.M),path
result={'scope':'source inspection only; not C++ compiler/type/ABI check and not runtime proof','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=CORE,text=True).strip(),'checks':results,'compiler_invoked':False,'runtime_cases_executed':0}
(OUT/'SOURCE_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'source_checks':len(results),'status':'SOURCE_CHECKS_ONLY','runtime_cases':0}))
