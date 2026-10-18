"""Exact independently qualified f0af finite-P1 OFF/MQ2 scope only."""
import hashlib,json
from pathlib import Path
from unified_scope import expected as old_layout

PARALLEL='EPL2_PARALLEL_POTENTIAL_20261017_V1'
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()

IDENTITY={'core_source_commit':'84359d4ba492acb639a2092fa271e9169038bf7d','framework_source_commit':'197741be9be9b8e390a557d639503b416d8e95f0','binary_sha256':'f0af8515057e315af708a0e3c2fde4a3098b0c0fb3f7014471d8d8c9426f1f30'}
AUTHORITY='9a161b700ae2d17470fe7b08fc16725b3ef6317c'
SCOPE='FINITE_SERVICE_NATIVE_V1'
PROFILES={f'{mode}_mq2_{on}':(base,on) for mode,base in [('B16','B16_OFF'),('S64','S64'),('Unified','U_OFF')] for on in [0,1]}
def require(ok,msg):
 if not ok:raise ValueError(msg)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def expected(profile):
 require(profile in PROFILES,'Undeclared/unqualified service profile (RG1/combined/Ideal/P2 excluded)');base,on=PROFILES[profile];f,i=old_layout(base);return {**f,'mq2':bool(on),'rg1':False},i
def features(identity,profile):
 require(all(identity[k]==v for k,v in IDENTITY.items()),'Another source/binary has no finite-service qualification');f,i=expected(profile);require(canonical(identity['feature_vector'])==canonical(f) and canonical(identity['ideal_vector'])==canonical(i),'Unqualified service/layout feature combination')
def validate(spec,release,configs,assets,review):
 from headroom_config import H0,options
 profile=spec['producer_profile'];features(spec['identity'],profile);base,on=PROFILES[profile];require(spec['scientific_scope']==SCOPE and review['qualification_kind']==SCOPE and review['status']=='INDEPENDENT_CONFIG_PASS' and review['coordination_commit']==AUTHORITY,'Service scope not independently qualified')
 require(spec['experiment_id']==review['experiment_id']==PARALLEL and spec['profile']==base and spec['regime']==('SERVICE_MQ2' if on else 'SERVICE_OFF'),'Wrong service campaign/profile/condition')
 row=review['profiles'][profile];require(configs==row['ordered_configs'] and assets==row['auxiliary_assets'] and spec['environment']==row['environment'] and spec['identity']['runtime_config_sha256']==row['runtime_config_sha256'],'Service ordered asset/environment identity changed')
 require(hashlib.sha256(canonical({'ordered_configs':configs[:5],'auxiliary_assets':assets,'environment':spec['environment']})).hexdigest()==H0[spec['mode']],'Frozen physical H0 base changed')
 extra=options([v['path'] for v in spec['configs'][5:]]);want={'-gpgpu_ep_l2_ideal_'+k:'0' for k in ['wb','meta','read_hit']};want.update({'-gpgpu_ep_l2_mq2':str(on),'-gpgpu_ep_l2_rg1':'0'})
 if base=='S64':want['-gpgpu_ep_l2_static_s64']='1'
 require(extra==want,'Non-whitelisted finite service overlay');require(options([v['path'] for v in spec['configs']])==row['effective_options'],'Effective service config differs')
 for e in review['evidence']:require(digest(e['path'])==e['sha256'],'Independent service evidence changed')
 require(review['all_eleven_gates_passed'] is True and review['native_all_off_equivalence']=='PASS' and review['independent_mode_semantics_passed'] is True,'Eleven service gates incomplete')
 return {'scientific_scope':SCOPE,'experiment_id':PARALLEL,'regime':spec['regime'],'profile':profile,'condition_qualification_sha256':release['downstream_config_qualification']['sha256'],'runtime_config_sha256':row['runtime_config_sha256']}
