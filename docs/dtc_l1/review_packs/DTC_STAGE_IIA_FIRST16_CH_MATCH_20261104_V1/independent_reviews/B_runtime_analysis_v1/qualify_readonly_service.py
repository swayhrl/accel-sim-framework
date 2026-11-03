"""CPU-only signature/cache behavior checks. Synthetic metadata is not performance evidence."""
from pathlib import Path
import tempfile,json,hashlib,importlib.util,types
B=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('service_cpu',B/'readonly_analysis_service.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);checks=[]
def check(n,c):assert c,n;checks.append({'name':n,'pass':True})
with tempfile.TemporaryDirectory(prefix='CPU_SYNTHETIC_',dir=B) as t:
 r=Path(t);meta=r/'meta.json';meta.write_text('{"synthetic":1}');row={'sources':{'RESULT':{'path':str(meta),'sha256':m.sha(meta)}}};check('fresh_critical_json_cache_matches',m.cache_metadata_ok(row));meta.write_text('{"synthetic":2}');check('changed_critical_json_invalidates_cache',not m.cache_metadata_ok(row));meta.unlink();check('missing_critical_json_invalidates_cache',not m.cache_metadata_ok(row))
 a=types.SimpleNamespace(R=r);contract={'expected_CH':[{'cohort':'SYNTHETIC_NO_SCIENTIFIC_IDENTITY'}]};sig,rows=m.result_signature(a,contract);sig2,_=m.result_signature(a,contract);check('unchanged_signature_stable',sig==sig2 and all(v is None for v in rows[0]['refs'].values()));p=r/'analysis/SYNTHETIC_NO_SCIENTIFIC_IDENTITY.RESULT.json';p.parent.mkdir();p.write_text('{"synthetic":true}');sig3,_=m.result_signature(a,contract);check('new_result_signature_changes',sig3!=sig);p.write_text('{"synthetic":false}');sig4,_=m.result_signature(a,contract);check('result_bytes_change_signature',sig4!=sig3)
 forname=r/'atomic_test.json';m.atomic(forname,{'synthetic':1});check('atomic_owned_state_json',json.loads(forname.read_text())=={'synthetic':1})
(B/'CPU_SERVICE_QUALIFICATION.json').write_text(json.dumps({'schema':'DTC_STAGEIIA_READONLY_ANALYSIS_SERVICE_CPU_QA_V1','synthetic_only':True,'checks':checks,'all_pass':all(x['pass'] for x in checks),'source_service_sha256':m.sha(B/'readonly_analysis_service.py'),'new_models_started':0},indent=2)+'\n');print(len(checks),'PASS')
