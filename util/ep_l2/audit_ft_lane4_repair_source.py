#!/usr/bin/env python3
"""Static-only R1 repair replay and ideal timestamp delta; never compiles/runs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

R1='be651ccfe7bd47c0bbd8c30fe6439ae3b60cf8de'
LANE4='b8b3d55b392fcff793d0aec684bddb73ba3065a9'
PATCH_REL='docs/ep_l2/review_packs/FT20261016_LANE5_WARMUP_IDENTITY_CANDIDATE_r2/CORE_R1_ADAPTED_CANDIDATE.patch'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--framework',type=Path,required=True);p.add_argument('--core',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    def git(*args,env=None,input=None):
        return subprocess.check_output(['git','-C',str(a.core),*args],env=env,input=input)
    assert not git('status','--porcelain').strip()
    publication=subprocess.check_output(['git','-C',str(a.framework),'rev-parse','origin/hrl/ep-l2-ft20261016-lane5-v1'],text=True).strip()
    patch=subprocess.check_output(['git','-C',str(a.framework),'show',publication+':'+PATCH_REL])
    (a.out/'LANE5_CLOCK_WARMUP_R1_CANDIDATE.patch').write_bytes(patch)
    replays=[]
    for base in [R1,LANE4]:
        with tempfile.TemporaryDirectory(prefix='lane4-repair-index-') as tmp:
            env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
            git('read-tree',base,env=env)
            git('apply','--cached','--check','-',env=env,input=patch)
            git('apply','--cached','-',env=env,input=patch)
            tree=git('write-tree',env=env).decode().strip()
            replays.append(dict(parent=base,replayed_tree=tree,patch_apply='PASS_STATIC_ONLY'))
    runtime_delta=git('diff','--name-only',replays[0]['replayed_tree'],replays[1]['replayed_tree'],'--','src')
    assert not runtime_delta.strip()
    parent=replays[0]['replayed_tree']
    text=git('show',parent+':src/gpgpu-sim/l2cache.cc').decode()
    old='m_L2cache->ep_l2_ideal_touch_resident(mf, cycle);'
    new='m_L2cache->ep_l2_ideal_touch_resident(mf, cycle + m_memcpy_cycle_offset);'
    assert text.count(old)==1
    changed=text.replace(old,new)
    with tempfile.TemporaryDirectory(prefix='lane4-tag-time-index-') as tmp:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
        git('read-tree',parent,env=env)
        blob=git('hash-object','-w','--stdin',input=changed.encode()).decode().strip()
        git('update-index','--cacheinfo','100644',blob,'src/gpgpu-sim/l2cache.cc',env=env)
        candidate=git('write-tree',env=env).decode().strip()
        tag_patch=git('diff','--binary',parent,candidate)
    (a.out/'CORE_IDEAL_TAG_TIMESTAMP_ONLY_CANDIDATE.patch').write_bytes(tag_patch)
    inc=git('show',parent+':src/gpgpu-sim/ep-l2-ft-cache.inc').decode()
    access=inc[inc.index('enum cache_request_status l2_cache::ft_access'):]
    checks=dict(shared_runtime_after_repair_equal=True,
        clock_fix_uses_gpu_sum='const unsigned long long physical_cycle = m_gpu->gpu_sim_cycle + m_gpu->gpu_tot_sim_cycle;' in access,
        preserved_native_tag_time='data_cache::access(addr, mf, time, events)' in access,
        warmup_delegates_when_off='if (!ft_enabled()) { baseline_cache::force_tag_access' in inc,
        warmup_requires_no_live_ft='assert(ft_drained() && m_ep_l2_wad_entries_live.empty())' in inc,
        ideal_bank_stays_physical='ep_l2_ideal_read_bank(mf, cycle)' in text,
        tag_timestamp_delta_only=changed.count(new)==1 and changed.replace(new,old)==text)
    assert checks['clock_fix_uses_gpu_sum'] and checks['preserved_native_tag_time'] and checks['warmup_requires_no_live_ft'] and checks['ideal_bank_stays_physical'] and checks['tag_timestamp_delta_only']
    report=dict(status='STATIC_APPLY_AND_SOURCE_AUDIT_ONLY_NOT_COMPILED',lane5_publication=publication,
        patch_source_path=PATCH_REL,patch_sha256=hashlib.sha256(patch).hexdigest(),replays=replays,
        checks=checks,tag_timestamp_patch_parent_tree=parent,tag_timestamp_candidate_tree=candidate,
        tag_timestamp_patch_sha256=hashlib.sha256(tag_patch).hexdigest(),
        official_R1_1_source=None,official_R1_1_binary=None,builds=0,executed_production_tests=0)
    (a.out/'SOURCE_REPAIR_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (a.out/'REVIEW_FINDINGS.md').write_text('''# R1.1 static repair findings — no runtime PASS

The Lane5 published combined candidate applies without conflict to both exact
Lane1 R1 be651ccf and Lane4 b8b3d55b in private indices. Their repaired runtime
sources are identical (the original difference is CMake test targets). Clock
and warmup candidate bytes are retained with producer publication/hash.
This is not an official repaired release; the warmup delta remains uncompiled.

1. Ideal-read replacement timestamp: the bank request already receives physical
   GPU cycle, which must stay physical. The same value currently reaches
   ep_l2_ideal_touch_resident -> tag_array::access, whereas native accesses add
   m_memcpy_cycle_offset. The attached one-call delta restores native Tag time
   while leaving bank/response timing unchanged. It is UNCOMPILED and requires
   a nonzero-offset ideal warm-hit/LRU test on official R1.1. Default OFF is
   unaffected. Apply only after the exact combined repair parent tree recorded
   in SOURCE_REPAIR_AUDIT, or rebase against official R1.1 and re-audit.

2. Dirty warmup victim: candidate force_tag_access releases a live RESIDENT
   after checking pins/pending, but has no explicit dirty-victim rejection or
   lower writeback before release. ft_drained() does not mean all resident
   cache lines are clean. Lane1 must test/preserve dirty data or explicitly
   reject the unsupported warmup phase. No assertion should be disabled.

3. Repeat/partial-sector warmup: requested sectors are reset to version-zero;
   other sectors retain versions. A drained but previously written line may
   still be dirty. The ideal ReferenceMemory is a separate address/producer
   version store and this candidate adds no host-reinitialization hook there.
   Initial-before-GPU prefill is consistent with cold symbolic version-zero;
   post-producer host rewrites require a defined model or explicit rejection.
   Do not infer an expanded host/oracle scope from this static replay.

4. Reservation/Tag agreement: a slot is reserved using the initial Tag probe,
   then baseline_cache::force_tag_access performs native Tag work. Actual
   chosen index, owner generation, partial-sector reset, warm immediate read,
   subsequent eviction/WB/set_done and final response drain need production
   evidence. I_READ_HIT bypasses ordinary hits and cannot by itself establish
   that the ordinary warm payload-owner path is repaired.

Only Lane1's official R0.1/R1.1 source freeze and Lane5's new physical_bank_clock
and memcpy_payload_identity plus per-ideal gates can qualify application runs.
No budget, input, oracle or new I_BANK point is introduced here.
''')
    assert not git('status','--porcelain').strip()
    print(json.dumps(report))


if __name__=='__main__':main()
