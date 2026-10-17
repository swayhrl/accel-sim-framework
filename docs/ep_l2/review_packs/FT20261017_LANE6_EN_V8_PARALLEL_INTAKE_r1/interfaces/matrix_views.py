"""Derived views after exact-release independent intake. No science authority or simulation."""
import argparse,json
from pathlib import Path
VIEWS=('ideal_potential','limitation_removal','finite_configuration','structure','cost_timing')
REGISTERED_INTAKE_HANDLERS={}
def require(ok,why):
 if not ok:raise ValueError(why)
def scope_shape(r):
 require(all(k in r for k in ('identity','scope','terminal','cycles','instructions','condition','workload','independent_intake_receipt','current_target_binding')),'Missing independently attested fields')
 require(type(r['cycles']) is int and r['cycles']>0,'No positive native/reference cycles')
 if r['scope']=='NATIVE_PHYSICAL':keys=('source_bound_64_slices','request_response_exact_once','WB_WAD_sector_drain')
 else:
  require(r['scope'] in ('REFERENCE_ALL_DATA','REFERENCE_PARTIAL_DECLARED'),'Unknown scope')
  keys=('original_request_identity','producer_order','store_exact_once','read_snapshot','architectural_consume','all_state_drained')
 require(all(r['terminal'].get(k) is True for k in keys),'Scope-specific terminal proof absent');return True
def comparison(a,b):
 for k in ('core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256'):require(a['identity'][k]==b['identity'][k],'Cross-release/input comparison')
 require(a['condition']==b['condition'] and a['workload']==b['workload'],'Comparison background differs');return a['cycles']/b['cycles']
def captured_fraction(b,u,i):
 require(b-i>0,'Ideal denominator must be positive');return (b-u)/(b-i)
def render(records,out):
 out=Path(out);require(not out.exists(),'Never overwrite a view revision');points={v:[] for v in VIEWS}
 for r in records:
  scope_shape(r);key=(r['identity']['core_source_commit'],r['scope']);require(key in REGISTERED_INTAKE_HANDLERS,'No reviewed exact-release consumer; metadata cannot grant scientific intake');views=REGISTERED_INTAKE_HANDLERS[key](r)
  for view,values in views.items():require(view in VIEWS,'Unknown derived view');points[view].extend(values)
 out.mkdir(parents=True)
 from chart_views import plot_points
 for view in VIEWS:plot_points(view,points[view],out)
 for v in VIEWS:(out/(v+'.json')).write_text(json.dumps({'view':v,'status':'NO_INDEPENDENTLY_INGESTED_POINTS' if not records else 'ATTESTED_RECEIPTS_ONLY','records':records,'missing_values_zero_filled':False},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--records',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();render(json.loads(a.records.read_text())['records'],a.output_dir)
