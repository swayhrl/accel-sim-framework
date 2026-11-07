"""CPU-only exact operational source adapter for a clean serial owner.

Produces private engine/ops source, never installs or executes a model. There
is no call to B2.apply, original parent.apply, exec, debugger or signal API.
"""
from pathlib import Path
import ast,copy,hashlib,json,types
OLD_NATIVE='5f978c77586f3be030ca0295adb6eec09d8152254df1f88f85becb45588850d9'
B2='d3ad4b880753a9bf42e91858743bdae9f657a63e578be4bc5180d8b3b44c6bc1'
OLD_OPS='29a97d55dc2acc4e84c3fa228025f7d2f619ef7d1fbc1af867645ec279047fb4'
REQUEST='DTC_ORACLE_REMAINING24_20261106_V1'
MARKER='DTC_ORACLE_CLEAN_MAIN_SINGLE_POOL_V1'
class Hold(RuntimeError):pass
def need(x,why):
 if not x:raise Hold(why)
def digest(b):return hashlib.sha256(b).hexdigest()
def encoded(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def source_replace_function(source,name,replacement):
 tree=ast.parse(source);rows=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name]
 need(len(rows)==1,'EXACT_ONE_FUNCTION:'+name);n=rows[0];lines=source.splitlines(keepends=True)
 old=''.join(lines[n.lineno-1:n.end_lineno]);need(source.count(old)==1,'UNIQUE_FUNCTION_SOURCE')
 new=replacement.rstrip()+'\n'
 return source.replace(old,new,1),dict(function=name,original_sha256=digest(old.encode()),replacement_sha256=digest(new.encode()))
def derive_native(original):
 need(digest(original)==OLD_NATIVE,'EXACT_FROZEN_ORACLE_NATIVE_REQUIRED')
 text=original.decode()
 replacement="""def assert_parent_lease():
 plan=read(R/'control/EXECUTION_PLAN.json')
 ref=plan['clean_owner_guard'];assert sha(ref['path'])==ref['sha256'],'CLEAN_OWNER_GUARD_PIN'
 guard=load('oracle_clean_owner_private_guard',ref['path'])
 return guard.verify_parent_lease(plan)"""
 text,edit=source_replace_function(text,'assert_parent_lease',replacement)
 compile(text,'<CPU_ONLY_CLEAN_NATIVE>','exec')
 return text,dict(schema='DTC_CLEAN_MAIN_NATIVE_EXACT_TRANSFORM_V1',original_sha256=OLD_NATIVE,
                  derived_sha256=digest(text.encode()),edits=[edit],unchanged_original_model_loop=True,
                  original_run_native_explicitly_sets_n_assert_batch_lease_to_new_function=True,
                  old_lease_read_replaced_not_spoofed=True)
def exact_replace(text,old,new,changes,count=1):
 need(text.count(old)==count,'EXACT_OPERATIONAL_ANCHOR:'+old[:100]);text=text.replace(old,new)
 changes.append(dict(original_sha256=digest(old.encode()),new_sha256=digest(new.encode()),count=count));return text
