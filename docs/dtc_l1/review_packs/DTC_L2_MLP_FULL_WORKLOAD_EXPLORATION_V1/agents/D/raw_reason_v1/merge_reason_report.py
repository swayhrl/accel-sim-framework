"""Optional sidecar overlay for independent report_v1; frozen consumer unchanged."""
import argparse,pathlib,json,hashlib,importlib.util,datetime,copy,html
P=pathlib.Path

def join_sidecar(report,sidecar):
 rows={r['cohort']:r for r in sidecar['rows']};assert len(rows)==len(sidecar['rows'])
 summary=dict(scanned_accepted_cells=len(rows),matched_report_cells=0,not_scanned_current_accepted_cells=0,identity_mismatch_cells=0,sidecar_evidence_errors=0,complete_stream_scope_cells=0,positive_field_cells=0,positive_sum_matches_aggregate=0,positive_sum_mismatches_aggregate=0,unprinted_reason_cells=0)
 for profiles in report['table'].values():
  for cells in profiles.values():
   for cell in cells.values():
    if not cell['accepted']:continue
    cell['L2_failure_reason_sidecar']=None
    row=rows.get(cell['cohort'])
    if row is None:
     cell['L2_failure_reason_status']='NOT_SCANNED_IN_THIS_SIDECAR';summary['not_scanned_current_accepted_cells']+=1;continue
    if row.get('uuid')!=cell.get('uuid')or row.get('result_sha256')!=cell.get('result_sha256'):
     cell['L2_failure_reason_status']='SIDECAR_IDENTITY_MISMATCH_WITHHELD';summary['identity_mismatch_cells']+=1;continue
    if row.get('status')!='SIDECAR_EXTRACTED_CLOSED_ACCEPTED'or row.get('source_closure',{}).get('source_verified_natural_closed_before_raw_open')is not True:
     cell['L2_failure_reason_status']='SIDECAR_EVIDENCE_ERROR_WITHHELD';summary['sidecar_evidence_errors']+=1;continue
    scan=row['closed_raw'];positive=scan['positive_reason_known_contributions'];match=row['known_reason_sum_matches_observed_reservation_fail_total']
    cell['L2_failure_reason_status']='EXTRACTED_POSITIVE_RAW_FIELDS'if positive is not None else'NO_POSITIVE_FIELDS_PRINTED_REMAIN_NONE'
    cell['L2_failure_reason_sidecar']=dict(positive_known_contributions=copy.deepcopy(positive),sum_known_positive_contributions=scan['sum_known_positive_reason_contributions'],observed_last_frame_reservation_fail_total=row['observed_last_frame_reservation_fail_total'],known_reason_sum_matches_aggregate=match,unprinted_reasons=None,complete_declared_stream_stats_coverage=row['complete_declared_stream_stats_coverage'],last_cumulative_frame_by_stream=copy.deepcopy(scan['last_cumulative_frame_by_stream']),raw_gzip_path=scan['raw_gzip_path'],raw_gzip_sha256=scan['raw_gzip_sha256'],raw_uncompressed_sha256=scan['raw_uncompressed_sha256'],source_closure=copy.deepcopy(row['source_closure']),scope=row['scope'])
    summary['matched_report_cells']+=1;summary['complete_stream_scope_cells']+=row['complete_declared_stream_stats_coverage']is True;summary['positive_field_cells']+=positive is not None;summary['unprinted_reason_cells']+=positive is None;summary['positive_sum_matches_aggregate']+=match is True;summary['positive_sum_mismatches_aggregate']+=match is False
 report['L2_raw_reason_sidecar_join']=summary
 return summary

