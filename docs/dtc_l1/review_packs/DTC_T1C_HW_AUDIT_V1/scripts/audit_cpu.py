#!/usr/bin/env python3
"""Bounded read/hash/arithmetic audit. No EDA, simulator, GPU or RTL writes.

Run in the isolated Framework checkout: python3 <this-file>.
Only this review pack is written. External inputs are individually named below;
the inventory lists tracked paths in rtl/ and scripts/ of five known L2 clones.
No Lane U state/raw/locks or other lane runtime directories are accessed.
"""
import csv
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = PACK.parents[3]
T_HEAD = "f520a445436b57c0a0f2494fb858a1636f04d2bc"
CORE_HEAD = "6fba0136f8465b59fe5858a950fa39efb265f654"
CORE = Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1')
HW = Path('/workspace/repos/gpu-l2-cache-verilog')
PDF = Path('/workspace/worktrees/accel-sim-decoupled-l2/docs/reference/赵皓宇 博士论文.pdf')
T = 'docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/'
SG = 'docs/dtc_l1/iscas2027/granularity/sg0/'
R8 = 'docs/l2_rtl/review_packs/V3-R8_ASIC_TIMING_CLOSURE/'
CLONES = {
    'gpu-l2-cache-verilog': '7aa1dec737a11524022531985ff3f71913e1ed9c',
    'gpu-l2-cache-verilog-v3r0-clean': 'e0f92857e5468337306a06abbbbe2f10d0aa4ded',
    'gpu-l2-cache-verilog-v3r1-clean': '270ceb57d235aebd9efd7ac8e32ed565a6bf5ddb',
    'gpu-l2-cache-verilog-v3r1r-clean': 'a5009dab5b793595d52d25627a61e1f31e9ccdbd',
    'gpu-l2-cache-verilog-v3r2-clean': 'f02733e51726d8d6e286a531b20a16aaeae11520',
}


