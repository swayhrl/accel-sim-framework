#!/usr/bin/env python3
"""Prepare exact c948 ideal integration, retaining repaired physical clocks.

Only a private Git index and the specified new output directory are written.
No worktree, compiler, resource admission, waiter or simulator is started.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
BASE='c948184504d82b80e23eb3f4ff6cdfd328ba9355'
PUBLICATION='57e1c363aede1a7790bdf94136d832d35ee7b34b'
ORIGINAL=ROOT/'docs/ep_l2/review_packs/FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2/CORE_MINIMAL.patch'
TESTS=ROOT/'tests/ep_l2/ft_lane4/r7'


def prepare(core,out):
    out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='lane4-r7-index-') as tmp:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
        def git(*args,data=None):
            return subprocess.check_output(['git','-C',str(core),*args],env=env,input=data)
        def put(path,raw):
            blob=git('hash-object','-w','--stdin',data=raw).decode().strip()
            git('update-index','--add','--cacheinfo','100644',blob,path)
        def replace(path,old,new):
            raw=git('show',':'+path)
            if raw.count(old)!=1:raise ValueError('unexpected source shape: '+path)
            put(path,raw.replace(old,new))
        assert git('rev-parse',BASE+'^{tree}')==git('rev-parse',PUBLICATION+'^{tree}')
        git('read-tree',BASE)
        applied=subprocess.run(['git','-C',str(core),'apply','--cached','--3way',str(ORIGINAL)],
                               env=env,capture_output=True)
        (out/'ORIGINAL_REPLAY.log').write_bytes(applied.stdout+applied.stderr)
        unmerged=git('diff','--name-only','--diff-filter=U').decode().splitlines()
        if applied.returncode!=1 or unmerged!=['tests/ep_l2/test_ft_wbuf.cc']:
            raise ValueError('unexpected replay conflict set: '+repr(unmerged))
        # The old patch extracted this fixture. Re-extract from exact c948 so
        # its repaired direct-call clock is never replaced by the old fixture.
        native=git('show',BASE+':tests/ep_l2/test_ft_wbuf.cc')
        marker=b'static void capacity_and_versions('
        assert native.count(marker)==1
        fixture,body=native.split(marker,1)
        old=b'unsigned sets=1)'
        assert fixture.count(old)==1
        fixture=fixture.replace(old,b'unsigned sets=1, bool ideal_wb=false, bool ideal_meta=false)')
        anchor=b'    std::string geometry='
        assert fixture.count(anchor)==1
        fixture=fixture.replace(anchor,
            b'    const char *idealargs[]={"ft-test","-gpgpu_ep_l2_ideal_wb",ideal_wb?"1":"0",'
            b'"-gpgpu_ep_l2_ideal_meta",ideal_meta?"1":"0"};\n'
            b'    option_parser_cmdline(p,5,idealargs);\n'+anchor)
        put('tests/ep_l2/ft_test_fixture.h',b'#ifndef EP_L2_FT_TEST_FIXTURE_H\n#define EP_L2_FT_TEST_FIXTURE_H\n'+fixture+b'\n#endif\n')
        put('tests/ep_l2/test_ft_wbuf.cc',b'#include "ft_test_fixture.h"\n\n'+marker+body)
        assert not git('ls-files','-u')
        header=git('show',':src/gpgpu-sim/l2cache.h')
        assert header.count(b'ft_bank_grants_for_test(unsigned bank) const')==1
        before_tag=git('write-tree').decode().strip()
        replace('src/gpgpu-sim/l2cache.cc',b'ep_l2_ideal_touch_resident(mf, cycle);',
                b'ep_l2_ideal_touch_resident(mf, cycle + m_memcpy_cycle_offset);')
        before_sync=git('write-tree').decode().strip()
        (out/'TAG_TIMESTAMP_ONLY.patch').write_bytes(git('diff',before_tag,before_sync,'--'))
        replace('src/gpgpu-sim/ep-l2-ideal-reference.h',b'  std::vector<Byte> read(uint64_t line, const Mask &mask) const {',
            b'  // Successful host prefill replaces selected sectors with fresh unknown\n'
            b'  // version-zero symbols, matching the FT Payload contract. Never reset\n'
            b'  // the producer clock or modify unselected bytes/older response copies.\n'
            b'  void host_prefill(uint64_t line, const Mask &mask) {\n'
            b'    assert((line & 127) == 0);\n'
            b'    auto it = versions_.find(line);\n'
            b'    for (unsigned b = 0; b < 128; ++b) if (mask[b]) {\n'
            b'      if (it != versions_.end()) it->second[b] = 0;\n'
            b'      known_.erase(line + b);\n'
            b'    }\n'
            b'  }\n'
            b'  std::vector<Byte> read(uint64_t line, const Mask &mask) const {')
        replace('src/gpgpu-sim/l2cache.cc',
            b'  if (!m_L2cache->ft_try_force_tag_access(addr, m_memcpy_cycle_offset + time, mask))\n'
            b'    return false;\n  ++m_memcpy_cycle_offset;',
            b'  if (!m_L2cache->ft_try_force_tag_access(addr, m_memcpy_cycle_offset + time, mask))\n'
            b'    return false;\n'
            b'  // Only an accepted, drained, clean host prefill may replace reference\n'
            b'  // symbols. A refusal leaves both the reference and offset unchanged.\n'
            b'  if (m_config->m_L2_config.m_ep_l2_ideal_read_hit) {\n'
            b'    ep_l2_ideal::ReferenceMemory::Mask bytes{};\n'
            b'    for (unsigned b = 0; b < 128; ++b) bytes[b] = mask.test(b / 32);\n'
            b'    m_ideal_reference.host_prefill(addr & ~uint64_t(127), bytes);\n'
            b'  }\n  ++m_memcpy_cycle_offset;')
        for name in ['test_ideal_host_prefill_reference.cc','test_ideal_host_prefill_partition.cc',
                     'ideal_host_prefill_b16.config']:
            put('tests/ep_l2/'+name,(TESTS/name).read_bytes())
        tree=git('write-tree').decode().strip()
        (out/'REFERENCE_SYNC_ONLY.patch').write_bytes(git('diff',before_sync,tree,'--'))
        (out/'REFERENCE_SYNC_RUNTIME_ONLY.patch').write_bytes(git('diff',before_sync,tree,'--','src'))
        preserved={}
        for name in ['src/gpgpu-sim/ep-l2-ft-cache.inc','tests/ep_l2/test_ft_memcpy_clock.cc',
                     'tests/ep_l2/test_ft_host_prefill.cc','tests/ep_l2/R0_1_REPAIR_SCOPE.md']:
            raw=git('show',BASE+':'+name);assert git('show',tree+':'+name)==raw
            preserved[name]=hashlib.sha256(raw).hexdigest()
        assert git('show',tree+':tests/ep_l2/test_ft_wbuf.cc').split(marker,1)[1]==body
        combined=git('diff','--cached','--binary',BASE,'--')
        (out/'CORE_C948_IDEAL_CANDIDATE.patch').write_bytes(combined)
        (out/'CORE_RUNTIME_ONLY.patch').write_bytes(git('diff','--cached',BASE,'--','src'))
        (out/'DIFF_STAT.txt').write_bytes(git('diff','--cached','--stat',BASE,'--'))
        git('read-tree',BASE);git('apply','--cached',str(out/'CORE_C948_IDEAL_CANDIDATE.patch'))
        assert git('write-tree').decode().strip()==tree
        report=dict(status='STATIC_CANDIDATE_NOT_COMPILED_NOT_QUALIFIED',base_core_commit=BASE,
            tree_equivalent_publication=PUBLICATION,result_tree=tree,reference_patch_parent_tree=before_sync,
            original_conflicts=unmerged,remaining_conflicts=0,obsolete_getter_patch_applied=False,
            fixture_resolution='Extract exact c948 clock implementation; add ideal options only; keep all test bodies exact.',
            preserved_producer_sha256=preserved,combined_patch_sha256=hashlib.sha256(combined).hexdigest(),
            combined_patch_roundtrip=True,compiler_invocations=0,production_tests_run=0,simulations=0,
            binary_sha256=None,runtime_config_sha256=None,trace_content_sha256=None)
        (out/'SOURCE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
        return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(prepare(a.core,a.out.resolve()),indent=2))
