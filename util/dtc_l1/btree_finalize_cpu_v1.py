#!/usr/bin/env python3
"""Finalize the CPU proof only after all independent receipts close; no launch."""
from datetime import datetime,timezone
import hashlib,json,os,subprocess
from pathlib import Path
import btree_format_stability_cpu_v1 as m
from btree_pair_proposal_cpu_v1 import FINITE,TRAD

def main():
    pre=json.loads((m.PACK/'PRECHECK_RECEIPT.json').read_text())
    deriv=json.loads((m.PACK/'G1_DERIVATION.json').read_text())
    ref=json.loads((m.PACK/'REFERENCE_DECODER.json').read_text())
    consumer=json.loads((m.PACK/'BTREE_CONSUMER_EQUIVALENCE.json').read_text())
    proposal=json.loads((m.PACK/'SIX_ARM_PROPOSAL.json').read_text())
    two=json.loads((m.PACK/'2D_FEASIBILITY_RECEIPT.json').read_text())
    m.need(all(v['status']=='PASS' for v in [pre,deriv,ref,consumer]),'G0-G2 receipts')
    m.need(proposal['status']=='PASS_CPU_PROPOSAL_ONLY' and len(proposal['arms'])==6 and proposal['common_lower_cap']['legal'],'six-arm proposal closed')
    m.need(m.sha(Path(ref['tool']['path']))==ref['tool']['sha256'],'reference proof frozen tool')
    m.need(m.sha(m.ROOT/'proof_source_g1_v1.py')==deriv['tool']['sha256'],'first derivation proof source retained')
    for p in pre['protected']:
        m.need(m.sha(Path(p['path']))==p['sha256'],('protected immutable',p['path']))
    for p in pre['originals']:
        m.need(m.sha(Path(p['path']))==p['sha256'],('original immutable',p['path']))
    for core,commit in [(FINITE,'6fba0136f8465b59fe5858a950fa39efb265f654'),(TRAD,'6582b9d171330d88b17e8d5294c97704229e3823')]:
        m.need(m.git(core,'rev-parse','HEAD')==commit,'frozen Core')
        for name in ['src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h','src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/dtc-l1-common.h','src/abstract_hardware_model.cc']:
            m.need(m.git(core,'rev-parse',f'HEAD:{name}')==m.git(core,'hash-object',name),'Core source equals frozen commit')
    for name in ['trace_parser.cc','trace_parser.h','warp_trace_stream.h']:
        p='gpu-simulator/trace-parser/'+name
        m.need(m.git(m.FROZEN,'rev-parse','HEAD:'+p)==m.git(m.FROZEN,'hash-object',p),'production parser equals frozen framework commit')
    for r in ref['kernels']:
        counts=r['counts'];m.need(counts['max_global_128b_lines']<=2 and counts['max_global_32b_sectors']<=5,'observed response bounds')
        m.need(set(r['memory_modes'])<={'0','1'},'mode domain')
        m.need(counts.get('memory_width_4',0)+counts.get('memory_width_8',0)==counts['memory_records'],'observed data widths')
    core=dict(status='PASS_STATIC_INPUT_COMPATIBILITY',proof_scope='Frozen parser full read plus independent all-record domain proof and exact frozen Core source compatibility; no Core/simulator execution',
      framework=m.git(m.FROZEN,'rev-parse','HEAD'),parser_source=consumer['frozen_parser'],
      source_files=proposal['core_source_bindings'],runtimes={a:dict(core=s['core'],framework=s['build_framework'],runtime=s['runtime']) for a,s in proposal['arms'].items()},
      observed=dict(memory_records=2011551,widths_bytes=[4,8],modes=[0,1],max_128b_references_per_instruction=2,max_32b_sectors_per_instruction=5,unaligned_or_cross_sector_lane_accesses=0,shared_local_texture_atomic_TMA_records=0,changed_instruction_width=4,changed_active_lanes=1),
      evidence=['trace_driven.cc:369-408 copies memadd_info width/addresses, maps LDG to CACHE_ALL/global; STG to existing ordinary store path; modified LDG.E.SYS consumes no imm',
                'Both Core abstract_hardware_model.cc memory_coalescing_arch handles widths1,2,4,8,16; all actual lanes aligned and within single32B sector and128B line',
                'dtc-l1-common.h::group_128b_references uses64bit line base and4bit sector mask; response_sector_is_new bounds sector<4; observed at most2 references and5 total sectors, each line <=4 sectors',
                'OO RefCount max8191 from13bits;128 live PIB entries and unique physical reference per entry bound each line <=128; IO128/256 and pool640/alloc4 remain the qualified paths',
                'shader.h::init overrides conventional cache MSHR entries with dtc_l1_mshr_entries for PAPER_BASE; literal cache config512 is not the effective32/512 conventional MSHR bound',
                'Finite quota default1 for create/inject/refill/retire; collect4 sectors/cycle, tag4 total1/bank, allocation4, coalescer32; no new side path introduced'],
      runtime_credit_reference_physical_drain_audits='NOT_RUN; required on any later A-owned natural-terminal attempt',native_output_equivalence='NOT_PROVEN')
    m.save(m.PACK/'CORE_COMPATIBILITY.json',core)
    files=[]
    for name in m.ORIGINAL:
        p=m.ROOT/'candidate'/name;m.need(m.sha(p)==next(x['sha256'] for x in deriv['members'] if Path(x['path']).name==name),'candidate identity freeze')
        p.chmod(0o444);files.append(dict(name=name,bytes=p.stat().st_size,sha256=m.sha(p)))
    (m.ROOT/'candidate').chmod(0o555)
    contract=dict(schema='BTREE_CONDITIONAL_E_LIST_BUNDLE_V1',interpretation='BTREE_FIXED_PC1C40_CONDITIONAL_FULL_E_LIST_TO_P_LIST_V1',
      conditional_producer=dict(revision='0e2fddcdef37fc59ad786553892b75567a5f2cdb',source_sha256='8dcb5ad444a6cb6a3cfb1271308e27b8395ee16afae0135703b3ac3820b09d4a',claim='COMPATIBLE_BUT_CAPTURE_UNBOUND'),
      transformation='all fixed6000 original member1 PC1c40 LDG.E.SYS width4 mode0 singleP/full32 records; E=ffffffff; address raw_word[physical active lane]; serialize same P with one mode0 address; all other bytes preserved',
      original_sha256=m.ORIGINAL,files=files,kernel_order=['kernel-1.traceg','kernel-2.traceg'],kernel_names=['findRangeK','findK'],ROI='complete ordered kernels; no truncation or warmup selection',expected_active_thread_instructions=444467849,expected_warp_records=15609327)
    bundle=hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    tools=[m.facts(p) for p in sorted((m.REPO/'util/dtc_l1').glob('btree_*_v1.*')) if p.suffix in ('.py','.cc')]
    identity=dict(status='FROZEN_INDEPENDENT_DERIVED_INPUT',bundle_sha256=bundle,bundle_hash_schema='SHA256(UTF8 json.dumps(identity_contract,sort_keys=True,separators=(comma,colon)))',identity_contract=contract,owned_input_directory=str(m.ROOT/'candidate'),readonly_modes='files0444 directory0555; byte SHA identity binding, not filesystem immutability against administrator',capture_equivalence='NOT_PROVEN',native_equivalence='NOT_PROVEN',consumer=consumer['frozen_parser'],cores=core['runtimes'],proof_tools=tools,derivation_initial_source=m.facts(m.ROOT/'proof_source_g1_v1.py'),input_members_not_in_Git=True,original_results_and_status='UNCHANGED_FORMAT_APPLICABILITY_REVIEW_PENDING')
    m.save(m.PACK/'INPUT_IDENTITY.json',identity)
    sources=[m.FROZEN/'gpu-simulator/trace-parser'/n for n in ['trace_parser.cc','trace_parser.h','warp_trace_stream.h']]+[m.FROZEN/'util/tracer_nvbit/tracer_tool/tracez_format.h',Path('/usr/local/cuda-11.8/include/cuda_runtime.h'),Path('/usr/local/cuda-11.8/include/vector_types.h')]
    m.save(m.PACK/'BUILD_RECEIPT.json',dict(status='PASS',compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],command='g++ -std=c++17 -O2 -I/usr/local/cuda-11.8/include -I/workspace/worktrees/accel-sim-decoupled-l1-fast64/gpu-simulator/trace-parser -I/workspace/worktrees/accel-sim-decoupled-l1-fast64/util/tracer_nvbit/tracer_tool util/dtc_l1/btree_production_parser_cpu_v1.cc /workspace/worktrees/accel-sim-decoupled-l1-fast64/gpu-simulator/trace-parser/trace_parser.cc -lcrypto -lzstd -pthread -o /workspace/dtc-btree-format-stability-cpu-174-v1/btree-production-parser-cpu',sources=[m.facts(p) for p in sources],cpu_driver_binary=m.facts(m.ROOT/'btree-production-parser-cpu'),linkage=subprocess.check_output(['ldd',str(m.ROOT/'btree-production-parser-cpu')],text=True),warnings='existing warp_trace_stream.h ignores fread return values on unused .tracez path; compiled production source unchanged',cuda_runtime_calls=0,simulator_linked=False,actual_parser_translation_unit_complete=True))
    after=[]
    for r in pre['existing_processes']:
        p=Path(f'/proc/{r["pid"]}/stat')
        if p.exists():
            ticks=p.read_text().rsplit(')',1)[1].split()[19];m.need(ticks==r['start_ticks'],'existing process not restarted');after.append(dict(pid=r['pid'],start_ticks=ticks,state='SAME_EXISTING_PROCESS'))
        else:after.append(dict(pid=r['pid'],state='EXITED_EXTERNALLY; this task issued no process control'))
    for r in pre['locks']:m.need(Path(r['path']).stat().st_ino==r['inode'],'A lock inode preserved')
    m.save(m.PACK/'POSTCHECK_RECEIPT.json',dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),protected_files=[m.facts(Path(p['path'])) for p in pre['protected']],originals_rehashed=pre['originals'],original_A_head_now=m.git(m.A,'rev-parse','HEAD'),frozen_B_head_now=m.git(m.B,'rev-parse','HEAD'),existing_processes=after,locks_acquired_by_this_task=0,A_registry_writes=0,original_trace_writes=0,runtime_source_or_binary_writes=0,new_GPU_runs=0,new_simulator_runs=0,other_lanes_resumed=False))
    gates=dict(status='DERIVED_INPUT_ADMITTED_FOR_BTRE_E_LIST_CONTRACT',gates={'G0':'PASS','G1':'PASS','G2':'PASS','G3':'PASS'},bundle_sha256=bundle,
      scope='CPU qualification of this explicit conditional derived-input contract only; ChatGPT review pending; no historical capture/native certification; original Btree pending unchanged',
      proof_receipts={n:m.sha(m.PACK/n) for n in ['PRECHECK_RECEIPT.json','G1_DERIVATION.json','BTREE_DERIVATION_AUDIT.tsv','REFERENCE_DECODER.json','BTREE_CONSUMER_EQUIVALENCE.json','CORE_COMPATIBILITY.json','INPUT_IDENTITY.json','BUILD_RECEIPT.json','POSTCHECK_RECEIPT.json','SIX_ARM_PROPOSAL.json','ENGINEERING_FAILURE_HISTORY.json']},
      two_dimensional=dict(status=two['status'],whole_kernel_model='NOT_CLOSED_STOP_BOUNDED_EXTENSION',new_input='NOT_RUN_NOT_AUTHORIZED'),
      performance='NOT_RUN',A_registration='NOT_RUN_REQUIRES_ORIGINAL_A_ACCEPTANCE_AFTER_SCIENCE_REVIEW',max_proposed_arms=6,run_authority='NONE_IN_THIS_WINDOW',gpu_runs=0,simulator_runs=0,old_Hotspot_HOLD='UNCHANGED',LUD='NOT_TOUCHED')
    m.save(m.PACK/'GATE.json',gates);print(json.dumps(dict(status=gates['status'],bundle_sha256=bundle,gates=gates['gates'])))
if __name__=='__main__':main()
