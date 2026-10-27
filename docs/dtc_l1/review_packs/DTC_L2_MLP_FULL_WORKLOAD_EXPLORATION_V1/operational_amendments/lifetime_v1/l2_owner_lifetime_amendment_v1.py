"""Keep existing owner alive through threading shutdown until its addon finishes.
Import has no side effects. Only existing owner main-thread pending callback calls
apply_in_owner. No controller replacement, signal, registry or frozen-source write.
"""
import sys,threading,concurrent.futures.thread as futures_thread,pathlib,os,hashlib
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');MARKER='DTC_L2_MLP_OWNER_LIFETIME_HOOK_V1'
def _hook_names():
 return [dict(module=getattr(getattr(x,'func',x),'__module__',''),name=getattr(getattr(x,'func',x),'__name__',repr(x)))for x in threading._threading_atexits]

def register_keepalive(thread,marker=MARKER):
 assert sys.implementation.name=='cpython'
 assert threading.current_thread()is threading.main_thread(),'Register via existing main-thread GIL pending callback'
 assert hasattr(threading,'_register_atexit')and hasattr(threading,'_threading_atexits'),'CPython threading pre-join hooks unavailable; no fallback applied'
 assert not threading._SHUTTING_DOWN and not futures_thread._shutdown,'Shutdown has already begun; do not reset shutdown state'
 assert thread is not threading.current_thread()and thread.is_alive()and not thread.daemon
 main=sys.modules['__main__']
 if hasattr(main,marker):
  old=getattr(main,marker);assert old['thread']is thread;return dict(old['proof'],idempotent_existing_registration=True)
 prior=tuple(threading._threading_atexits);functions=[getattr(x,'func',x)for x in prior];assert futures_thread._python_exit in functions,'ThreadPool shutdown hook must already be registered'
 state=dict(hook_entered=False,addon_naturally_completed=False)
 def wait_for_existing_l2_addon():
  state.update(hook_entered=True,futures_shutdown_on_entry=futures_thread._shutdown)
  # Never reset futures globals or interrupt old/new jobs. Let the finite
  # authorized scheduler reach its own normal end before TPE global shutdown.
  while thread.is_alive():thread.join(.5)
  state.update(addon_naturally_completed=True,futures_shutdown_on_return=futures_thread._shutdown)
 threading._register_atexit(wait_for_existing_l2_addon)
 assert tuple(threading._threading_atexits[:-1])==prior and getattr(threading._threading_atexits[-1],'func',None)is wait_for_existing_l2_addon
 proof=dict(status='REGISTERED_OWNER_LIFETIME_PREJOIN_HOOK',owner_pid=os.getpid(),addon_ident=thread.ident,addon_native_id=thread.native_id,addon_name=thread.name,python_version=sys.version,prior_hook_count=len(prior),prior_hooks=[dict(module=getattr(x,'__module__',''),name=getattr(x,'__name__',''))for x in functions],registered_hook_index=len(prior),hook_order='REVERSE_REGISTRATION_NEW_KEEPALIVE_BEFORE_ALL_CURRENT_HOOKS',earlier_threadpool_exit_index=functions.index(futures_thread._python_exit),threadpool_shutdown_state_before=futures_thread._shutdown,no_shutdown_flag_reset=True,no_frozen_source_or_registry_or_lease_write=True,no_old_mainloop_interception=True)
 setattr(main,marker,dict(thread=thread,hook=wait_for_existing_l2_addon,state=state,proof=proof))
 return proof

def apply_in_owner():
 import json
 plan=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes());assert os.getpid()==plan['parent_pid']==1498278
 ticks=int((P('/proc/self/stat')).read_text().rsplit(')',1)[1].split()[19]);assert ticks==plan['parent_start_ticks']
 thread=getattr(sys.modules['__main__'],'DTC_L2_MLP_ADDON_THREAD');assert thread.name=='DTC_L2_MLP_ONE_OWNER'
 return register_keepalive(thread)
