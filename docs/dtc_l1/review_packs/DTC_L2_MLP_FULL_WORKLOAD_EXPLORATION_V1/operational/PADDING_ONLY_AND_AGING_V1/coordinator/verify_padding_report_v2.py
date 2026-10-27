"""Post-validate every accepted row of a report without changing its population.

Original generator/strict stays intact. New operational-overlay results require
the additional archived strict link; absent/invalid evidence fails the report.
"""
import pathlib,json,hashlib,importlib.util,datetime,argparse
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def verify(report_path,extra_source=None,extra_sha256=None):
 report=read(report_path);checks=[];module=None
 for digest,profiles in report['table'].items():
  for profile,cells in profiles.items():
   for cell,row in cells.items():
    if not row.get('accepted'):continue
    rp=P(row['result_path']);assert sha(rp)==row['result_sha256'];v=read(rp);c=v['cohort'];linked='additional_padding_admission_strict'in v.get('proof',{})
    if v['state']=='REFERENCE_ACCEPTED_NO_NEW_START':
     assert not linked;checks.append(dict(cohort=c,status='UNCHANGED_LEGAL_REFERENCE'));continue
    ip=R/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);out=P(intent['output']);assert intent['uuid']==row['uuid']==v['uuid'];triple=[intent,read(out/'NATIVE_LAUNCH.json'),read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];present=['additional_padding_admission_binding'in d for d in triple]
    if any(present):
     assert all(present) and linked,'Overlay evidence cannot be accepted with partial binding/strict link'
     if module is None:
      assert extra_source is not None and extra_sha256 is not None and sha(extra_source)==extra_sha256
      sp=importlib.util.spec_from_file_location('report_padding_extra_verifier',extra_source);module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
     result=module.verify_result_sidecar(v,out);assert result['status']=='PASS_SIDE_CAR_LINK','Original and archived intent overlay identities disagree';checks.append(dict(cohort=c,status='PASS_ADDITIONAL_ARCHIVED_STRICT_LINK',verification=result))
    else:
     assert not linked,'Dangling additional strict metadata on original path';checks.append(dict(cohort=c,status='UNCHANGED_ORIGINAL_NATIVE_PATH'))
 expected=sum(report['state_counts'].get(s,0)for s in ['PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','REFERENCE_ACCEPTED_NO_NEW_START']);assert len(checks)==expected
 return dict(status='PASS_ACCEPTED_POPULATION_ADMISSION_EVIDENCE_AUDIT',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),report_path=str(report_path),report_sha256=sha(report_path),accepted_rows=expected,overlay_rows=sum(r['status']=='PASS_ADDITIONAL_ARCHIVED_STRICT_LINK'for r in checks),extra_verifier_path=str(extra_source)if extra_source else None,extra_verifier_sha256=extra_sha256,model_starts=0,report_population_unchanged=True,checks=checks)
def main():
 p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--extra-source');p.add_argument('--extra-sha256');p.add_argument('--output',required=True);a=p.parse_args();v=verify(P(a.report),P(a.extra_source)if a.extra_source else None,a.extra_sha256)
 with P(a.output).open('x')as h:json.dump(v,h,indent=2);h.write('\n')
 print(json.dumps({k:x for k,x in v.items()if k!='checks'}))
if __name__=='__main__':main()
