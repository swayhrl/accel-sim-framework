"""Private capacity-bound adapter for the exact four nonTag families.
Only one terminal allocation-gauge bound is parameterized in the legacy parser.
No historical file, parser global or runtime occupancy evidence is changed.
"""
from pathlib import Path
import hashlib,types
LEGACY_PATH=Path('/root/data/ep_l2_dtc_l1_native_v2/DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/ag6_strict.py')
LEGACY_SHA256='9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4'
ANCHOR='0 <= value("oo_physical_allocated") <= 640 * 64, "physical_640_per_SM_capacity"'
VARIANTS={
 'PHYS768_TAG64x8':dict(physical=768,oo_pib=128,perbank=1,total=4,token='PHYS768'),
 'PHYS1024_TAG64x8':dict(physical=1024,oo_pib=128,perbank=1,total=4,token='PHYS1024'),
 'OO_PIB192':dict(physical=640,oo_pib=192,perbank=1,total=4,token='PIB192'),
 'TAG4BANK_PERBANK2_TOTAL8':dict(physical=640,oo_pib=128,perbank=2,total=8,token='TAGSVC8')}
FIXED_OPTIONS={
 '-gpgpu_dtc_l1_mode':['3'],'-gpgpu_dtc_l1_finite_service':['1'],
 '-gpgpu_dtc_l1_logical_sets':['64'],'-gpgpu_dtc_l1_logical_ways':['8'],
 '-gpgpu_dtc_l1_tag_banks':['4'],'-gpgpu_dtc_l1_tag_hash_bankrow':['1'],
 '-gpgpu_dtc_l1_allocation_width':['4'],'-gpgpu_dtc_l1_ref_count_bits':['13'],
 '-gpgpu_dtc_l1_lower_outstanding_cap':['32768'],'-gpgpu_dtc_l1_pib_entries':['8'],
 '-gpgpu_dtc_l1_mshr_entries':['32'],'-gpgpu_dtc_l1_io_pib_entries':['256'],
 '-gpgpu_dtc_l1_progressive_wakeup':['0'],'-gpgpu_dtc_l1_invalidate_on_source_event':['0'],
 '-gpgpu_cache:dl1':['S:32:128:4,L:T:m:L:L,A:512:8,16:0,32'],
 '-gpgpu_n_clusters':['64'],'-gpgpu_n_cores_per_cluster':['1'],
 '-gpgpu_shader_core_pipeline':['2048:32'],'-gpgpu_clock_domains':['1410.0:1410.0:1410.0:850.0'],
 '-gpgpu_n_mem':['20'],'-gpgpu_n_sub_partition_per_mchannel':['2'],
 '-gpgpu_cache:dl2':['S:128:128:16,L:B:m:L:L,A:192:4,32:0,32'],
 '-gpgpu_frfcfs_dram_sched_queue_size':['64'],'-gpgpu_dram_return_queue_size':['192']}
def validate_spec(spec):
 profile=spec['profile'];assert profile==spec['structure_variant']and profile in VARIANTS,'EXACT_NON_TAG_STRUCTURE_FAMILY_REQUIRED'
 assert spec['cell']=='DH'and spec['downstream_profile']=='P0','DH_DOWNSTREAM_P0_REQUIRED'
 options=spec['expected_options'];shape=VARIANTS[profile]
 expected=dict(FIXED_OPTIONS,**{
 '-gpgpu_dtc_l1_physical_lines':[str(shape['physical'])],
 '-gpgpu_dtc_l1_oo_pib_entries':[str(shape['oo_pib'])],
 '-gpgpu_dtc_l1_tag_req_per_bank':[str(shape['perbank'])],
 '-gpgpu_dtc_l1_tag_req_per_cycle':[str(shape['total'])]})
 for key,value in expected.items():assert options.get(key)==value,'UNAUTHORIZED_STRUCTURE_OR_PLATFORM_DELTA '+key
 sms=int(options['-gpgpu_n_clusters'][0])*int(options['-gpgpu_n_cores_per_cluster'][0])
 assert sms==64 and shape['physical']in[640,768,1024]
 return dict(profile=profile,physical_lines_per_SM=shape['physical'],SMs=sms,capacity_bound=shape['physical']*sms,active_OO_PIB=shape['oo_pib'],cohort_token=shape['token'],validated_declared_option_keys=sorted(expected))
def transformed_source(spec):
 shape=validate_spec(spec);source=LEGACY_PATH.read_bytes();assert hashlib.sha256(source).hexdigest()==LEGACY_SHA256
 text=source.decode();assert text.count(ANCHOR)==1
 replacement='0 <= value("oo_physical_allocated") <= '+str(shape['physical_lines_per_SM'])+' * '+str(shape['SMs'])+', "physical_'+str(shape['physical_lines_per_SM'])+'_per_SM_capacity"'
 transformed=text.replace(ANCHOR,replacement,1);assert transformed.replace(replacement,ANCHOR,1)==text
 binding=dict(source_path=str(LEGACY_PATH),source_sha256=LEGACY_SHA256,transformed_source_sha256=hashlib.sha256(transformed.encode()).hexdigest(),replacement_count=1,physical_lines_per_SM=shape['physical_lines_per_SM'],SMs=shape['SMs'],capacity_bound=shape['capacity_bound'],only_terminal_allocation_gauge=True,peak_occupancy_not_proven=True,all_other_parser_source_bytes_unchanged=True,structure_profile=shape['profile'],active_OO_PIB=shape['active_OO_PIB'])
 return transformed,binding
def load_for(spec):
 transformed,binding=transformed_source(spec)
 module=types.ModuleType('perffirst28_config_bound_capacity_parser');module.__file__=str(LEGACY_PATH)
 exec(compile(transformed,str(LEGACY_PATH)+':declared_capacity_bound','exec'),module.__dict__)
 return module,binding
