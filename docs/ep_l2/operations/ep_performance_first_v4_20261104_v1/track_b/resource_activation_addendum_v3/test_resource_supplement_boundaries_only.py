"""Small resource-graph metadata checks; no old suite/eventloop/models."""
import copy
import main_activate_900_with_qualified_resources as m

def main():
 d=m.load_supplement()
 for label in ['helper','root','pin','base']:
  x=copy.deepcopy(d)
  if label=='helper':x['Main_qualified_helper_ref']['sha256']='0'*64
  if label=='root':x['root']='/root/data/UNAUTHORIZED_ROOT'
  if label=='pin':x['resource_pin_additions']=[r for r in x['resource_pin_additions']if r['path']!=x['Main_qualified_helper_ref']['path']]
  if label=='base':x['selected_900_spec_refs']['W_ONLY']['sha256']='0'*64
  try:m.validate_supplement_data(x)
  except ValueError:continue
  raise AssertionError('unexpected resource supplement acceptance '+label)
if __name__=='__main__':main()
