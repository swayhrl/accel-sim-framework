import pathlib,json,sys,importlib.util,copy,argparse
P=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('binder',P/'bind_unconsumed_resources.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
a=argparse.ArgumentParser();a.add_argument('group');tag=a.parse_args().group;idx=b.read(P/'bound/SPEC_INDEX.json');points=[x for x in idx['rows']if x['group']==tag];g=b.GROUPS[tag];root=pathlib.Path(g['data_ROOT']);files={x['cohort']:pathlib.Path(x['successor_spec_ref']['path'])for x in idx['rows']};file_for=lambda c:files.get(c,root/'cases'/c/'control/FROZEN_SPEC.json');first=b.read(points[0]['successor_spec_ref']['path']);r=pathlib.Path(first['host_engine_ref']['path']).parent;sys.path.insert(0,str(r))
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load(first['host_engine_ref']['path'],'actual_cap10_engine');c=load(first['mode_contract_ref']['path'],'actual_cap10_contract');reg=copy.deepcopy(b.read(b.REG));q=reg['registered_future_requests'][g['goal']]
for z in points:q['admitted_specs'][z['cohort']]=z['successor_spec_ref']['sha256']
m.authority=lambda:(reg,None);m.spec_path=file_for;rows=[]
for z in points:
 case=z['cohort'];s=b.read(z['successor_spec_ref']['path']);c.validate_static(s);rows.append(dict(name='actual accepted HostQ/static '+case,status='PASS'));peer=b.read(file_for(s['same_background_peer_cohort']));c.validate_fair_pair(s,peer);rows.append(dict(name='mixed old/new resource fair peer '+case,status='PASS'))
 if tag=='system':m.spec_for(case,require_release=False);rows.append(dict(name='complete private registry spec_for '+case,status='PASS'))
 elif '_1700_'in case:
  try:m.spec_for(case);raise RuntimeError('premature1700 accepted')
  except (ValueError,OSError)as e:rows.append(dict(name='unchanged1700 gate '+case,status='PASS_EXPECTED_HOLD',reason=str(e)))
 else:m.spec_for(case);rows.append(dict(name='complete private registry spec_for '+case,status='PASS'))
x=dict(status='PASS',group=tag,checks=len(rows),rows=rows,registry_mutation='IN_MEMORY_DEEP_COPY_ONLY',new_native_or_runtime_or_HostQ=False,model_starts=0);b.write(P/('ACTUAL_RESOURCE_SPEC_'+tag.upper()+'_CPU.json'),x);print(json.dumps(dict(group=tag,status='PASS',checks=len(rows))))
