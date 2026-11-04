from pathlib import Path
import sys,types,copy,json,hashlib,math
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
m=types.ModuleType('structure_plot_CPU_QA');m.__file__=str(O/'plot_structure.py');exec(compile((O/'plot_structure.py').read_bytes(),m.__file__,'exec'),m.__dict__)
checks=[]
def ck(n,b):assert b,n;checks.append(dict(name=n,PASS=True))
p,b,ps,snap,summary=m.load_provider(m.FIXED_PROVIDER)
data=m.build_data(snap,summary,dict(provider_sha256=ps,source='ACTUAL_B_V3_CPU_CHECK'))
ck('actual_fixed8_32nonTag_and16separateHOLD',len(data['cells'])==32 and len(data['input_order'])==8 and data['Tag_safety_HOLD_excluded']==16)
ck('actual_missing_kept_null',all(c['S_DH']is None and c['Rnew']is None for c in data['cells']if not c['accepted']))
try:m.load_provider(m.FIXED_PROVIDER,'wrong');ok=False
except ValueError:ok=True
ck('provider_SHA_mismatch_rejected',ok)
for name,change in [('wrong_input',lambda x:x['rows'][0].update(input_digest='wrong')),('unknown_status',lambda x:next(r for r in x['rows']if r['variant']in m.VARIANTS).update(status='UNRECOGNIZED')),('fabricated_unaccepted_cycles',lambda x:next(r for r in x['rows']if not r['accepted']and r['variant']in m.VARIANTS).update(cycles=0))]:
 bad=copy.deepcopy(snap);change(bad)
 try:m.build_data(bad,summary,dict(provider_sha256=ps));ok=False
 except ValueError:ok=True
 ck(name+'_rejected',ok)
ck('exact_zero_uses_integers_not_display',m.exact_direction(10**16,10**16+1)=='negative'and format(10**16/(10**16+1),'.3f')=='1.000'and m.exact_direction(11,11)=='exact_zero')
# Explicitly synthetic layout/data fixture, never published as B/provider science.
rows=[];base=[]
for n,d in m.FIXED_INPUTS:
 for cell,cycles in [('DH',1000),('CH',1500)]:base.append(dict(program=n,input_digest=d,accepted=True,source_profile='P0',source_cell=cell,cycles=cycles))
 for v in m.TAG_VARIANTS:rows.append(dict(program=n,input_digest=d,suite='CPU_SYNTHETIC',design='DH',downstream_profile='P0',variant=v,status='SAFETY_HOLD_CPU_PROGRESS_NEGATIVE',accepted=False,cycles=None))
 for j,v in enumerate(m.VARIANTS):
  i=[x[0]for x in m.FIXED_INPUTS].index(n);state='ACCEPTED_STRICT_ARCHIVE_RESTORE'if i==0 else('ARCHIVED_NEGATIVE_NO_PERFORMANCE'if(i+j)%4==0 else'UNUSED_FAMILY_HOLD'if(i+j)%4==1 else'VERIFICATION_HOLD'if(i+j)%4==2 else'AWAIT_CLOSED_RESULT');cycles=[800,1000,1250,2000][j]if i==0 else None;rows.append(dict(program=n,input_digest=d,suite='CPU_SYNTHETIC',design='DH',downstream_profile='P0',variant=v,status=state,accepted=i==0,cycles=cycles,S_DH=1000/cycles if cycles else None,Rnew=1500/cycles if cycles else None,uuid=None,cohort='CPU_SYNTHETIC_NOT_NATIVE'))
common_ids=[m.FIXED_INPUTS[0][1]];ss=dict(fixed_input_n=8,CORE32_population=False,common_nonTag_accepted_intersection=dict(n=1,ids=common_ids,variants={v:{key:dict(n=1,GM=(1000 if key=='S_DH'else 1500)/[800,1000,1250,2000][j])for key in ['S_DH','Rnew']}for j,v in enumerate(m.VARIANTS)}));synthetic=m.build_data(dict(rows=rows,baseline_sources=base),ss,dict(provider_sha256='CPU_SYNTHETIC_LAYOUT_ONLY'),synthetic=True)
ck('commonGM_same_single_input_allcolumns',synthetic['common_accepted_intersection']['n']==1 and synthetic['common_accepted_intersection']['GM'][m.VARIANTS[3]]['S_DH']==.5)
ck('unaccepted_categories_preserved',{c['display_state']for c in synthetic['cells']}=={'ACCEPTED','PENDING','NEGATIVE','UNUSED_HOLD','VERIFY_HOLD'})
root=m.configure_runtime(O/'qa_render');out1=root/'synthetic_a';out2=root/'synthetic_b';out1.mkdir(exist_ok=True);out2.mkdir(exist_ok=True);stamp='2000-01-01T00:00:00+00:00';source=m.sha(O/'plot_structure.py');files,env=m.render(synthetic,out1,stamp,source);m.render(synthetic,out2,stamp,source)
ck('PNG_SVG_repeat_deterministic',all(m.sha(p)==m.sha(out2/p.name)for p in files))
(out1/'FIGURE_DATA.json').write_text(json.dumps(synthetic,indent=2)+'\n');(O/'CPU_QUALIFICATION.json').write_text(json.dumps(dict(status='PASS_CPU_AND_SYNTHETIC_LAYOUT',checks=checks,n=len(checks),source_sha256=source,render_environment=env,actual_provider_SHA=ps,synthetic_layout_not_scientific=True,synthetic_pngs=[str(p)for p in files if p.suffix=='.png'],new_models=0,services=0,scientific_writes=0),indent=2)+'\n');print(json.dumps(dict(status='CPU_PLOT_PASS',n=len(checks),environment=env,source=source)))
