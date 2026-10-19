"""Prepare all four same-input RO conditions; does not qualify or launch a simulator.

Rehashes whole traces. Run only with E's offline resource admission when inputs
are large; the C source-only checkpoint does not invoke this on an application.
"""
import argparse,hashlib,json
from pathlib import Path
import ro_oracle

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepare(oracle,out):
 m=ro_oracle.verify(oracle)
 if m['status']!='CERTIFIED_WITH_MODEL_SCOPE' or m['unresolved_opcodes']:
  raise ValueError('complete resolved oracle required')
 if m['address_domain']!='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS':
  raise ValueError('unresolved aliases')
 if not m['kernels'] or m['kernel_count']!=len(m['kernels']):raise ValueError('incomplete epoch')
 manifest=(oracle/'manifest.json').resolve();ranges=(oracle/'certified_ranges.csv').resolve()
 if any(c.isspace() for p in [manifest,ranges] for c in str(p)):raise ValueError('unsupported config path whitespace')
 out.mkdir(parents=True,exist_ok=False);profiles=[]
 for t,by in [(0,0),(1,0),(0,1),(1,1)]:
  name=f'RO_T{t}_M{by}';config=out/(name+'.config')
  text=f'''-gpgpu_ep_l2_ft_mode 2
-gpgpu_ep_l2_wbuf_entries 16
-gpgpu_ep_l2_payload_mode 2
-gpgpu_ep_l2_descriptor_pool_size 512
-gpgpu_ep_l2_descriptor_per_line_cap 32
-gpgpu_ep_l2_wad_entries 128
-gpgpu_ep_l2_bank_ops 1
-gpgpu_ep_l2_static_s64 0
-gpgpu_ep_l2_wb_local_cap 0
-gpgpu_ep_l2_mq2 0
-gpgpu_ep_l2_rg1 0
-gpgpu_ep_l2_ideal_wb 0
-gpgpu_ep_l2_ideal_meta 0
-gpgpu_ep_l2_ideal_read_hit 0
-gpgpu_ep_l2_i_mem_all_data 0
-gpgpu_ep_l2_diag_copy_free 0
-gpgpu_ep_l2_diag_l2_data_free 0
-gpgpu_ep_l2_ro_tag_detach {t}
-gpgpu_ep_l2_ro_line_mshr_bypass {by}
-gpgpu_ep_l2_ro_ranges {ranges}
-gpgpu_ep_l2_ro_ranges_sha256 {sha(ranges)}
-gpgpu_ep_l2_ro_manifest {manifest}
-gpgpu_ep_l2_ro_manifest_sha256 {sha(manifest)}
-gpgpu_ep_l2_ro_scope TRACE_MODEL_CLOSED_WORLD
'''
  config.write_text(text)
  profiles.append(dict(profile=name,tag_detach=t,line_mshr_bypass=by,config_sha256=sha(config),
   traditional_line_mshr='RETAINED' if not by else 'BYPASSED_FOR_CERTIFIED_RO_ONLY',
   pending_tag='REPLACEABLE_WAIT1_POLICY' if t else 'RETAINED_TO_FILL',
   shared_request_descriptors=512,total_payload_slots=1168,
   runtime_state='REQUIRES_A_RELEASE_AND_E_INDEPENDENT_QUALIFICATION'))
 r=dict(campaign_id='EPL2_MECHANISM_STUDY_20261019_V1',status='INPUT_BOUND_FOUR_CONFIGS_ONLY_NOT_RUNTIME_QUALIFICATION',
  whole_epoch_manifest_sha256=sha(manifest),ranges_sha256=sha(ranges),commandlist_sha256=m['commandlist_sha256'],
  complete_trace_identities=m['kernels'],oracle_scope=m['scope'],profiles=profiles,
  same_new_binary_for_all_four=True,full_application_owner='E',full_application_starts=0,
  physical_p1_and_other_feature_disable='Use A supported full parent config; E effective dump must reject P2/ideals/diagnostics/victim/MQ2/RG1/quota/S64 combinations',
  launch_gate='Whole input verification above plus exact A release/binary and current E science/resource/24-start ledger acceptance. Older withdrawn qualifications never authorize a new launch.')
 (out/'FOUR_MODE_BINDING.json').write_text(json.dumps(r,indent=2)+'\n');return r

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--oracle',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.oracle,a.out),indent=2))
