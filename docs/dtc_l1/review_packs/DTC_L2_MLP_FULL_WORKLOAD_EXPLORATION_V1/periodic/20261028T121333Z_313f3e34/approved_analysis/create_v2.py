"""Prose/identity-description correction only; reuses frozen v1 source bytes."""
import copy,hashlib,json,pathlib
P=pathlib.Path(__file__).resolve().parent;V1=P.parent/'results_refresh_20261028_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
oldmanifest=load(V1/'MANIFEST.json')
for entry in oldmanifest['files']:
 src=V1/entry['name'];assert sha(src)==entry['sha256']
 dest=P/entry['name'];assert not dest.exists();dest.write_bytes(src.read_bytes())
old_phrase='F128 has the same seven-positive/six-negative identities but different magnitudes'
new_phrase='F128 and F256 have the same positive/negative counts (7/6), but different program sets: vectorAdd and GESUMMV are positive for F128 and negative for F256, while ATAX and scalarProd are negative for F128 and positive for F256'
old_identity='same270 effective options as the old failed M16 and same input/Core/Framework/binary'
new_identity='the same 270 expected physics option values declared by the frozen specs, with the same input/Core/Framework/binary identity; this is a declared-spec comparison, not validation of the failed M16 run\'s actual effective options'
for name in ['REPORT.md','analyze_refresh.py']:
 text=(P/name).read_text(encoding='utf-8');assert text.count(old_phrase)==1 and text.count(old_identity)==1
 text=text.replace(old_phrase,new_phrase).replace(old_identity,new_identity)
 # The renderer source uses a single-quoted Python string for the identity sentence.
 if name.endswith('.py'):text=text.replace("run's actual effective options","run’s actual effective options")
 (P/name).write_text(text,encoding='utf-8')
renderer=(P/'analyze_refresh.py').read_text(encoding='utf-8')
renderer=renderer.replace('same_270_effective_options_as_original_M16=True','same_270_expected_physics_values_as_original_frozen_spec=True,identity_comparison_scope=\'R2 strict effective options equal expected values declared in both frozen specs; original failed runtime effective options not independently accepted\'')
(P/'analyze_refresh.py').write_text(renderer,encoding='utf-8')
report=(P/'REPORT.md').read_text(encoding='utf-8')
note='**V2 correction:** Reuses the exact V1 18:09 CST source snapshot. Only F128/F256 set wording and the scope of the failed-M16 option comparison were corrected; no new data, collector, simulation or tests. V1 preimage remains intact. READY/publication should reference this V2 directory.'
first,rest=report.split('\n',1);(P/'REPORT.md').write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['EVIDENCE.json','ANALYSIS.json']:
 old=load(V1/name);new=copy.deepcopy(old)
 value=new['supplemental'].pop('same_270_effective_options_as_original_M16')
 new['supplemental']['same_270_expected_physics_values_as_original_frozen_spec']=value
 new['supplemental']['identity_comparison_scope']='Declared spec.expected_options values match (270); R2 own strict effective options match these values. No accepted full effective-option verification is claimed for original failed M16 runtime.'
 new['schema']='RESULTS_REFRESH_20261028_V2_PROSE_CORRECTION'
 new['version_provenance']=dict(previous_directory=V1.name,previous_file_sha256=sha(V1/name),same_source_snapshot=True,statistics_recomputed=False,new_observations=False,
  original_analysis_script_sha256=old['sources']['analysis_script_sha256'],corrected_renderer_sha256=sha(P/'analyze_refresh.py'),
  corrections=['Same F128/F256 sign counts, different program sets.','Expected frozen-spec option comparison, not verified original failed runtime effective options.'])
 assert new['primary']==old['primary']
 assert new['supplemental']['target_option_diff_from_P0']==old['supplemental']['target_option_diff_from_P0']
 write(name,new)
provenance=dict(schema='RESULTS_REFRESH_V2_CORRECTION_PROVENANCE',snapshot_utc='2026-10-28T10:09:38.618532+00:00',
 previous_directory=V1.name,previous_report_sha256=sha(V1/'REPORT.md'),previous_manifest_sha256=sha(V1/'MANIFEST.json'),
 previous_machine_sha256=sha(V1/'EVIDENCE.json'),primary_statistics_and_cells_identical=True,supplemental_cycles_and_option_diff_identical=True,
 new_sampling=False,collector_run=False,model_runs=0,tests_rerun=False,READY_should_reference=P.name,
 corrections=[dict(old=old_phrase,new=new_phrase),dict(old=old_identity,new=new_identity)],
 source_snapshots=[dict(name=n,sha256=sha(P/n),same_as_v1=(P/n).read_bytes()==(V1/n).read_bytes())for n in ['PRIMARY_SNAPSHOT.json','SUPPLEMENTAL_SNAPSHOT.json','ORIGINAL_SCAN_M16_SPEC.json','SCAN_DH_P0_SPEC.json']],
 preserved_v1=[dict(name=x['name'],sha256=sha(V1/x['name']))for x in oldmanifest['files']])
write('CORRECTION_PROVENANCE.json',provenance)
manifest=dict(schema='RESULTS_REFRESH_MANIFEST_V2_PROSE_CORRECTION',snapshot_utc=provenance['snapshot_utc'],previous_manifest_sha256=sha(V1/'MANIFEST.json'),
 files=[dict(name=x.name,sha256=sha(x),bytes=x.stat().st_size)for x in sorted(P.iterdir())if x.is_file()and x.name!='MANIFEST.json'])
write('MANIFEST.json',manifest)
print(json.dumps(dict(report_sha256=sha(P/'REPORT.md'),manifest_sha256=sha(P/'MANIFEST.json'),evidence_sha256=sha(P/'EVIDENCE.json'),
 primary_source_sha256=sha(P/'PRIMARY_SNAPSHOT.json'),supplemental_source_sha256=sha(P/'SUPPLEMENTAL_SNAPSHOT.json'))))
