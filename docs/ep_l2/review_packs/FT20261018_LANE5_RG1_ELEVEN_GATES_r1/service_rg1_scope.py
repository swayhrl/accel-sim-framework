"""Separately qualified RG1-only finite-P1 profiles; no MQ2 qualification inheritance."""
import hashlib
from service_scope import IDENTITY,AUTHORITY,PARALLEL,canonical,digest,require,_runtime_dump,_terminal_services
from unified_scope import expected as old_layout

SCOPE='FINITE_SERVICE_RG1_NATIVE_V1'
PROFILES={f'{name}_rg1_1':base for name,base in [('B16','B16_OFF'),('S64','S64'),('Unified','U_OFF')]}
def expected(profile):
 require(profile in PROFILES,'Undeclared RG1 ON profile; combined/Ideal/P2/quota excluded');f,i=old_layout(PROFILES[profile]);return {**f,'mq2':False,'rg1':True},i
def features(identity,profile):
 require(all(identity[k]==v for k,v in IDENTITY.items()),'Different RG1 runtime/source');f,i=expected(profile);require(canonical(identity['feature_vector'])==canonical(f) and canonical(identity['ideal_vector'])==canonical(i),'RG1 resource/single-factor vector mismatch')
def validate(spec,release,configs,assets,review):
 from headroom_config import H0,options
 profile=spec['producer_profile'];features(spec['identity'],profile);base=PROFILES[profile];require(spec['scientific_scope']==review['qualification_kind']==SCOPE and review['status']=='INDEPENDENT_CONFIG_PASS' and review['coordination_commit']==AUTHORITY,'RG1 is not separately qualified')
 require(spec['experiment_id']==review['experiment_id']==PARALLEL and spec['profile']==base and spec['regime']=='SERVICE_RG1','Wrong RG1 campaign/mode/condition');row=review['profiles'][profile]
 require(configs==row['ordered_configs'] and assets==row['auxiliary_assets'] and spec['environment']==row['environment'] and spec['identity']['runtime_config_sha256']==row['runtime_config_sha256'],'RG1 complete config/environment content changed')
 require(hashlib.sha256(canonical({'ordered_configs':configs[:5],'auxiliary_assets':assets,'environment':spec['environment']})).hexdigest()==H0[spec['mode']],'RG1 frozen physical base changed')
 want={'-gpgpu_ep_l2_ideal_'+k:'0' for k in ['wb','meta','read_hit']};want.update({'-gpgpu_ep_l2_mq2':'0','-gpgpu_ep_l2_rg1':'1'})
 if base=='S64':want['-gpgpu_ep_l2_static_s64']='1'
 require(options([v['path'] for v in spec['configs'][5:]])==want and options([v['path'] for v in spec['configs']])==row['effective_options'],'Non-whitelisted RG1 overlay/effective config')
 for ev in review['evidence']:require(digest(ev['path'])==ev['sha256'],'Independent RG1 evidence changed')
 require(review['all_eleven_gates_passed'] is True and review['native_all_off_equivalence']=='PASS' and review['independent_mode_semantics_passed'] is True and review['actual_OFF_ON_ready_witnesses']==6,'RG1 gates or actual ready-path witnesses incomplete')
 return {'scientific_scope':SCOPE,'experiment_id':PARALLEL,'regime':'SERVICE_RG1','profile':profile,'condition_qualification_sha256':release['downstream_config_qualification']['sha256'],'runtime_config_sha256':row['runtime_config_sha256']}
def runtime_dump(raw,spec):features(spec['identity'],spec['producer_profile']);return _runtime_dump(raw,spec)
def terminal_services(raw,spec):features(spec['identity'],spec['producer_profile']);return _terminal_services(raw,spec)
