"""Positive local-ideal scope in the existing physical-path runner and V2."""
import hashlib,json
from pathlib import Path
from registry import canonical
from headroom_config import H0,options,PARALLEL_EXPERIMENT,PARALLEL_COORDINATION

IDENTITY={'core_source_commit':'a26b3566744abd83c0c0ae2ce43be34e796206e7','framework_source_commit':'8ab6013ea90755fdc74819e92090c2de50f4f199','binary_sha256':'37dc77943e7667327069faa203139b089bcb88c7d38e6347602928e3ba6cd0b5'}
PROFILE_BITS={'B16_OFF':(False,False,False),'U_OFF':(False,False,False),'I_WB':(True,False,False),'I_META':(False,True,False),'I_WB_META':(True,True,False),'I_READ_HIT':(False,False,True)}
COMMON={'finite_wbuf','unified_wb','tvd','ro','adaptive_policy','wbuf_entries','payload_capacity_per_slice','bank_count','ops_per_bank_cycle'}
EXTRA={'ideal_wb','ideal_meta','ideal_read_hit','nominal_payload_capacity_per_slice','diagnostic_extra_payload_backing','wb_data_capacity_non_binding'}

def require(value,message):
 if not value:raise ValueError(message)

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def features(identity,profile):
 require(all(identity[k]==v for k,v in IDENTITY.items()),'Local ideal has no independent scope for another runtime')
 f=identity['feature_vector'];i=identity['ideal_vector'];require(set(f)==COMMON|EXTRA and profile in PROFILE_BITS,'Incomplete local feature vector/profile')
 wb,meta,read=PROFILE_BITS[profile];require(i=={'wb':wb,'meta':meta,'read_hit':read},'Wrong local ideal vector')
 require(f=={'finite_wbuf':True,'unified_wb':profile=='U_OFF','tvd':False,'ro':False,'adaptive_policy':False,'wbuf_entries':16,'payload_capacity_per_slice':None if wb else 1168,'bank_count':4,'ops_per_bank_cycle':1,'ideal_wb':wb,'ideal_meta':meta,'ideal_read_hit':read,'nominal_payload_capacity_per_slice':1168,'diagnostic_extra_payload_backing':wb,'wb_data_capacity_non_binding':wb},'Unqualified local resources/feature combination')


def validate(spec,release,configs,assets,review):
 require(spec.get('scientific_scope')=='LOCAL_IDEAL_NATIVE_V1' and review['qualification_kind']=='LOCAL_IDEAL_NATIVE_V1','Wrong local scope')
 require(review['status']=='INDEPENDENT_CONFIG_PASS' and review['coordination_commit']==PARALLEL_COORDINATION,'Local config not qualified')
 require(spec.get('experiment_id')==review['experiment_id']==PARALLEL_EXPERIMENT and spec.get('regime')=='H0','Local campaign/background mismatch')
 features(spec['identity'],spec['profile']);row=review['profiles'][spec['profile']]
 require(spec['identity']['feature_vector']==row['feature_vector'] and spec['identity']['ideal_vector']==row['ideal_vector'],'Local producer vector differs')
 require(configs==row['ordered_configs'] and assets==row['auxiliary_assets'] and spec['environment']==row['environment'] and spec['identity']['runtime_config_sha256']==row['runtime_config_sha256'],'Local ordered content identity differs')
 require(len(configs)==6 and hashlib.sha256(canonical({'ordered_configs':configs[:5],'auxiliary_assets':assets,'environment':spec['environment']})).hexdigest()==H0[spec['mode']],'Local original5-layer base changed')
 expected={'-gpgpu_ep_l2_ideal_'+k:str(int(v)) for k,v in spec['identity']['ideal_vector'].items()}
 # CLI uses read_hit/meta/wb exactly; preserve all other native options.
 require(options([spec['configs'][5]['path']])==expected,'Local overlay has extra/missing option')
 require(options([x['path'] for x in spec['configs']])==row['effective_options'],'Local actual config differs')
 for e in review['evidence']:require(digest(e['path'])==e['sha256'],'Local independent evidence changed')
 require(review['all_eleven_gates_passed'] is True and review['native_all_off_equivalence']=='PASS' and review['independent_mode_semantics_passed'] is True,'New runtime scope incomplete')
 return {'experiment_id':PARALLEL_EXPERIMENT,'regime':'H0','profile':spec['profile'],'condition_qualification_sha256':release['downstream_config_qualification']['sha256'],'runtime_config_sha256':row['runtime_config_sha256'],'scientific_scope':'LOCAL_IDEAL_NATIVE_V1'}


def runtime_dump(raw,spec):
 features(spec['identity'],spec['profile']);expected={'-gpgpu_ep_l2_ideal_'+k:str(int(v)) for k,v in spec['identity']['ideal_vector'].items()}
 expected.update({'-gpgpu_ep_l2_ft_mode':'2' if spec['mode']=='U_WB16' else '1','-gpgpu_ep_l2_wbuf_entries':'16','-gpgpu_ep_l2_wad_entries':'128','-gpgpu_ep_l2_payload_mode':'2','-gpgpu_ep_l2_descriptor_pool_size':'512','-gpgpu_ep_l2_descriptor_per_line_cap':'32','-gpgpu_clock_domains':'1132.0:1132.0:1132.0:850.0','-gpgpu_l2_rop_latency':'160','-dram_latency':'100','-gpgpu_simple_dram_model':'0','-gpgpu_dram_partition_queues':'64:128:64:64','-gpgpu_frfcfs_dram_sched_queue_size':'128','-gpgpu_dram_return_queue_size':'192'})
 actual={};clocks=[]
 for line in Path(raw).open():
  if line.startswith('-'):
   p=line.split('#',1)[0].split(None,1)
   if len(p)==2 and p[0] in expected:require(p[0] not in actual,'Repeated local native option');actual[p[0]]=p[1].strip()
  if line.startswith('GPGPU-Sim uArch: clock freqs: '):clocks.append([float(x) for x in line.split('freqs: ',1)[1].split(':')])
 require(actual==expected and clocks==[[1132e6,1132e6,1132e6,850e6]],'Actual local options/clocks differ')
 return {'status':'ACTUAL_LOCAL_OPTIONS_CLOCKS_MATCH','options':actual,'clock_frequencies_Hz':clocks[0]}


def input_source_identity(spec,release):
 binding=release.get('retained_input_scope')
 if binding is None:return {k:spec['identity'][k] for k in IDENTITY},release.get('producer_publication_commit')
 require(digest(binding['path'])==binding['sha256'],'Retained input-scope evidence changed')
 report=json.loads(Path(binding['path']).read_text());require(report['status']=='UNCHANGED_COMPLETE_INPUT_PARSER_AND_CONTENT_SCOPE' and report['new_source_identity']=={k:spec['identity'][k] for k in IDENTITY},'Wrong new input-scope binding')
 require(report['source_trees'] and all(v['old']==v['new'] for v in report['source_trees']),'Input parser/opcode semantics changed')
 require(spec['atomic_input_scope']['sha256'] in report['retained_atomic_report_sha256'],'Complete input proof not explicitly retained')
 if spec.get('native_legacy_semantic_proof'):require(spec['native_legacy_semantic_proof']['sha256']==report['retained_native_byte_proof_sha256'],'Wrong retained native-byte proof')
 require(report['new_host_prefill_and_read_reference_tests_passed'] is True,'New host/reference semantics untested')
 return report['original_source_identity'],report['original_producer_publication']
