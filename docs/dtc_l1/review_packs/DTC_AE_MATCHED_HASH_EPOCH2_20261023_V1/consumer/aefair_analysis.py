"""Post-cohort evidence consumer; refuses incomplete/mixed-source matrices."""
import pathlib,json,hashlib,importlib.util,datetime
from fractions import Fraction

T=pathlib.Path('/root/data/dtc_main_20261023_v1/ae_fair_v1')
CELLS=('CM','CH','DM','DH')
def require(ok,why):
 if not ok:raise ValueError(why)
def read(p):return json.loads(pathlib.Path(p).read_text())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def ratio(x):return {'exact':str(x),'decimal':float(x)}

def aggregate(rows):
 require(set(rows)==set(CELLS),'complete four-cell population required')
 for cell,r in rows.items():
  require(r['performance_accepted'] is True,'unaccepted point:'+cell)
  require(type(r['cycles']) is int and r['cycles']>0,'positive integer cycles:'+cell)
  require((r['instructions'],r['CTA'],r['kernel_count'])==(739246080,1024,1),'whole input identity:'+cell)
 require(len({r['core_commit'] for r in rows.values()})==1,'mixed Core source')
 require(len({r['framework_commit'] for r in rows.values()})==1,'mixed Framework source')
 require(len({r['uuid'] for r in rows.values()})==4,'reused attempt population')
 for off,on,allowed in [('CM','CH','-gpgpu_cache:dl1'),('DM','DH','-gpgpu_dtc_l1_tag_hash_bankrow')]:
  a=rows[off]['effective_options'];b=rows[on]['effective_options']
  changes={k for k in set(a)|set(b) if a.get(k)!=b.get(k)}
  require(changes=={allowed},'non-hash effective option changed:'+str(changes))
 c0,c1,d0,d1=(rows[c]['cycles'] for c in CELLS)
 sc=Fraction(c0,c1);sd=Fraction(d0,d1);interaction=sd/sc
 if sd<=1:
  disposition='AE_GAIN_NOT_OBSERVED_OR_REVERSED_IN_THIS_FRESH_GEMM_TUPLE'
 elif interaction>1:
  disposition='DTC_HAS_LARGER_WITHIN_DESIGN_HASH_SPEEDUP_UNDER_THE_STATED_GEOMETRIES'
 elif interaction==1:
  disposition='EQUAL_WITHIN_DESIGN_HASH_SPEEDUPS_UNDER_THE_STATED_GEOMETRIES'
 else:
  disposition='CONVENTIONAL_CACHE_HAS_LARGER_WITHIN_DESIGN_HASH_SPEEDUP'
 return {'cycles':{c:rows[c]['cycles'] for c in CELLS},'conventional_hash_speedup':ratio(sc),'DTC_AE_speedup':ratio(sd),'interaction_R':ratio(interaction),'conventional_cycle_reduction':ratio(1-Fraction(c1,c0)),'DTC_cycle_reduction':ratio(1-Fraction(d1,d0)),'bounded_disposition':disposition,'core_commit':next(iter(rows.values()))['core_commit'],'framework_commit':next(iter(rows.values()))['framework_commit'],'interpretation_boundary':'Deterministic four-cell discovery GEMM under different C+/DTC geometries, not a universal DTC-specific or statistical significance theorem. Equal data capacity does not imply equal area; index latency is a modeling assumption.'}

def collect_verified():
 request=read(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 require(set(request['matrix_order'])=={'E2-AEFAIR-'+c for c in CELLS},'different frozen matrix')
 s=importlib.util.spec_from_file_location('exact_existing_aefair_result_consumer',T/'tools/aefair_result.py');archive=importlib.util.module_from_spec(s);s.loader.exec_module(archive)
 rows={};proofs=[]
 for cell in CELLS:
  cohort='E2-AEFAIR-'+cell;intent=read(T/'control/qualification_ledger'/(cohort+'.INTENT.json'));done=read(T/'control/qualification_ledger'/(cohort+'.DONE.json'));out=pathlib.Path(intent['output'])
  r=read(out/'AEFAIR_STRICT.json');qual=read(T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cohort+'.json'));rec=read(T/'control'/(cohort+'_ARCHIVE_RECEIPT.json'))
  require(done==read(out/'NATIVE_EXIT.json') and done['launcher_wait_returncode']==0 and done['stop_reason'] is None,'non-natural native terminal')
  require(intent['uuid']==done['uuid']==r['uuid']==qual['uuid'],'attempt/strict identity join')
  require(qual['status']=='AEFAIR_SCIENCE_QUALIFIED' and qual['strict_sha256']==sha(out/'AEFAIR_STRICT.json'),'scientific proof changed')
  require(r['raw_sha256']==sha(out/'raw.log')==done['raw_sha256'],'complete raw output SHA changed')
  require(rec['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and rec['scientific_status']=='AEFAIR_SCIENCE_QUALIFIED','archive/restore not qualified')
  require(rec['source_disposition']=='SOURCE_KEEP' and rec['source_release_bytes']==0,'source preservation')
  bundle=pathlib.Path(rec['target_mount_path']);manifest=read(bundle/'SOURCE_MANIFEST.json')
  require(manifest==archive.manifest_for(cohort),'source/immutable archive manifest disagreement')
  f,v=archive.libraries(bundle);index=f.verify_archive(bundle,manifest)
  require(index['archive_sha256']==rec['archive_sha256'],'whole archive SHA')
  restored=f.check_native(pathlib.Path(rec['native_restore']),manifest)
  require(len(restored)==len(manifest['entries']),'independent native restore population')
  spec=read(T/'control'/(cohort+'_SPEC.json'))
  require(r['core_commit']==spec['core_commit'] and r['framework_commit']==spec['framework_commit'],'source receipt identity')
  rows[cell]=r;proofs.append({'cell':cell,'uuid':r['uuid'],'strict_sha256':sha(out/'AEFAIR_STRICT.json'),'native_exit_sha256':sha(out/'NATIVE_EXIT.json'),'raw_sha256':r['raw_sha256'],'archive_sha256':rec['archive_sha256'],'true164_root':rec['true164_root'],'native_restore':rec['native_restore'],'archive_and_restore_independently_rechecked':True,'restore_entries':len(restored)})
 result=aggregate(rows);result.update(schema='DTC_AEFAIR_COMPLETE_SCIENTIFIC_RESULT_V1',verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_four_complete_accepted_archived_restored=True,proofs=proofs)
 return result,rows

if __name__=='__main__':
 result,rows=collect_verified();destination=T/'analysis';destination.mkdir(exist_ok=True)
 (destination/'COMPLETE_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
