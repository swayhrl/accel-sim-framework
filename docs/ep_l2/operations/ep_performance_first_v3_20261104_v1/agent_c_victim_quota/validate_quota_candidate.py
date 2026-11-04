#!/usr/bin/env python3
# Candidate-only Host contract validator. Never launches or registers a model.
import json, hashlib, sys
from pathlib import Path
SOURCE = {'archive_sha256': 'ffe77ffc39d805b0c5d044f9cd3782d983ce8b17d2056b9ec67d11aa5193b579', 'binary_sha256': 'bab27c440a58426b05d4d10312feeaa55cd28319d52e9396009738e036667553', 'core_source_commit': 'bf4e48447136b990bd2db15e2972a4394e37d21f', 'framework_source_commit': '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7', 'vendor_pybind11_commit': 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b'}
def validate(s, check_files=True):
    assert s['source_identity'] == SOURCE, 'Source5 mismatch'
    assert s['mode'] == 'WV_ZERO_RO' and s['RO_certificate'] is None
    assert s['application_start_authorization'] is False
    e=s['expected_effective_options']
    assert len(e)==s['effective_option_count']==283
    assert s['Source78_effective_option_count']==282
    assert s['parameter_value'] in (0,64,128)
    assert e['-gpgpu_ep_l2_tvd_clean_limit']==str(s['parameter_value'])
    for key,value in {'-gpgpu_ep_l2_ft_mode':'2','-gpgpu_ep_l2_tvd_clean':'1','-gpgpu_ep_l2_tvd_dirty':'1','-gpgpu_ep_l2_ro_line_mshr_bypass':'0','-gpgpu_ep_l2_ro_tag_detach':'0','-gpgpu_ep_l2_descriptor_pool_size':'512','-gpgpu_ep_l2_bank_ops':'1','-gpgpu_ep_l2_wad_entries':'128','-gpgpu_ep_l2_tvd_fixed_entries':'0','-dram_latency':'100','-gpgpu_frfcfs_dram_sched_queue_size':'128','-gpgpu_cache:dl2':'S:32:128:8,L:B:m:L:P,A:128:1,128:0,32'}.items():
        assert e[key]==value, key
    if check_files:
        for r in s['ordered_configs']:
            assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
        assert hashlib.sha256(Path(s['binary_path']).read_bytes()).hexdigest()==SOURCE['binary_sha256']
        assert hashlib.sha256(Path(s['static_library_path']).read_bytes()).hexdigest()==SOURCE['archive_sha256']
    return 'PASS_CANDIDATE_ONLY_NOT_NATIVE_OR_APPLICATION_QUALIFICATION'
if __name__ == '__main__':
    for arg in sys.argv[1:]: print(arg, validate(json.loads(Path(arg).read_text())))
