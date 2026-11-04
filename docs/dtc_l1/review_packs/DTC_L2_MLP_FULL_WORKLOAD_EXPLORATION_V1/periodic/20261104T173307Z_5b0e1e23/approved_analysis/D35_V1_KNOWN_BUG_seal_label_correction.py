"""Immutable prose correction; does not change consumer/QA/dry data."""
import json,pathlib
import derived35_consumer as d
D=pathlib.Path(__file__).parent
def put(p,v):
    with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
labels=d.read(D/'RATIFIED_P0_PRESENTATION_LABELS.json')['rows'];details=[]
for row in labels:
    source=d.read(row['reference_result_path']);proof=source['proof']
    details.append(dict(**row,proof_suite_field_present='suite'in proof,proof_profile_field_present='profile'in proof,proof_suite_value=proof.get('suite'),proof_profile_value=proof.get('profile')))
assert len(details)==6 and all(not r['proof_suite_field_present']and not r['proof_profile_field_present']for r in details)
put(D/'RATIFIED_P0_LABEL_FIELD_PRESENCE.json',dict(rows=details,interpretation='All six historical downstream proof objects omit suite and profile. Frozen35 displays PolyBench/GPU and P0; full270 effective equality proves P0. Null is absent evidence, not a different known legacy string.',consumer_source_unchanged=True,CPU_QA_unchanged=True))
raw=(D/'REPORT.md').read_text()
raw=raw.replace('Six ratified P0 references use older display labels, listed below and in `RATIFIED_P0_PRESENTATION_LABELS.json`. Their input digest, input-binding SHA, build, complete270 physics and ROI remain exact. Legacy suite/profile text is not used to loosen input identity or select a workload; the frozen35 grouping and all270 P0 vector determine presentation/parameter identity.', 'All six ratified P0 reference proof objects **omit suite and profile fields** (the projection below is `None`/JSON null); there are no known different legacy strings to compare. `RATIFIED_P0_LABEL_FIELD_PRESENCE.json` explicitly records field absence. Their input digest, input-binding SHA, build, complete270 physics and ROI remain exact. The frozen35 suite is PolyBench/GPU and the full270 vector establishes P0; missing presentation metadata does not weaken scientific identity. This corrects the earlier REPORT wording while preserving that preimage unchanged.')
raw=raw.replace('| Ratified original slot | Legacy suite → frozen35 suite | Legacy profile → vector identity |','| Ratified original slot | Absent proof suite → frozen35 suite | Absent proof profile → vector identity |')
with(D/'REPORT_FINAL.md').open('x')as f:f.write(raw)
put(D/'PROSE_CORRECTION.json',dict(previous_report=dict(path=str(D/'REPORT.md'),sha256=d.sha(D/'REPORT.md')),corrected_report=dict(path=str(D/'REPORT_FINAL.md'),sha256=d.sha(D/'REPORT_FINAL.md')),reason='Absence of suite/profile fields was initially described too loosely as older display labels. No numerical/source identity, consumer, QA or selected reference changes.',consumer_sha256=d.sha(D/'derived35_consumer.py'),CPU_QA_sha256=d.sha(D/'CPU_QUALIFICATION_FROZEN.json'),original_manifest_sha256=d.sha(D/'MANIFEST.json')))
old=d.read(D/'MANIFEST.json');files=[D/r['relative_path']for r in old['files']]+[D/x for x in ['REPORT_FINAL.md','RATIFIED_P0_LABEL_FIELD_PRESENCE.json','PROSE_CORRECTION.json','seal_label_correction.py','MANIFEST.json']]
put(D/'MANIFEST_FINAL.json',dict(**{k:v for k,v in old.items()if k!='files'},final_report='REPORT_FINAL.md',files=[dict(path=str(p),relative_path=str(p.relative_to(D)),sha256=d.sha(p),bytes=p.stat().st_size)for p in files],previous_manifest_sha256=d.sha(D/'MANIFEST.json'),correction_does_not_change_measurements_or_code=True))
print(json.dumps(dict(manifest_path=str(D/'MANIFEST_FINAL.json'),manifest_sha256=d.sha(D/'MANIFEST_FINAL.json'),report_path=str(D/'REPORT_FINAL.md'),report_sha256=d.sha(D/'REPORT_FINAL.md'),consumer_sha256=d.sha(D/'derived35_consumer.py'),CPU_QA_sha256=d.sha(D/'CPU_QUALIFICATION_FROZEN.json'))))
