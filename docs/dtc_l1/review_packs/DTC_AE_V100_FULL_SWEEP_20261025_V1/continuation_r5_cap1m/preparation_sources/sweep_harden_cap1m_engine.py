import pathlib,ast
p=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py');s=p.read_text();a="s=spec_for(cohort);host=identity();r,e=read_current_authority();q=r['registered_future_requests'][REQUEST]";assert s.count(a)==1;s=s.replace(a,a+"\n require(s.get('operational_runtime_profile')=='OBSERVABILITY_CAP1M_WALL90_V1','future unused cell requires exact derived runtime spec')")
a="c=read(candidate)\n";assert s.count(a)==1;s=s.replace(a,a+" require(all(p.get(k)==v for k,v in c.items() if k!='status'),'registered runtime candidate fields changed')\n")
ast.parse(s);p.write_text(s);print('NEW_ENGINE_FAILS_CLOSED_WITHOUT_DERIVED_SPEC_AND_COMPLETE_CANDIDATE_BINDING')
