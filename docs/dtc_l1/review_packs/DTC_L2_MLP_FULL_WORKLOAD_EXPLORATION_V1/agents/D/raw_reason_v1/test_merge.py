import pathlib,importlib.util,copy,json,hashlib
H=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('merge_fixture',H/'merge_reason_report.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=0
def ck(v):
 global checks
 assert v;checks+=1
cell=dict(accepted=True,cohort='c',uuid='u',result_sha256='result',cycles=100)
row=dict(cohort='c',uuid='u',result_sha256='result',status='SIDECAR_EXTRACTED_CLOSED_ACCEPTED',source_closure=dict(source_verified_natural_closed_before_raw_open=True),closed_raw=dict(positive_reason_known_contributions={'GLOBAL_ACC_R:MSHR_ENRTY_FAIL':7},sum_known_positive_reason_contributions=7,last_cumulative_frame_by_stream={},raw_gzip_path='/closed/raw',raw_gzip_sha256='compressed',raw_uncompressed_sha256='body'),known_reason_sum_matches_observed_reservation_fail_total=True,observed_last_frame_reservation_fail_total=7,complete_declared_stream_stats_coverage=True,scope='VERIFIED_SINGLE_STREAM_DECLARED_TRACE')
def report():return dict(table={'digest':{'E384':{'DH':copy.deepcopy(cell)}}})
r=report();j=m.join_sidecar(r,dict(rows=[row]));ck(j['matched_report_cells']==1);ck(j['positive_sum_matches_aggregate']==1);ck(r['table']['digest']['E384']['DH']['cycles']==100);ck(r['table']['digest']['E384']['DH']['L2_failure_reason_sidecar']['unprinted_reasons']is None)
for key in['uuid','result_sha256']:
 bad=copy.deepcopy(row);bad[key]='wrong';r=report();j=m.join_sidecar(r,dict(rows=[bad]));ck(j['identity_mismatch_cells']==1);ck(r['table']['digest']['E384']['DH']['L2_failure_reason_sidecar']is None)
r=report();j=m.join_sidecar(r,dict(rows=[]));ck(j['not_scanned_current_accepted_cells']==1);ck(r['table']['digest']['E384']['DH']['L2_failure_reason_sidecar']is None)
bad=copy.deepcopy(row);bad['source_closure']['source_verified_natural_closed_before_raw_open']=False;j=m.join_sidecar(report(),dict(rows=[bad]));ck(j['sidecar_evidence_errors']==1)
none=copy.deepcopy(row);none['closed_raw']['positive_reason_known_contributions']=None;none['closed_raw']['sum_known_positive_reason_contributions']=None;none['known_reason_sum_matches_observed_reservation_fail_total']=None;none['observed_last_frame_reservation_fail_total']=0;r=report();j=m.join_sidecar(r,dict(rows=[none]));ck(j['unprinted_reason_cells']==1);ck(r['table']['digest']['E384']['DH']['L2_failure_reason_sidecar']['positive_known_contributions']is None);ck(j['positive_sum_matches_aggregate']==0)
print(json.dumps(dict(status='CPU_ONLY_PASS',checks=checks,actual_simulator_starts=0,source_sha256=hashlib.sha256((H/'merge_reason_report.py').read_bytes()).hexdigest()),indent=2))
