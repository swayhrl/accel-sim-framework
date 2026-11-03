from pathlib import Path
import ast,json,hashlib,sys,contextlib
H=Path(__file__).resolve().parent;R=H/'runtime';sys.path.insert(0,str(R))
import ep_perf_common_v2 as common,ep_perf_archive as archive
eng=(R/'ep_perf_native_wv_modes_draft.py').read_text();arc=(R/'ep_perf_archive.py').read_text();rows=[]
def check(k,b):rows.append(dict(label=k,PASS=bool(b)));assert b,k
check('consume_and_live_claim_update_same_global_Main_admission',eng.count('with locked(GLOBAL_MAIN_ADMISSION_LOCK):')==2)
check('archive_claim_release_same_global_Main_admission',arc.count('with locked(GLOBAL_MAIN_ADMISSION_LOCK):')==1)
check('no_local_admission_lock_in_runtime', "ROOT/'control/ADMISSION.lock'"not in eng+arc and "ROOT.parent/'control/ADMISSION.lock'"not in eng+arc)
check('global_Main_lock_reuses_active_X_owner',str(common.GLOBAL_MAIN_ADMISSION_LOCK).endswith('execution_performance_first_20261103_v1/control/ADMISSION.lock'))
check('archive_window_global_Main_not_local', "with locked(GLOBAL_MAIN_RESTORE_WINDOW_LOCK):"in arc and "ROOT/'control/ARCHIVE_SHARED_WINDOW.lock'"not in arc)
seen=[]
@contextlib.contextmanager
def fake_lock(p,*a,**k):seen.append(str(p));yield
archive.locked=fake_lock;archive._archive_case=lambda c:dict(TEST_ONLY=True,case=c)
v=archive.archive_case('TEST_ONLY')
check('real_archive_entry_selects_global_restore_window_without_any_actual_lock_or_archive',seen==[str(common.GLOBAL_MAIN_RESTORE_WINDOW_LOCK)]and v['TEST_ONLY'])
(H/'GLOBAL_MAIN_LOCK_CONTROLS.json').write_text(json.dumps(dict(schema='EP_SYSTEM850_GLOBAL_MAIN_LOCK_CONTROL_V1',status='PASS_REAL_BLOCK_SOURCE_AND_ARCHIVE_ENTRY_LOCK_SELECTION_NOT_LIVE_SCIENCE',controls=rows,total=len(rows),new_models=0,real_registry_writes=0,real_Main_locks_acquired=0),indent=2)+'\n')
print('PASS',len(rows),'globalMain lock controls')