def panel(report):
 e=html.escape;s=report['L2_raw_reason_sidecar_join'];out=['<h2>Closed raw L2 rejection reasons — sidecar</h2>',f'<p>{s["matched_report_cells"]} accepted cells matched by cohort, UUID and immutable result SHA; {s["positive_field_cells"]} have positive printed fields; {s["positive_sum_matches_aggregate"]} printed sums equal their observed aggregate; {s["not_scanned_current_accepted_cells"]} newer accepted cells have not been scanned. Missing reason fields remain None. These fields were omitted by the frozen proof extractor; their raw presence is separate evidence, without changing acceptance.</p>','<details><summary>Per-cell literal reason counts and raw provenance</summary><table><tr><th>Program / profile / design</th><th>Positive literal fields</th><th>Observed aggregate</th><th>Raw line / final kernel UID / stream</th></tr>']
 for d,p in sorted(report['programs'].items(),key=lambda item:item[1]['program']):
  for profile,cells in report['table'][d].items():
   for design,cell in cells.items():
    side=cell.get('L2_failure_reason_sidecar')
    if side is None:continue
    positive=side['positive_known_contributions']
    fields='<br>'.join(e(k)+': '+str(v)for k,v in(positive or{}).items())or'None (no positive field printed)'
    loc='<br>'.join('line '+str(r['line'])+' / UID '+str(frame['kernel_uid'])+' / stream '+str(frame['stream_id'])for frame in side['last_cumulative_frame_by_stream'].values()for r in frame['reason_lines'])or'Final frame has no positive reason lines'
    out.append('<tr><td>'+e(p['program']+' / '+profile+' / '+design)+'<small><code>'+d+'</code></small></td><td>'+fields+'</td><td>'+str(side['observed_last_frame_reservation_fail_total'])+'</td><td>'+loc+'</td></tr>')
 out.append('</table></details><p>Last cumulative frame per stream is used once. No summation of successive kernel snapshots, no implicit zero for a missing reason, and no interpretation of rejected attempts as unique misses or elapsed application cycles. Full raw paths, hashes and native closure ancestry are in report.json.</p>')
 return '\n'.join(out)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='/root/data/dtc_l2_mlp_exploration_20261027_v1');ap.add_argument('--base-generator',default=str(P(__file__).resolve().parents[1]/'report_v1/build_report.py'));ap.add_argument('--sidecar',required=True);ap.add_argument('--output',required=True);ap.add_argument('--base-tool-commit',default='UNCONFIRMED_BASE_SOURCE_SHA_IS_CANONICAL');ap.add_argument('--tool-commit',default='UNCOMMITTED_MERGER_SHA_IS_CANONICAL');a=ap.parse_args()
 out=P(a.output).resolve();assert not out.exists(),'Use a new derived output directory';assert not out.is_relative_to(P(a.root).resolve())
 source=P(a.base_generator);spec=importlib.util.spec_from_file_location('read_only_base_report',source);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
 r=base.acquire(a.root,a.base_tool_commit);data=P(a.sidecar).read_bytes();sidecar=json.loads(data)
 assert sidecar['root']==str(P(a.root))
 joined=join_sidecar(r,sidecar);r['L2_raw_reason_sidecar_source']=dict(path=str(P(a.sidecar).resolve()),sha256=hashlib.sha256(data).hexdigest(),utc=sidecar['utc']);r['reason_merger']=dict(path=str(P(__file__).resolve()),sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),base_generator_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),tool_commit=a.tool_commit)
 r['source_snapshots'].append(dict(path=str(P(a.sidecar).resolve()),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
 manifest=base.write_report(r,out)
 hp=out/'dashboard.html';text=hp.read_text();marker='<h2>Evidence and limitations</h2>';assert marker in text;hp.write_text(text.replace(marker,panel(r)+marker),encoding='utf-8')
 for f in manifest['files']:
  p=out/f['path'];f.update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
 manifest['reason_merger']=r['reason_merger'];manifest['sidecar_source']=r['L2_raw_reason_sidecar_source'];(out/'REPORT_MANIFEST.json').write_bytes(base.encode(manifest))
 print(json.dumps(dict(status='READ_ONLY_REPORT_WITH_RAW_REASON_OVERLAY',utc=r['utc'],output=str(out),join=joined,manifest=manifest),indent=2))
if __name__=='__main__':main()