def derive_ops(original,b2_source):
 need(digest(original)==OLD_OPS and digest(b2_source)==B2,'QUALIFIED_B2_AND_29A_SOURCE_REQUIRED')
 b2=types.ModuleType('CPU_ONLY_B2_PURE_SOURCE_TRANSFORM');exec(compile(b2_source,'<B2_SOURCE_PROJECTION_ONLY>','exec'),b2.__dict__)
 text,previous=b2.derive_ops_source(original.decode());changes=[]
 owner="""def owner():
 assert sys.dont_write_bytecode
 _C_assert_clean_owner()"""
 text,edit=source_replace_function(text,'owner',owner);changes.append(edit)
 text=exact_replace(text,"MARKER='"+b2.MARKER+"'","MARKER='"+MARKER+"'",changes)
 text=exact_replace(text,"root in [BASE/'initial8',BASE/'remaining24']","root==_C_execution_root",changes)
 text=exact_replace(text,"assert root==BASE/'initial8','INITIAL_OWNER_POOL_REQUIRED'","assert root==_C_execution_root,'ONLY_NEW96_CLEAN_POOL'",changes)
 text=exact_replace(text,"first=state['contexts'][str(BASE/'initial8')]","first=state['contexts'][str(_C_execution_root)]",changes,count=2)
 # The unused install_extension_callback is removed completely: all original
 # 32 cells are terminal; this generation has no second registration callback.
 text,edit=source_replace_function(text,'install_extension_callback',"def install_extension_callback(callback):\n raise RuntimeError('NO_EXTENSION_CALLBACK_IN_CLEAN_NEW96_GENERATION')")
 changes.append(edit)
 text=exact_replace(text,'owner_pid=1498278,owner_start_ticks=977758783',"owner_pid=_C_owner_pid,owner_start_ticks=_C_owner_start",changes,count=2)
 text=exact_replace(text,'start_ticks=977758783','start_ticks=_C_owner_start',changes)
 text=exact_replace(text,"command=[str(N/'bin/experiment'),'prepare',c,'--project','DTC_L1']",
                    "command=_C_native_command(ctx,c,'prepare')",changes)
 text=exact_replace(text,"command[1]='run-native'","command=_C_native_command(ctx,c,'run-native')",changes)
 text=exact_replace(text,"(len(contexts)==2 or(BASE/'control/POOL_STOP_NEW.json').exists())",
                    "(len(contexts)==1 and first['request']==_C_request)",changes)
 compile(text,'<CPU_ONLY_CLEAN_OPS>','exec')
 need('1498278'not in text and '977758783'not in text,'OLD_OWNER_ID_REMAINS_IN_PRIVATE_OPS')
 return text,dict(schema='DTC_CLEAN_MAIN_OPS_EXACT_TRANSFORM_V1',qualified_B2_transform=previous,
  serial_successor_edits=changes,source_sha256=digest(text.encode()),single_context_new96=True,
  single_archive_worker_retained=True,qualified_HOLD_latch_serial_launch_RSS_anchors_retained=True)

SPEC_OPERATIONAL_KEYS={'host_launcher_layout'}
def scientific_spec_projection(spec):
 # All fields except the explicitly requalified launcher proof must stay equal,
 # including original four+enum paths, runtime ELF, source, options, input/ROI,
 # counters, original env, limits/caps, planID/cohort/request and historicalrefs.
 return{k:v for k,v in spec.items()if k not in SPEC_OPERATIONAL_KEYS}
def require_science_equal(before,after):
 need(scientific_spec_projection(before)==scientific_spec_projection(after),'FROZEN96_SCIENTIFIC_SPEC_CHANGED')
 return True
def plan_projection(before,*,root,parent,guard_ref,lease_ref,source_pins,layout_ref,engine_pin_ref,peer_ref):
 need(before['request']==REQUEST and before['expected_new_starts']==96
      and before['stage']=='remaining24','EXACT96_UNREGISTERED_PLAN_SCOPE')
 after=copy.deepcopy(before)
 after.update(execution_root=str(root),parent_pid=parent['pid'],parent_start_ticks=parent['start_ticks'],
     parent_controller_path=parent['controller']['path'],parent_controller_sha256=parent['controller']['sha256'],
     clean_owner_guard=guard_ref,clean_owner_lease=lease_ref,source_pins=source_pins,
     launcher_layout=layout_ref,RESULT_ENGINE_PIN=engine_pin_ref,peer_disk_adapter=peer_ref,
     shared_pool_roots=[str(root)],shared_pool_dispatch_reservations_path=str(Path(root).parent/'control/SHARED_POOL_DISPATCH_RESERVATIONS.json'),
     clean_operational_generation=dict(kind='SERIAL_LEGAL_DTC_MAIN_SUCCESSOR',
        old32_new_starts=0,new_starts=96,old_q_lease_journal_modified=False,
        same_PID_exec_or_legacy_frame_required=False))
 # This is still CPU preparation. It must not manufacture SCIENCE_FINAL_FROZEN
 # or an authorization from the original CPU draft.
 after['preparation_phase']='CPU_CLEAN_SUCCESSOR_DRAFT_NOT_REGISTERED'
 after['actual_execution_authorized']=False
 return after

def native_argv(frontend,cohort,operation):
 need(operation in ['prepare','run-native'],'ONLY_QUALIFIED_NATIVE_MODEL_OPERATIONS')
 return ['/usr/bin/python3','-B',str(frontend),'experiment',operation,cohort,'--project','DTC_L1']

if __name__=='__main__':print(json.dumps(dict(status='CPU_SOURCE_ADAPTER_ONLY',registrations=0,models=0)))
