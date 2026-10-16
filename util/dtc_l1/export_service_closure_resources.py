#!/usr/bin/env python3
"""Export the preregistered resource vector, without treating it as silicon area."""
import argparse
import csv
import json
from pathlib import Path
import re
from collect_service_closure_attempts import sha


def options(text):
    return dict((k,v.strip()) for k,v in re.findall(r'^-([\w:]+)\s+([^#\n]+)',text,re.M))


def vector(arm,cfg):
    mode=int(cfg['gpgpu_dtc_l1_mode']);dtc=mode in [2,3]
    chunks=cfg['gpgpu_cache:dl1'].split(',');geometry=chunks[0].split(':')
    sets,line,ways=map(int,geometry[1:]);parsed_mshr,merge=map(int,chunks[2].split(':')[1:])
    effective_mshr=int(cfg['gpgpu_dtc_l1_mshr_entries']) if mode==1 else parsed_mshr
    physical=int(cfg['gpgpu_dtc_l1_physical_lines']) if dtc else 0
    tag=int(cfg['gpgpu_dtc_l1_logical_sets'])*int(cfg['gpgpu_dtc_l1_logical_ways']) if dtc else 0
    depth=int(cfg['gpgpu_dtc_l1_oo_pib_entries'] if mode==3 else cfg['gpgpu_dtc_l1_io_pib_entries'] if mode==2 else cfg['gpgpu_dtc_l1_pib_entries'])
    conventional_bytes=sets*line*ways
    unified=int(cfg['gpgpu_unified_l1d_size'])*1024
    return dict(arm=arm,mode=mode,ordinary_organisation=geometry[0],ordinary_enabled_data_bytes=conventional_bytes,
        dtc_physical_lines=physical,dtc_data_bytes=physical*128,
        enabled_data_total_bytes=conventional_bytes+physical*128,
        shared_capacity_bytes=int(cfg['gpgpu_shmem_size']),adaptive_cache=int(cfg['gpgpu_adaptive_cache_config']),
        ordinary_enabled_tag_entries=sets*ways,dtc_logical_mapping_entries=tag,
        logical_mapping_extra_data_bytes=0,
        ordinary_host_max_geometry_bytes=unified if unified else 4*conventional_bytes,
        pib_records=depth,ordinary_mshr_parsed=parsed_mshr,ordinary_mshr_effective=effective_mshr,
        ordinary_merge_limit_per_mshr=merge,ordinary_max_merge_records=effective_mshr*merge,
        ordinary_tag_banks=int(cfg['gpgpu_l1_banks']),ordinary_latency_cycles=int(cfg['gpgpu_l1_latency']),
        ordinary_data_port_bytes_per_cycle=int(chunks[-1]),ordinary_fill_port_bytes_per_cycle=int(chunks[-1]),
        dtc_tag_banks=int(cfg['gpgpu_dtc_l1_tag_banks']) if dtc else 0,
        dtc_tag_latency_cycles=1 if dtc else 0,dtc_allocations_per_core_cycle=4 if dtc else 0,
        dtc_candidate_queue_records=depth if dtc else 0,
        dtc_total_lower_misses_per_sm_physical_bound=physical,
        dtc_create_and_inject_each_per_core_cycle=1 if dtc else 0,
        dtc_refill_bytes_per_core_cycle=32 if dtc else 0,
        dtc_collection_bytes_per_core_cycle=128 if dtc else 0,
        dtc_waiter_updates_per_core_cycle=4 if mode==3 else 0,
        dtc_ref_counter_bits_per_line=int(cfg['gpgpu_dtc_l1_ref_count_bits']) if mode==3 else 0,
        dtc_raw_ref_counter_bits=physical*int(cfg['gpgpu_dtc_l1_ref_count_bits']) if mode==3 else 0,
        dtc_last_ref_or_release_updates_per_retirement_registered=32 if dtc else 0,
        dtc_successful_retirements_per_core_cycle=1 if dtc else 0,
        lower_credit_cap_scope='ROW_SPECIFIC_GLOBAL_NOT_PER_SM_STORAGE',
        area_status='RESOURCE_VECTOR_ONLY_BITS_CAM_AND_PORT_AREA_UNRESOLVED')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence-root',required=True);ap.add_argument('--output-dir',required=True)
    a=ap.parse_args();ev=Path(a.evidence_root);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=False)
    rows=[];inputs=[]
    for p in csv.DictReader((ev/'review_pack/r2/CANONICAL_BASELINE_REUSE.tsv').open(),delimiter='\t'):
        if p['workload']!='Btree':continue
        run=Path(p['run_dir']);candidates=list(run.glob('*stdout*'));assert len(candidates)==1
        source=candidates[0];assert sha(source)==p['stdout_sha256']
        rows.append(vector(p['variant'],options(source.read_text())))
        inputs.append(dict(arm=p['variant'],path=str(source),sha256=sha(source),basis='ORIGINAL_CANONICAL_EXECUTED_OPTIONS'))
    seen=set()
    for p in csv.DictReader((ev/'review_pack/r2/REGISTERED_ROWS_V2.tsv').open(),delimiter='\t'):
        if p['arm'] in seen:continue
        s=json.loads(Path(p['spec_path']).read_text());cfg={}
        for c in s['configs']:
            source=Path(c['path']);assert sha(source)==c['sha256'];cfg.update(options(source.read_text()))
            inputs.append(dict(arm=p['arm'],path=str(source),sha256=c['sha256'],basis='REGISTERED_CONFIG_INHERITANCE'))
        rows.append(vector(p['arm'],cfg));seen.add(p['arm'])
    for name,data in [('RESOURCE_VECTOR.tsv',rows),('RESOURCE_SOURCE_HASHES.tsv',inputs)]:
        with (out/name).open('x') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(data)
    print(json.dumps(dict(arms=len(rows),cost_method='SOURCE_RESOURCE_VECTOR_NOT_EQUAL_AREA')))


if __name__=='__main__':main()
