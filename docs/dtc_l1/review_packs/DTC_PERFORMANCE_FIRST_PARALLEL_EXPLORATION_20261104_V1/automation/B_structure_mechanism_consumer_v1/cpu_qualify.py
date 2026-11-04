import importlib.util,json,pathlib,time,hashlib
D=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('mechanism_readonly',D/'analyze.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def test(name,ok):
 assert ok,name;checks.append({'check':name,'PASS':True})
test('first_explicit_zero_allowed',m.interval({'x':0},{},True)=={'x':0})
test('later_new_field_is_unavailable',m.interval({'x':10},{},False)=={'x':None})
test('later_missing_field_is_unavailable',m.interval({}, {'x':9},False)=={'x':None})
test('counter_decrease_unavailable_not_negative_work',m.interval({'x':5},{'x':10})=={'x':None})
test('explicit_endpoints_delta',m.interval({'x':12},{'x':10})=={'x':2})
test('physical_terminal_gauge_not_additive',m.classified('DTC_L1_oo_physical_allocated')=='terminal_gauge'and'DTC_L1_oo_physical_allocated'not in m.ADDITIVE)
test('peak_not_additive',m.classified('DTC_L1_pib_peak_per_sm')=='running_peak'and'DTC_L1_pib_peak_per_sm'not in m.ADDITIVE)
test('unknown_field_not_auto_added',m.classified('DTC_SERVICE_V1_invented_counter')=='UNCLASSIFIED_NO_DIFFERENCE')
test('missing_latency_not_zero',m.ratio(None,5)is None and m.ratio(1,0)is None)
provider=D/'snapshots/qualification_actual_two_v1/PROVIDER_CAPTURE.json';pr=json.loads(provider.read_bytes());snap=json.loads((pathlib.Path(pr['snapshot'])/'SNAPSHOT.json').read_bytes());refs=snap['baseline_sources'];e=[]
# Two multi-kernel inputs, including legal P0 aliases. Closed historical inputs only.
for program in ['ATAX','scan']:
 for cell in ['CH','DH']:
  b=next(x for x in refs if x['program']==program and x['source_cell']==cell)
  r=m.build_raw(b['canonical_RESULT'],b['input_binding'],cell,'P0',program,b['input_digest'],b['cycles'])
  test(program+cell+'_exact_source_kernel_contract',len(r['kernels'])==(2 if program=='ATAX'else 33))
  test(program+cell+'_cycle_sum',sum(x['cycles']for x in r['kernels'])==b['cycles'])
  if cell=='DH':test(program+'_finite_service_window_all64SM',all(x['finite_service_window']['matches_64SM_clock_window']for x in r['kernels']))
  e.append({k:r[k]for k in ['program','cell','RESULT','bottom_RESULT','uuid','raw_gzip','raw_uncompressed_sha256','input_binding','cycles','parsing_wall_seconds']});e[-1]['kernel_count']=len(r['kernels'])
result={'all_pass':True,'checks':checks,'count':len(checks),'additional_closed_raw_qualifications':e,'live_raw_reads':0,'model_starts':0,'native_writes':0,'does_not_prove_future_performance':True,'fixture_scope':'Boundary arithmetic + four actual closed multi-kernel baseline raw inputs; six new/control raw rows separately in initial snapshot; no archive tar replay or process execution.'}
(D/'CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(len(checks),[(x['program'],x['cell'],x['kernel_count'])for x in e])
