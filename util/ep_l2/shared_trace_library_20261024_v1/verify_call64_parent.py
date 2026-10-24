"""Independent terminal join; no simulator or GPU launch."""
from pathlib import Path
import hashlib,json,re,lzma
B=Path('/root/data/ep_l2_main_ada_call_pc64_compat_20261024_v1');O=B/'run/f29b01fff6504be2a10c4922b34c7808'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec_sha='2c51b73f601d0234062aaa765615406298a1c5356f9c94b6b663838a9ae610cb'
assert sha(B/'control/FROZEN_SPEC.json')==spec_sha
s=json.loads((B/'control/FROZEN_SPEC.json').read_text());q=json.loads((B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json').read_text())
assert q['spec_sha256']==spec_sha and sha(B/'control/NATIVE_PRELAUNCH_QUALIFICATION_R2.json')=='d630e62cc32400dca7168ae589635a36106470f23fe53c52b3b5a6c21a3f5887'
for p,digest in s['pinned_files'].items():assert sha(p)==digest,p
exit=json.loads((O/'EXIT.json').read_text());assert exit['exit_code']==0 and exit['stop_reason'] is None and exit['native_observed'] and exit['application_attempt_consumed']==1
raw=(O/'raw.log').read_text();assert sha(O/'raw.log')==exit['raw_sha256']
decoded=[]
for line in raw.splitlines():
    if line.startswith('ADA8_DECODE '):decoded.append(dict(x.split('=',1) for x in line.split()[1:]))
assert len(decoded)==75 and sum(int(x['mask'],16).bit_count() for x in decoded)==1932
aux=[x for x in decoded if x['aux']=='1'];source=[x for x in decoded if x['aux']=='0']
assert len(aux)==15 and len(source)==60 and sum(int(x['mask'],16).bit_count() for x in aux)==449
assert sum(int(x['mask'],16).bit_count() for x in decoded if x['space']=='8')==514
assert sum(x['op'].startswith('CALL.') for x in decoded)==3 and sum(x['op'].startswith('RET.') for x in decoded)==3
for x in decoded:
    assert int(x['pc'],16)>2**32
    if x['op'].startswith('CALL.'):assert x['src']==x['dst']==x['gpr_operands']=='0'
def counter(pattern):
    values=re.findall(pattern,raw,re.M);assert values,pattern;return int(values[-1])
assert counter(r'^gpu_tot_sim_insn\s*=\s*(\d+)')==1932
assert counter(r'^gpu_tot_issued_cta\s*=\s*(\d+)')==2
assert counter(r'^ctas_completed\s+(\d+)')==2
assert counter(r'^\s*L1C_total_cache_accesses\s*=\s*(\d+)')==18
assert counter(r'^\s*L1C_total_cache_misses\s*=\s*(\d+)')==11
assert counter(r'^\s*Total_core_cache_stats_breakdown\[CONST_ACC_R\]\[HIT\]\s*=\s*(\d+)')==7
assert counter(r'^gpgpu_n_mem_const\s*=\s*(\d+)')==6
config=Path(s['cases']['call65_pc64_v8_v1']['config']).read_text();assert re.search(r'^-gpgpu_perfect_inst_const_cache\s+0\s*$',config,re.M)
maps=json.loads((O/'NATIVE_PROCESS.json').read_text());actual_paths={x.split()[-1] for x in maps['maps'].splitlines() if len(x.split())>=6 and x.split()[-1].startswith('/')}
assert s['binary'] in actual_paths and any('core64/' in p and p.endswith('libcudart.so') for p in actual_paths)
for p in actual_paths:assert p in s['pinned_files'] and sha(p)==s['pinned_files'][p]
D=Path(s['cases']['call65_pc64_v8_v1']['trace_entry']).parent
grouped=next(D.glob('*.traceg.xz'));warps=[];current=None;ctas=0
with lzma.open(grouped,'rt') as f:
    for line in f:
        if line.startswith('thread block ='):ctas+=1
        elif line.startswith('warp ='):current=[];warps.append(current)
        elif re.match(r'^[0-9a-fA-F]{16}\s',line):
            t=line.split();n=int(t[2]);op=t[3+n];current.append((int(t[0],16),int(t[1],16),op,t[t.index('ADA8')+1:]))
assert ctas==2 and len(warps)==4 and sum(len(w) for w in warps)==60
assert sum(mask.bit_count() for w in warps for pc,mask,op,ext in w)==1483
base=min(pc for w in warps for pc,mask,op,ext in w);calls=returns=0
for w in warps:
    stack={lane:[] for lane in range(32)}
    for index,(pc,mask,op,ext) in enumerate(w):
        if not (op.startswith('CALL.') or op.startswith('RET.')):continue
        assert ext[2:4]==['-1','0'] and ext[5:7]==['0','0']
        kind=int(ext[7]);values=list(map(int,ext[8:]));lanes=[lane for lane in range(32) if mask>>lane&1]
        assert len(values)==len(lanes) and kind==(1 if op.startswith('CALL.') else 2)
        for lane,value in zip(lanes,values):
            next_pc=next(q for q,m,_,_ in w[index+1:] if m>>lane&1)
            assert next_pc==base+value
            if kind==1:stack[lane].append(pc+16);calls+=1
            else:assert stack[lane] and stack[lane].pop()==base+value;returns+=1
    assert not any(stack.values())
assert calls==returns==65
registry=json.loads(Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_text());row=registry['registered_future_requests'][s['request']]
assert row['spec_sha256']==spec_sha and row['consumed']==row['budget']==1
result={'status':'PARENT_INDEPENDENT_SCOPED_CALL64_TERMINAL_JOIN_PASS','request':s['request'],'run':str(O),'spec_sha256':spec_sha,'raw_sha256':sha(O/'raw.log'),'pinned_files_rehashed':len(s['pinned_files']),'saved_native_mapping_files_rehashed':{p:sha(p) for p in sorted(actual_paths)},'mapping_attestation_limit':'Saved process maps plus independent postrun exact frozen-file SHA; the original live hash list missed the late Core mapping. Do not claim complete live mapping hash sampling.','source_records':60,'source_active_lane_instances':1483,'aux_uops':15,'aux_active_lane_instances':449,'actually_issued_active_lane_uops':1932,'constant_lane_instances':514,'L1C_accesses':18,'L1C_misses':11,'L1C_hits':7,'constant_requests':6,'ctas_issued_and_completed':2,'physical_warps':4,'per_lane_call_targets_and_successors_independently_joined':calls,'per_lane_return_targets_and_frames_independently_joined':returns,'original_full64_pc_preserved':True,'source_PC_or_target_relocation':False,'hardware_performance_qualification':False,'scope':'Embedded REL CALL/RET in one code body; does not release CALL.ABS/JIT/multicontext/Graph/texture domains','application_attempt_consumed':1,'failed_case3_refunded':False}
(O/'PARENT_INDEPENDENT_TERMINAL_JOIN.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
