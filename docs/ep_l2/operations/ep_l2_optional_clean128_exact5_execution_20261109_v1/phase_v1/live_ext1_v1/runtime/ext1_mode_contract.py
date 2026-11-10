import hashlib,json
from pathlib import Path
P=Path
EXT2=P("/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1/cases/EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1/control/FROZEN_SPEC.json")
PIN="34559c8f77cdb5ddd51dbdbed5eef65ef6bb426e233ff91fd2e023cd2c5f442a"
CASE="EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1"
REQ="EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1"
def validate_static(s,candidate=False):
 assert hashlib.sha256(EXT2.read_bytes()).hexdigest()==PIN
 b=json.loads(EXT2.read_bytes())
 assert s['cohort']==CASE and s['science_request_id']==REQ and s['victim_extension']==1
 assert s['source_identity']==b['source_identity'] and s['input_identity_sha256']==b['input_identity_sha256']
 assert s['mode']==b['mode']=='WV_ZERO_RO' and s['T'] is s['M'] is False
 assert s['geometry']==b['geometry'] and s['limits']==b['limits']
 assert s['expected_instructions']==b['expected_instructions'] and s['expected_CTA']==b['expected_CTA']
 assert s['expected_kernel_launches']==b['expected_kernel_launches'] and s['expected_kernel_scopes']==b['expected_kernel_scopes']
 assert s['all_unique_kernel_members']==b['all_unique_kernel_members'] and s['command_count']==b['command_count']
 x=dict(b['expected_effective_options']);x['-gpgpu_ep_l2_victim_extension']='1'
 assert s['expected_effective_options']==x and len(x)==283
 assert s['exact_config_canonical_sha256']=='36b9d132a37645c2f6b3f68522fbfca39ed1f0ff091aab0b93d5668fb1738af9'
 assert s['application_budget']==s['approved_launches']==1 and s['automatic_retry'] is s['refund'] is False
 assert s['source_keep'] is True
 return {'status':'EXT1_SOURCE5_EXACT_DELTA_PASS_NO_START','launch_permission':False}