def runtime_dump(raw,spec):
 features(spec['identity'],spec['producer_profile']);f=spec['identity']['feature_vector'];want={'-gpgpu_ep_l2_mq2':str(int(f['mq2'])),'-gpgpu_ep_l2_rg1':'0','-gpgpu_ep_l2_bank_ops':'1','-gpgpu_ep_l2_static_s64':str(int(f['static_s64'])),'-gpgpu_ep_l2_wb_local_cap':'0','-gpgpu_ep_l2_i_mem_all_data':'0','-gpgpu_ep_l2_ft_mode':'2' if f['unified_wb'] else '1','-gpgpu_ep_l2_wbuf_entries':'16','-gpgpu_ep_l2_wad_entries':'128','-gpgpu_ep_l2_payload_mode':'2','-gpgpu_ep_l2_descriptor_pool_size':'512','-gpgpu_ep_l2_descriptor_per_line_cap':'32','-gpgpu_clock_domains':'1132.0:1132.0:1132.0:850.0','-gpgpu_l2_rop_latency':'160','-dram_latency':'100','-gpgpu_simple_dram_model':'0','-gpgpu_dram_partition_queues':'64:128:64:64','-gpgpu_frfcfs_dram_sched_queue_size':'128','-gpgpu_dram_return_queue_size':'192',**{'-gpgpu_ep_l2_ideal_'+k:'0' for k in ['wb','meta','read_hit']}}
 actual={};clocks=[]
 for line in Path(raw).open():
  if line.startswith('-'):
   parts=line.split('#',1)[0].split(None,1)
   if len(parts)==2 and parts[0] in want:require(parts[0] not in actual,'Repeated service native option');actual[parts[0]]=parts[1].strip()
  if line.startswith('GPGPU-Sim uArch: clock freqs: '):clocks.append([float(v) for v in line.split('freqs: ',1)[1].split(':')])
 require(actual==want and clocks==[[1132e6,1132e6,1132e6,850e6]],'Actual finite service clocks/options differ');return {'status':'ACTUAL_FINITE_SERVICE_OPTIONS_CLOCKS_MATCH','options':actual,'clock_frequencies_Hz':clocks[0]}
def terminal_services(raw,spec):
 """Cumulative instrumentation is associated with its native terminal clock."""
 import re
 features(spec['identity'],spec['producer_profile']);frames={};clock=None
 for line in Path(raw).open():
  match=re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*',line)
  if match:clock=int(match[1])
  if not line.startswith('EPL2SERVICEV1|'):continue
  parts=line.strip().split('|');row={k:int(v) for k,v in (p.split('=',1) for p in parts[2:])};require(clock is not None,'Service counters lack native cumulative clock');kind=parts[1];key=(clock,kind,row['slice'],row.get('bank',row.get('client',-1)));require(key not in frames or frames[key]==row,'Conflicting service snapshot');frames[key]=row
 final={(kind,sid,sub):row for (cycle,kind,sid,sub),row in frames.items() if cycle==clock};require(set(final)=={(k,s,n) for s in range(64) for k,ns in [('MQ2',[-1]),('RG1_BANK',range(4)),('RG1_CLIENT',range(7))] for n in ns},'Missing exact64-slice cumulative service counters')
 for (kind,sid,sub),row in final.items():
  if kind=='MQ2':require(row['enabled']==int(spec['identity']['feature_vector']['mq2']) and row['window']==2 and row['lower_enqueues_per_cycle']==1 and row['bypasses']<=row['wb_bank_waits'] and (row['enabled'] or row['bypasses']==0),'MQ2 terminal counter/limit mismatch')
  if kind=='RG1_BANK':require(row['enabled']==0 and row['recovered_grants']==0,'Unqualified RG1 activity')
 return {kind:{str(sid)+(':'+str(sub) if sub>=0 else ''):row for (k,sid,sub),row in final.items() if k==kind} for kind in ['MQ2','RG1_BANK','RG1_CLIENT']}
