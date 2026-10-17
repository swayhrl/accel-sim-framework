"""Exact unifiedfb runtime/profile allowlist; independent qualification remains mandatory."""
import hashlib,json
from pathlib import Path
IDENTITY={'core_source_commit':'9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f','framework_source_commit':'8ab6013ea90755fdc74819e92090c2de50f4f199','binary_sha256':'fb67448d08818bc8cbe72961580e8340f0e6f337a4df95e7c8ee9468472953f7'}
LOCAL={'B16_OFF':(0,0,0),'U_OFF':(0,0,0),'I_WB':(1,0,0),'I_META':(0,1,0),'I_WB_META':(1,1,0),'I_READ_HIT':(0,0,1),'S64':(0,0,0),'U_CAP16':(0,0,0),'P2_B16':(0,0,0),'P2_U_WB16':(0,0,0),'I_MEM_ALL_DATA':(0,0,0)}
def require(v,m):
 if not v:raise ValueError(m)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def expected(profile):
 require(profile in LOCAL,'Undeclared unified profile')
 wb,meta,read=map(bool,LOCAL[profile]);u=profile in ('U_OFF','U_CAP16','P2_U_WB16');s64=profile=='S64';all_data=profile=='I_MEM_ALL_DATA'
 f={'finite_wbuf':not all_data,'unified_wb':u,'tvd':False,'ro':False,'adaptive_policy':False,'wbuf_entries':16,'payload_capacity_per_slice':None if wb or all_data else 1168,'bank_count':None if all_data else 4,'ops_per_bank_cycle':None if all_data else(2 if profile.startswith('P2_') else 1),'static_s64':s64,'wb_local_cap':16 if profile=='U_CAP16' else 0,'bypass_capacity':80 if s64 else 128,'static_wb_capacity':None if wb or u or all_data else(64 if s64 else 16),'ideal_wb':wb,'ideal_meta':meta,'ideal_read_hit':read,'nominal_payload_capacity_per_slice':1168,'diagnostic_extra_payload_backing':wb,'wb_data_capacity_non_binding':wb,'nominal_static_wb_anchor':16}
 if all_data:f.update(i_mem_all_data=True,configured_finite_wbuf=True,nominal_background='B16_OFF',data_hierarchy='NOT_APPLICABLE',reference_ready_latency_physical_GPUcycles=1,instruction_fetch='NATIVE_UNCHANGED',numerical_SASS_output_validated=False)
 return f,{'wb':wb,'meta':meta,'read_hit':read,'mem_all_data':all_data}

def features(identity,profile):
 require(all(identity[k]==v for k,v in IDENTITY.items()),'Another binary/source has no unified scope')
 f,i=expected(profile);require(canonical(identity['feature_vector'])==canonical(f) and canonical(identity['ideal_vector'])==canonical(i),'Unqualified unified resource/ideal combination')

def overlay(profile):
 f,i=expected(profile);v={'-gpgpu_ep_l2_ideal_'+k:str(int(i[k])) for k in ['wb','meta','read_hit']}
 if profile=='S64':v['-gpgpu_ep_l2_static_s64']='1'
 if profile=='U_CAP16':v['-gpgpu_ep_l2_wb_local_cap']='16'
 if profile.startswith('P2_'):v['-gpgpu_ep_l2_bank_ops']='2'
 if profile=='I_MEM_ALL_DATA':v['-gpgpu_ep_l2_i_mem_all_data']='1'
 return v

def validate(spec,release,configs,assets,review):
 from headroom_config import H0,options,PARALLEL_EXPERIMENT,PARALLEL_COORDINATION
 profile=spec['producer_profile'];features(spec['identity'],profile)
 require(spec['scientific_scope']==('ALL_DATA_REFERENCE_V1' if profile=='I_MEM_ALL_DATA' else 'UNIFIED_NATIVE_V1'),'Wrong actual reference/physical scope')
 require(review['qualification_kind']=='UNIFIED_NATIVE_V1' and review['status']=='INDEPENDENT_CONFIG_PASS' and review['coordination_commit']==PARALLEL_COORDINATION,'New runtime is not independently qualified')
 require(spec['experiment_id']==review['experiment_id']==PARALLEL_EXPERIMENT and spec['regime']==('P2' if profile.startswith('P2_') else 'H0'),'Wrong experiment/background')
 row=review['profiles'][profile];require(configs==row['ordered_configs'] and assets==row['auxiliary_assets'] and spec['environment']==row['environment'] and spec['identity']['runtime_config_sha256']==row['runtime_config_sha256'],'Ordered config/input environment identity changed')
 require(hashlib.sha256(canonical({'ordered_configs':configs[:5],'auxiliary_assets':assets,'environment':spec['environment']})).hexdigest()==H0[spec['mode']],'Original physical5-layer base changed')
 require(options([p['path'] for p in spec['configs'][5:]])==overlay(profile),'Non-whitelisted runtime overlay')
 require(options([p['path'] for p in spec['configs']])==row['effective_options'],'Effective config differs')
 for ev in review['evidence']:require(digest(ev['path'])==ev['sha256'],'Independent source qualification changed')
 require(review['all_eleven_gates_passed'] and review['native_all_off_equivalence']=='PASS' and review['independent_mode_semantics_passed'],'New scope gates incomplete')
 return {'experiment_id':PARALLEL_EXPERIMENT,'regime':spec['regime'],'profile':profile,'scientific_scope':spec['scientific_scope'],'condition_qualification_sha256':release['downstream_config_qualification']['sha256'],'runtime_config_sha256':row['runtime_config_sha256']}

def runtime_dump(raw,spec):
 profile=spec['producer_profile'];features(spec['identity'],profile);f,i=expected(profile)
 want=overlay(profile);want.update({'-gpgpu_ep_l2_i_mem_all_data':str(int(i['mem_all_data'])),'-gpgpu_ep_l2_static_s64':str(int(f['static_s64'])),'-gpgpu_ep_l2_wb_local_cap':str(f['wb_local_cap']),'-gpgpu_ep_l2_bank_ops':str(2 if profile.startswith('P2_') else 1),'-gpgpu_ep_l2_ft_mode':'2' if f['unified_wb'] else'1','-gpgpu_ep_l2_wbuf_entries':'16','-gpgpu_ep_l2_wad_entries':'128','-gpgpu_ep_l2_payload_mode':'2','-gpgpu_ep_l2_descriptor_pool_size':'512','-gpgpu_ep_l2_descriptor_per_line_cap':'32','-gpgpu_clock_domains':'1132.0:1132.0:1132.0:850.0','-gpgpu_l2_rop_latency':'160','-dram_latency':'100','-gpgpu_simple_dram_model':'0','-gpgpu_dram_partition_queues':'64:128:64:64','-gpgpu_frfcfs_dram_sched_queue_size':'128','-gpgpu_dram_return_queue_size':'192'})
 actual={};clocks=[]
 for line in Path(raw).open():
  if line.startswith('-'):
   p=line.split('#',1)[0].split(None,1)
   if len(p)==2 and p[0] in want:require(p[0] not in actual,'Repeated native option');actual[p[0]]=p[1].strip()
  if line.startswith('GPGPU-Sim uArch: clock freqs: '):clocks.append([float(v) for v in line.split('freqs: ',1)[1].split(':')])
 require(actual==want and clocks==[[1132e6,1132e6,1132e6,850e6]],'Actual unified native options/clocks differ')
 return {'status':'ACTUAL_UNIFIED_OPTIONS_CLOCKS_MATCH','options':actual,'clock_frequencies_Hz':clocks[0]}
