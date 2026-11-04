"""Only five small overlay boundary checks; no Host/eventloop/model suite."""
import copy
import main_install_with_budget900_overlay as m

def main():
 d,_=m.load_overlay()
 for label in ['hardware','wrongbase','scope','wrongmode']:
  x=copy.deepcopy(d)
  if label=='hardware':x['points'][0]['expected_effective_options']={'-gpgpu_n_clusters':'1'}
  if label=='wrongbase':x['points'][0]['base_spec_ref']['sha256']='0'*64
  if label=='scope':x['points'][0]['cohort']='EP_PERF_PFV4_UNAUTHORIZED_OTHER_V1'
  if label=='wrongmode':x['points'][0]['mode']='WV_ZERO_RO'
  try:m.validate_overlay_data(x)
  except ValueError:continue
  raise AssertionError('unexpected overlay acceptance '+label)
 try:m.load_overlay(expected_sha='0'*64)
 except ValueError:return
 raise AssertionError('wrong overlay SHA accepted')
if __name__=='__main__':main()
