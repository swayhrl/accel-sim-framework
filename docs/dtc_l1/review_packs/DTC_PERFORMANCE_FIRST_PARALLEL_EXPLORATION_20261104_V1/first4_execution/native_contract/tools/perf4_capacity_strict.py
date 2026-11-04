"""Private forward capacity-bound adapter; no historical parser or shared module mutation.
Only the terminal physical-allocation gauge bound follows the declared capacity.
This is not a runtime peak-occupancy measurement or numerical validation.
"""
from pathlib import Path
import hashlib,types
LEGACY_PATH=Path('/root/data/ep_l2_dtc_l1_native_v2/DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/ag6_strict.py')
LEGACY_SHA256='9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4'
ANCHOR='0 <= value("oo_physical_allocated") <= 640 * 64, "physical_640_per_SM_capacity"'
def load_for(spec):
 source=LEGACY_PATH.read_bytes();assert hashlib.sha256(source).hexdigest()==LEGACY_SHA256
 options=spec['expected_options'];physical=int(options['-gpgpu_dtc_l1_physical_lines'][0]);sms=int(options['-gpgpu_n_clusters'][0])*int(options['-gpgpu_n_cores_per_cluster'][0])
 assert physical==768 and sms==64 and spec['structure_variant']=='PHYS768_TAG64x8'
 text=source.decode();assert text.count(ANCHOR)==1
 replacement='0 <= value("oo_physical_allocated") <= '+str(physical)+' * '+str(sms)+', "physical_'+str(physical)+'_per_SM_capacity"'
 transformed=text.replace(ANCHOR,replacement,1);assert transformed.replace(replacement,ANCHOR,1)==text
 module=types.ModuleType('perffirst4_config_bound_capacity_parser');module.__file__=str(LEGACY_PATH)
 exec(compile(transformed,str(LEGACY_PATH)+':PHYS768_capacity_bound','exec'),module.__dict__)
 binding=dict(source_path=str(LEGACY_PATH),source_sha256=LEGACY_SHA256,transformed_source_sha256=hashlib.sha256(transformed.encode()).hexdigest(),replacement_count=1,physical_lines_per_SM=physical,SMs=sms,capacity_bound=physical*sms,only_terminal_allocation_gauge=True,peak_occupancy_not_proven=True,all_other_parser_source_bytes_unchanged=True)
 return module,binding