def git(repo, *args, binary=False):
    r = subprocess.run(['git', '-C', str(repo), *args], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.stdout if binary else r.stdout.decode().strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tsv(name, rows, fields=None):
    rows = list(rows)
    fields = fields or list(rows[0])
    with (PACK / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main():
    assert git(CORE, 'rev-parse', 'HEAD') == CORE_HEAD
    checks = {'cpu_only': True, 'lane_u_paths_accessed': False,
              'rtl_or_simulator_writes': False, 'eda_invocations': 0,
              't_anchor': T_HEAD, 'core_anchor': CORE_HEAD}
    records = []

    def source(sid, repo, rel, category, variant, scope):
        path = repo / rel
        data = path.read_bytes()
        commit = git(repo, 'rev-parse', 'HEAD')
        committed = git(repo, 'show', f'{commit}:{rel}', binary=True)
        assert data == committed, f'Uncommitted source: {path}'
        records.append(dict(source_id=sid, path=str(path), git_commit=commit,
                            file_sha256=sha(data), bytes=len(data), kind=category,
                            variant=variant, scope=scope,
                            library_PVT_voltage='UNAVAILABLE',
                            DC_version='UNAVAILABLE',
                            matched_current_finite_L1='NO'))

    for sid, rel in [('T_RESOURCE', 'RESOURCE_OVERHEAD.tsv'),
                     ('T_SCOPE', 'SCIENTIFIC_SCOPE.md'),
                     ('T_LEGALITY', 'CONFIG_LEGALITY_REVIEW.json'),
                     ('T_REPORT', 'LATEST_REPORT.md'),
                     ('T_PREREG', 'scripts/preregister.py')]:
        assert (ROOT / (T + rel)).read_bytes() == git(ROOT, 'show', T_HEAD + ':' + T + rel, binary=True)
        source(sid, ROOT, T + rel, 'frozen_simulator_document', 'A/B plus T pilot variants',
               'Configuration/arithmetic only; not RTL or measured PPA; audited T anchor ' + T_HEAD)
        # The Framework audit branch later has a different HEAD; the T blob anchor is authoritative.
        records[-1]['git_commit'] = T_HEAD
    for sid, rel in [('CORE_COMMON', 'src/gpgpu-sim/dtc-l1-common.h'),
                     ('CORE_SHADER', 'src/gpgpu-sim/shader.cc'),
                     ('CORE_SHADER_H', 'src/gpgpu-sim/shader.h')]:
        source(sid, CORE, rel, 'C++ behavioral_model', 'finite IO/OO/Base',
               'Software contract; never host sizeof/vector allocation as hardware area')
    for sid, rel in [('SG0_RTL', 'SG0_DISSERTATION_RTL_AUDIT.tsv'),
                     ('SG0_IDENTITY', 'SG0_SOURCE_IDENTITY.tsv'),
                     ('SG0_PDF', 'SG0_DISSERTATION_PROVENANCE.tsv')]:
        source(sid, ROOT, SG + rel, 'prior_source_audit', 'historical L1 versus candidate L2',
               '69cd5b6 candidate RTL is not established as dissertation implementation')
        records[-1]['git_commit'] = T_HEAD
    hw_files = [
        ('L2_PARAMS', 'rtl/decouple_cache_v3/gsgpu_l2cache_params.v'),
        ('L2_FILELIST', 'rtl/decouple_cache_v3/filelist_v3.f'),
        ('L2_TOP', 'rtl/decouple_cache_v3/gsgpu_l2cache.v'),
        ('L2_TAG', 'rtl/decouple_cache_v3/gsgpu_l2cache_tagram_wrapper.v'),
        ('L2_META', 'rtl/decouple_cache_v3/gsgpu_l2cache_buf_meta_ram_wrapper.v'),
        ('L2_ADDR', 'rtl/decouple_cache_v3/gsgpu_l2cache_buf_addr_ram_wrapper.v'),
        ('L2_DATA', 'rtl/decouple_cache_v3/gsgpu_l2cache_dataram_wrapper.v'),
        ('L2_STRB', 'rtl/decouple_cache_v3/gsgpu_l2cache_strbram_wrapper.v'),
        ('L2_SPRAM', 'rtl/decouple_cache_v3/gsgpu_spram.v'),
        ('L2_OLD_IOOO', 'rtl/decouple_cache/gpu_l2_params.vh'),
        ('L2_CLASSIC', 'rtl/classic_cache/gpu_l2_tag_array.v'),
        ('L2_DC', 'scripts/dc_elab_v3.tcl'),
        ('L2_GENUS', 'scripts/genus_elab_v3.tcl'),
        ('L2_OPEN_SCRIPT', 'scripts/open_synth_v3.sh'),
        ('L2_RAM_CONTRACT', 'docs/decouple_cache_v3_data_ram_timing.md'),
        ('L2_R8_AUDIT', R8 + 'r8_a_environment_and_collateral_audit.md'),
        ('L2_R8_COMMANDS', R8 + 'r8_a_commands_and_provenance.md'),
        ('L2_R8_STA', R8 + 'r8_a_sta_report.md'),
        ('L2_R8_README', R8 + 'README.md'),
        ('L2_R7_DECISION', 'docs/l2_rtl/review_packs/V3-R7-T_TIMING_ANALYSIS_AND_OPTIMIZATION/r7_t2_decision.md'),
    ]
    assert git(HW, 'rev-parse', 'HEAD') == CLONES[HW.name]
    for sid, rel in hw_files:
        source(sid, HW, rel, 'unmatched_L2_collateral', 'L2; not A/B finite L1',
               'gsgpu_l2cache defaults 256x16 Tag; 4x1024 data slots; no qualified current-L1 PPA')
    records.append(dict(source_id='THESIS_CH4', path=str(PDF), git_commit='UNBOUND_TO_RTL',
                        file_sha256=sha(PDF.read_bytes()), bytes=PDF.stat().st_size,
                        kind='historical_published_synthesis_result', variant='historical IO and OO',
                        scope='PDF pp79/82, printed pp61/64; sections4.3.3/4.5.3; OO/IO area+4.7%; raw DC absent',
                        library_PVT_voltage='UNAVAILABLE', DC_version='UNAVAILABLE',
                        matched_current_finite_L1='NO'))
    assert records[-1]['file_sha256'] == 'a9482b420b62636aac379c4a9e670c0f09ec78c287d51fe90a4ac02d66687213'
    tsv('HARDWARE_PROVENANCE.tsv', records)
    byid = {r['source_id']: r for r in records}
    def refs(*ids):
        return ';'.join(i + ':' + byid[i]['file_sha256'] for i in ids)

    inventory = []
    for name, commit in CLONES.items():
        repo = Path('/workspace/repos') / name
        assert git(repo, 'rev-parse', 'HEAD') == commit
        tracked = git(repo, 'ls-files', '--', 'rtl', 'scripts').splitlines()
        candidates = [p for p in tracked if Path(p).suffix.lower() in ('.rpt', '.lib', '.db', '.lef', '.sdc')
                      or ('dc' in Path(p).name.lower() and p.endswith('.tcl'))]
        report_roots = [p for p in ('reports', 'synth', 'synthesis', 'dc', 'build/synth', 'out/synth', 'outputs')
                        if (repo / p).exists()]
        inventory.append(dict(repo=str(repo), head=commit,
                              scope='git tracked path names only in rtl/ and scripts/; fixed report-root existence checks',
                              candidates=json.dumps(candidates), existing_report_roots=json.dumps(report_roots),
                              limit='Not a server-wide absence proof; untracked trees and private/unrelated projects not searched'))
    tsv('BOUNDED_SEARCH_SCOPE.tsv', inventory)

    rows = []
    def cost(metric, a, b, unit, rule, sources, limitation):
        rows.append(dict(metric=metric, A_original_OO128=a, B_T1C_OO128=b,
                         delta=b-a if isinstance(a, int) and isinstance(b, int) else 'CONDITIONAL',
                         unit=unit, evidence_level='ESTIMATED_ONLY', formula_or_condition=rule,
                         source_sha256=refs(*sources), exclusions=limitation))
    cost('logical_sets',32,64,'sets','frozen A/B configuration',['T_RESOURCE'],'not measured hardware')
    cost('ways_per_bank_lookup',4,8,'ways','frozen A/B configuration',['T_RESOURCE'],'not comparator timing')
    cost('logical_mappings',128,512,'entries','sets*ways',['T_RESOURCE'],'not physical data growth')
    cost('coverage',16,64,'KiB','mappings*128/1024',['T_RESOURCE'],'logical mapped coverage, not physical capacity')
    cost('bank_count',4,4,'banks','fixed',['T_SCOPE'],'actual RAM implementation unavailable')
    cost('sets_per_bank',8,16,'sets/bank','sets/4',['T_SCOPE'],'row decoding 3 to4 bits; not RAM access time')
    cost('mappings_per_bank',32,128,'entries/bank','sets*ways/4',['T_SCOPE'],'fixed bank count does not fix bank area')
    cost('identity_57_example',128*57,512*57,'bit','mappings*57 aligned-address identity bits',['T_RESOURCE','T_PREREG'],'example retains redundant set bits; not implemented tag width')
    cost('physical_ID_10_example',128*10,512*10,'bit','mappings*ceil(log2(640))',['T_RESOURCE'],'excludes generation copy and port cost')
    cost('valid_example',128,512,'bit','one bit/mapping',['T_RESOURCE'],'excludes state-encoding/ports')
    old_lru=(math.factorial(4)-1).bit_length()
    new_lru=(math.factorial(8)-1).bit_length()
    assert (old_lru,new_lru)==(5,16)
    cost('LRU_information_bound_example',32*old_lru,64*new_lru,'bit','sets*ceil(log2(ways!))',['T_PREREG','CORE_COMMON'],'lower information bound, no update logic or hardware encoding; software uses uint64 timestamps')
    a=128*68+32*old_lru
    b=512*68+64*new_lru
    assert (a,b,b-a)==(8864,35840,26976)
    cost('LANE_T_EXAMPLE_SUM',a,b,'bit','57 identity+10 physID+1 valid per mapping plus LRU bound',['T_RESOURCE','T_PREREG'],'NOT area/minimal total RTL cost; excludes generation, pending, comparators, SRAM periphery, wires and control')
    cost('LANE_T_EXAMPLE_SUM_BYTES',a//8,b//8,'byte','example bits/8',['T_RESOURCE'],'delta3372 bytes; byte count is not silicon area')
    cost('parallel_comparators_conditional',4*4,4*8,'comparators','one comparator per way per bank IF all4 banks have parallel way compares',['T_SCOPE','CORE_COMMON'],'architectural estimate; comparator widths/cells/sharing not bound')
    cost('packed_row_width_conditional',4*68,8*68,'bit/read row','ways*68 under the illustrative packing',['T_RESOURCE'],'not a selected macro width; excludes generation/LRU')
    cost('way_mux_levels_conditional',2,3,'binary mux levels','log2(ways) for balanced binary select IF implemented',['T_RESOURCE'],'not a measured critical path or guaranteed topology')
    cost('per_Tag_generation_copy_64_conditional',128*64,512*64,'bit','C++ physical_identity.generation is uint64; hardware IF it retains64 bits per Tag',['CORE_COMMON'],'delta24576 conditional; narrower/eliminated versions require wrap/reuse correctness proof; not summed into LaneT example')
    cost('per_Tag_LRU_timestamp_64_software_only',128*64,512*64,'bit','uint64 tag_entry.lru in software',['CORE_COMMON'],'alternative to illustrative exact-LRU bound; never add both; not an RTL prescription')
    cost('physical_data',640*128*8,640*128*8,'bit','640*128B*8',['T_RESOURCE'],'capacity invariant; macro organization/periphery/ports unqualified')
    cost('ordinary_side_data',16*1024*8,16*1024*8,'bit','16KiB*8',['T_RESOURCE'],'capacity invariant only')
    cost('shared_data_SEPARATE',96*1024*8,96*1024*8,'bit','96KiB*8; separately accounted',['T_RESOURCE'],'not counted as DTC data or included in measured total area')
    cost('PIB_OO',128,128,'entries','fixed OO128',['T_RESOURCE'],'entry width/ports/RAM unavailable; historical IO256 distinct')
    cost('physical_RefCnt_declared',640*13,640*13,'bit','640*13 declared bits',['T_SCOPE','CORE_COMMON'],'software uint64 guarded by13-bit maximum; real storage/control not implemented')
    cost('physical_TagValid',640,640,'bit','one per physical line',['CORE_COMMON'],'does not include logical Tag valid bits')
    cost('max_reference_associations',4096,4096,'associations','128 PIB *32 refs/warp',['T_SCOPE'],'upper bound not physical implementation; de-duplication may reduce occupancy')
    cost('dense_waiter_bitmap_alternative',640*128,640*128,'bit','IF one bit per(physical,PIB) member; historical-style dense option',['CORE_COMMON','THESIS_CH4'],'not current implementation; excludes generation, scheduling, ports; sparse software vectors do not select this option')
    cost('global_lower_outstanding_cap',32768,32768,'requests','fixed T option legality check',['T_PREREG'],'global cap unchanged; storage placement not inferred')
    tsv('TAG_SCALING_COST.tsv',rows)
    with (ROOT / (T+'RESOURCE_OVERHEAD.tsv')).open() as f:
        resource={r['candidate']:r for r in csv.DictReader(f,delimiter='\t')}
    assert int(resource['original']['tag_storage_example_bits'])==a
    assert int(resource['T1-C']['tag_storage_example_bits'])==b
    # Bank identity invariant is exhaustive over the lcm(32,64) periodic domain.
    assert all((i%32)%4==(i%64)%4 for i in range(math.lcm(32,64)))
    checks['bank_identity_invariant'] = 'PASS_EXHAUSTIVE_PERIOD_64'
    checks['packing_arithmetic'] = dict(status='PASS',A_bits=a,B_bits=b,delta_bits=b-a)

    missing='UNAVAILABLE'
    common=dict(rtl_commit=missing,rtl_source_sha256=missing,top_module=missing,
                parameters=missing,process_library=missing,PVT=missing,voltage=missing,
                DC_version=missing,constraints_sha256=missing,SRAM_macro_and_ports=missing,
                includes_full_data_and_periphery=missing)
    area=[]
    def ar(variant,metric,value,unit,level,source_ids,conditions,**kw):
        r=dict(variant=variant,metric=metric,value=value,unit=unit,evidence_level=level,**common)
        r.update(kw)
        r.update(report_source_sha256=refs(*source_ids), applicability=conditions)
        area.append(r)
    for variant in ['A_original_OO128_32x4','B_T1C_OO128_64x8','current_finite_IO256','current_Cplus_Base']:
        for metric,unit in [('total_area','um^2'),('logic_area','um^2'),('SRAM_area','um^2'),('qualified_Fmax','MHz'),('matched_setup_WNS','ps')]:
            ar(variant,metric,missing,unit,'UNAVAILABLE',['T_REPORT','L2_R8_STA'],
               'No bound finite-L1 RTL/run/technology/macro evidence; unmatched L2 cannot substitute')
    ar('historical_dissertation_OO_vs_IO','relative_area_increase',4.7,'percent',
       'MEASURED_HISTORICAL_NOT_MATCHED',['THESIS_CH4'],
       'Published historical synthesis claim only; PDF p82/printed64 s4.5.3; raw DC/top/PVT/macro accounting unavailable; not A/B finite service or T1C')
    ar('A_and_B_simulator_only','tag_service_target_clock',1410,'MHz','ESTIMATED_ONLY',['T_PREREG','CORE_COMMON'],
       'Simulator core clock only; one-cycle tag assumption, no ASIC timing',
       rtl_commit='NOT_RTL_core_'+CORE_HEAD,rtl_source_sha256=refs('CORE_COMMON'),parameters='A32x4/B64x8; fourbanks; same finite services')
    ar('A_and_B_simulator_only','arithmetic_cycle_budget',f'{1e6/1410:.6f}','ps','ESTIMATED_ONLY',['T_PREREG'],
       '1e6ps/1410MHz; nominal model period before clock uncertainty/setup/IO; not measured delay or Fmax',
       rtl_commit='NOT_RTL',parameters='T model core clock1410MHz')
    tsv('AREA_TIMING_COMPARISON.tsv',area)

    sram=[]
    for item,ports,geometry,src in [
        ('current_A_B_Tag','UNAVAILABLE; contract needs1bank request/cycle with update/conflict rules','A32x4 vs B64x8;4banks','T_RESOURCE'),
        ('current_A_B_physical_data','UNAVAILABLE; collection/refill contention unresolved','640x128B fixed','T_RESOURCE'),
        ('current_A_B_ordinary','UNAVAILABLE','16KiB fixed','T_RESOURCE'),
        ('current_A_B_shared_SEPARATE','UNAVAILABLE','96KiB separately fixed','T_RESOURCE'),
        ('current_A_B_PIB','UNAVAILABLE','OO128 fixed; IO256 is different variant','T_RESOURCE'),
        ('current_A_B_generation_refcount_waiter','UNAVAILABLE; multiupdate and bypass unspecified','640 physical;128 PIB;4096 max associations','CORE_COMMON'),
        ('L2_v3_Tag_wrapper','behavioral1R+1W; same-set collision illegal; SYNTHESIS blackbox','256sets x16ways x58bits/way','L2_TAG'),
        ('L2_v3_request_meta_wrapper','SYNTHESIS blackbox; behavioral DPRAM not foundry macro','512 entries; depth/width parameterized','L2_META'),
        ('L2_v3_request_addr_wrapper','SYNTHESIS blackbox; behavioral DPRAM not foundry macro','2 banks;512 total request entries','L2_ADDR'),
        ('L2_v3_data_wrapper','behavioral masked singleport SPRAM; half-rate interface','4banks x1024slots;1024bit line','L2_DATA'),
        ('L2_v3_STRB_wrapper','behavioral masked singleport SPRAM; half-rate interface','4banks x1024slots;128bit STRB','L2_STRB'),
    ]:
        sram.append(dict(storage=item,geometry=geometry,ports_and_collision_model=ports,
                         actual_macro_name='UNAVAILABLE',macro_library_sha256='UNAVAILABLE',
                         process_PVT_voltage='UNAVAILABLE',area_um2='UNAVAILABLE',
                         access_setup_hold_timing='UNAVAILABLE',evidence_level='UNAVAILABLE',
                         source_sha256=refs(src),applicability='Structure/interface evidence only; no mapped macro area/timing. L2 rows are not A/B variants.'))
    tsv('SRAM_MACRO_INVENTORY.tsv',sram)
    # Rehash exactly inspected input files; no external source writes are performed.
    checks['source_rehash_unchanged'] = all(sha(Path(r['path']).read_bytes())==r['file_sha256'] for r in records)
    assert checks['source_rehash_unchanged']
    checks['MEASURED_MATCHED_rows'] = sum(r['evidence_level']=='MEASURED_MATCHED' for r in area)
    checks['T1C_RTL_status']='T1C_RTL_NOT_AVAILABLE_IN_BOUNDED_INSPECTED_MATERIAL'
    checks['total_area_qualification']='NOT_QUALIFIED'
    checks['same_frequency_qualification']='NOT_QUALIFIED'
    checks['generated_at_UTC']=datetime.now(timezone.utc).isoformat()
    (PACK/'CPU_AUDIT_RECEIPT.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    # Manifest intentionally excludes itself, avoiding an impossible self-hash.
    tsv('FILES_SHA256.tsv', ({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
                             for p in sorted(PACK.rglob('*')) if p.is_file() and p.name!='FILES_SHA256.tsv'))
    print(json.dumps(checks,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
