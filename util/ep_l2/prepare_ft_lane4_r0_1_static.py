#!/usr/bin/env python3
"""Reproduce an uncompiled ideal delta on exact Lane1 R0.1; no checkout/build."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

BASE='62dc1d179b5516e68b21b695c7a9c5d0667e9671'
PUBLICATION='c93d900e1f968a3b69990dc29b78d50fc18f35ac'
ROOT=Path(__file__).resolve().parents[2]
PATCH=ROOT/'docs/ep_l2/review_packs/FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2/CORE_MINIMAL.patch'


def prepare(core,out):
    out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='lane4-r0-1-index-') as tmp:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
        def git(*args,data=None):
            return subprocess.check_output(['git','-C',str(core),*args],env=env,input=data)
        def replace(path,old,new,count):
            raw=git('show',':'+path)
            if raw.count(old)!=count:raise ValueError('unexpected source shape: '+path)
            # Delete just the first duplicate; the second remains in place.
            updated=raw.replace(old,new,1)
            blob=git('hash-object','-w','--stdin',data=updated).decode().strip()
            git('update-index','--cacheinfo','100644',blob,path)
        assert git('rev-parse',BASE+'^{tree}')==git('rev-parse',PUBLICATION+'^{tree}')
        git('read-tree',BASE)
        method=(b'  unsigned long long ft_bank_grants_for_test(unsigned bank) const {\n'
                b'    return m_L2cache->ep_l2_payload_bank_grants(bank);\n  }\n')
        replace('src/gpgpu-sim/l2cache.h',method,b'',2)
        (out/'R0_1_DUPLICATE_ACCESSOR_ONLY.patch').write_bytes(git('diff','--cached',BASE,'--'))
        git('read-tree',BASE)
        applied=subprocess.run(['git','-C',str(core),'apply','--cached','--3way',str(PATCH)],
                               env=env,capture_output=True)
        (out/'APPLY.log').write_bytes(applied.stdout+applied.stderr)
        if applied.returncode:raise ValueError('ideal patch replay failed')
        assert not git('ls-files','-u')
        replace('src/gpgpu-sim/l2cache.h',method,b'',2)
        before_tag=git('write-tree').decode().strip()
        replace('src/gpgpu-sim/l2cache.cc',
                b'ep_l2_ideal_touch_resident(mf, cycle);',
                b'ep_l2_ideal_touch_resident(mf, cycle + m_memcpy_cycle_offset);',1)
        tree=git('write-tree').decode().strip()
        (out/'CORE_IDEAL_TAG_TIMESTAMP_ONLY.patch').write_bytes(git('diff',before_tag,tree,'--'))
        # Exact producer repair bytes must survive ideal integration unchanged.
        preserved=['src/gpgpu-sim/ep-l2-ft-cache.inc',
                   'tests/ep_l2/test_ft_memcpy_clock.cc',
                   'tests/ep_l2/test_ft_host_prefill.cc',
                   'tests/ep_l2/R0_1_REPAIR_SCOPE.md']
        hashes={}
        for name in preserved:
            raw=git('show',BASE+':'+name)
            assert raw==git('show',tree+':'+name),name
            hashes[name]=hashlib.sha256(raw).hexdigest()
        patch=git('diff','--cached','--binary',BASE,'--')
        (out/'CORE_R0_1_IDEAL_STATIC.patch').write_bytes(patch)
        (out/'CORE_RUNTIME_ONLY.patch').write_bytes(git('diff','--cached',BASE,'--','src'))
        (out/'DIFF_STAT.txt').write_bytes(git('diff','--cached','--stat',BASE,'--'))
        # Replay the delivered combined patch independently into a fresh index.
        git('read-tree',BASE)
        git('apply','--cached','--check',str(out/'CORE_R0_1_IDEAL_STATIC.patch'))
        git('apply','--cached',str(out/'CORE_R0_1_IDEAL_STATIC.patch'))
        assert git('write-tree').decode().strip()==tree
        report=dict(status='STATIC_REPLAY_VERIFIED_UNCOMPILED_NOT_QUALIFIED',
                    base_core_commit=BASE,base_tree=git('rev-parse',BASE+'^{tree}').decode().strip(),
                    tree_equivalent_publication=PUBLICATION,result_tree=tree,tag_patch_parent_tree=before_tag,
                    original_ideal_patch_sha256=hashlib.sha256(PATCH.read_bytes()).hexdigest(),
                    combined_patch_sha256=hashlib.sha256(patch).hexdigest(),
                    preserved_producer_files_sha256=hashes,unmerged_entries=0,
                    exact_combined_patch_roundtrip=True,builds=0,simulations=0,
                    source_edits=['frozen Lane4 ideal implementation',
                                  'remove one duplicate test accessor',
                                  'ideal Tag touch uses memcpy offset; bank/reply remain physical'],
                    runtime_source_commit=None,binary_sha256=None,
                    runtime_config_sha256=None,trace_content_sha256=None)
        (out/'SOURCE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
        return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(prepare(a.core,a.out.resolve()),indent=2))
