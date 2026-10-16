#!/usr/bin/env python3
"""Freeze six CPU-only config proposals. Does not register, schedule, or run arms."""
import csv,json,re,shlex
from pathlib import Path
import btree_format_stability_cpu_v1 as m

FINITE=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1')
TRAD=Path('/workspace/worktrees/gpgpu-sim-iscas2027-sg1-canonical')
def effective(paths):
    out={}
    for p in paths:
        key=None
        for token in shlex.split(p.read_text(),comments=True):
            if re.match(r'^-[A-Za-z_]',token):key=token;out[key]=[]
            else:m.need(key is not None,'config token');out[key].append(token)
    return out
def main():
    cfg=m.PACK/'proposed_config';cfg.mkdir(exist_ok=False)
    common=cfg/'COMMON_LOWER_CAP.config';common.write_text('-gpgpu_dtc_l1_lower_outstanding_cap 32768\n')
    sg=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-sg1-wholeline/docs/dtc_l1/iscas2027/granularity/sg1/config')
    trace=m.FROZEN/'gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config'
    registry=m.A/'docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/r2/REGISTERED_ROWS_V2.tsv'
    rows=list(csv.DictReader(registry.open(),delimiter='\t'))
    arms={};copies={};evidence=m.A/'docs/dtc_l1/iscas2027/service_closure_174_v1/config'
    for arm in ['B16-N','TC80-N','TRAD96/C+','IO256','OO128','IO128']:
        finite=arm.startswith(('IO','OO'));family='IO128' if arm=='IO128' else 'IO' if arm=='IO256' else 'OO' if arm=='OO128' else 'TRAD96'
        row=next(r for r in rows if r['workload']=='Btree' and r['arm']==family)
        template=Path(row['spec_path']);m.need(m.sha(template)==row['spec_sha256'],'original Btree fixed spec')
        spec=json.loads(template.read_text());m.need(spec['expected_instructions']==444467849 and spec['trace_list_sha256']==m.ORIGINAL['kernelslist.g'],'full Btree scope')
        if arm in ('B16-N','TC80-N'):
            paths=[m.A/'configs/dtc_l1/fast64/FAST64_BASE.config',sg/('SG1_B16_N_OVERLAY.config' if arm=='B16-N' else 'SG1_TC80_N_OVERLAY.config'),common,trace]
        else:
            paths=[Path(c['path']) for c in spec['configs'][:-1]]+[common,trace]
        owned=[]
        for p in paths:
            if p==common:owned.append(p);continue
            q=cfg/p.name
            if q.exists():m.need(q.read_bytes()==p.read_bytes(),'copy collision')
            else:q.write_bytes(p.read_bytes())
            copies[str(p)]=m.facts(p);owned.append(q)
        opts=effective(owned)
        m.need(m.sha(Path(spec['runtime']))==spec['runtime_sha256'],'frozen runtime')
        mode='2' if arm.startswith('IO') else '3' if arm=='OO128' else '1'
        m.need(opts['-gpgpu_dtc_l1_mode']==[mode],'fixed mode')
        if finite:
            m.need(opts['-gpgpu_dtc_l1_finite_service']==['1'],'finite service')
            active_pib=int(opts['-gpgpu_dtc_l1_io_pib_entries' if arm.startswith('IO') else '-gpgpu_dtc_l1_oo_pib_entries'][0])
            m.need(active_pib==(256 if arm=='IO256' else 128),'fixed PIB')
            vector=dict(logical_tag_sets=32,logical_tag_ways=4,logical_tag_lines=128,physical_128b_lines=640,data_bytes=81920,active_PIB=active_pib,conventional_MSHR='BYPASSED_FOR_CACHEABLE_GLOBAL_LOADS',ref_count_bits=13 if arm=='OO128' else 'NOT_USED_BY_IO',tag_banks=4,tag_per_bank_cycle=1,tag_total_cycle=4,allocation_per_cycle=4,lower_create_per_cycle=1,lower_inject_per_cycle=1,refill_per_cycle=1,collect_sectors_per_cycle=4,retire_per_cycle=1,coalescer_threads_per_cycle=32,extra_side_path='ordinary store acknowledgement; no added shared/local/atomic/bypass path; all unchanged')
        else:
            ways=4 if arm=='B16-N' else 20 if arm=='TC80-N' else 24
            m.need(opts['-gpgpu_cache:dl1']==[f'N:32:128:{ways},L:T:m:L:L,A:512:8,16:0,32'],'qualified conventional line geometry')
            vector=dict(cache_sets=32,cache_ways=ways,cache_128b_lines=32*ways,data_bytes=4096*ways,active_PIB=int(opts['-gpgpu_dtc_l1_pib_entries'][0]),MSHR=int(opts['-gpgpu_dtc_l1_mshr_entries'][0]),l1_latency=int(opts['-gpgpu_l1_latency'][0]),tag_banks=4,tag_per_bank_cycle=1,tag_total_cycle=4,finite_service=False,finite_service_metrics='UNAVAILABLE',extra_side_path='unchanged traditional cache/store paths')
        arms[arm]=dict(status='PROPOSED_NOT_REGISTERED_NOT_RUN',template=m.facts(template),core=spec['core'],build_framework=spec['build_framework'],runtime=dict(path=spec['runtime'],sha256=spec['runtime_sha256']),configs=[dict(relative_path=str(p.relative_to(m.PACK)),sha256=m.sha(p)) for p in owned],effective_options=opts,resource_vector=vector,whole_kernel_names=['findRangeK','findK'],expected_active_thread_instructions=444467849,expected_warp_records=15609327)
    union=set().union(*(set(s['effective_options']) for s in arms.values()))
    differences={k:{a:s['effective_options'].get(k) for a,s in arms.items()} for k in sorted(union) if len({json.dumps(s['effective_options'].get(k)) for s in arms.values()})>1}
    allowed=lambda k:k.startswith(('-gpgpu_dtc_l1_','-gpgpu_cache:dl1')) or k=='-gpgpu_unified_l1d_size'
    m.need(all(allowed(k) for k in differences),('common platform mismatch',differences))
    required={'-gpgpu_n_clusters':['64'],'-gpgpu_n_cores_per_cluster':['1'],'-gpgpu_clock_domains':['1410.0:1410.0:1410.0:850.0'],'-network_mode':['2'],'-gpgpu_dtc_l1_lower_outstanding_cap':['32768'],'-gpgpu_coalesce_arch':['70'],'-gpgpu_shmem_num_banks':['32'],'-gpgpu_shmem_warp_parts':['1'],'-gpgpu_adaptive_cache_config':['0'],'-gpgpu_l1_cache_write_ratio':['0']}
    for opt,v in required.items():m.need(all(s['effective_options'].get(opt)==v for s in arms.values()),('common option',opt))
    src=[]
    for core in [FINITE,TRAD]:
        for name in ['src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h','src/gpgpu-sim/dtc-l1-common.h','src/abstract_hardware_model.cc']:src.append(m.facts(core/name))
        text=(core/'src/gpgpu-sim/gpu-sim.cc').read_text()
        m.need('const unsigned cap = m_shader_config->dtc_l1_lower_outstanding_cap;' in text and 'assert(cap > 0);' in text,'both existing Core lower cap semantics')
    receipt=dict(status='PASS_CPU_PROPOSAL_ONLY',arms=arms,common_required_options=required,declared_effective_option_differences=differences,config_sources=list(copies.values()),core_source_bindings=src,common_lower_cap=dict(value=32768,legal=True,evidence='Both frozen Core gpu-sim.cc register OPT_UINT32 and acquire_lower_request asserts cap>0; 32768 is representable. Finite primary and TRAD96 Btree template already explicitly32768. New B16-N/TC80-N overlay makes common32768 explicit; no old attempt modified.'),
      same128_comparison='IO128 vs OO128: same128 active PIB, fixed qualified finite Core; do not claim equal total metadata/area',
      activation='NOT_AUTHORIZED_IN_CPU_WINDOW; ChatGPT science review of G0-G3 then original A sole authority must independently accept/register UUID attempts; this file is not an A manifest',
      ratios='only new B16-N/TC80-N/TRAD96-C+ vs new IO/OO; IO128 vs OO128; no old-input denominators, GM12, equal-area or native claim',
      stop='Any G0-G3 science failure, cap illegality, runtime mismatch, regression or ranking reversal: retain failure and STOP expansion; no tuning/third interpretation',
      launches=0,performance_results='NOT_RUN',tool=m.facts(Path(__file__)))
    m.save(m.PACK/'SIX_ARM_PROPOSAL.json',receipt);print('Six fixed CPU-only arm proposals; cap32768/common platform PASS')
if __name__=='__main__':main()
