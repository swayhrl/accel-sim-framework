def run_native(cohort):
 ident='cpu-uuid';out=R/'DTC/run/results'/ident;observations=[{'pid':model.pid,'start_ticks':gen(model.pid)}];frame_identity=id(sys._getframe());before=None;deadline=time.monotonic()+12
 while time.monotonic()<deadline:
  value=resources({},False)
  if (R/'FINISH').exists():
   result={'frame_identity_before':frame_identity,'frame_identity_after':id(sys._getframe()),'model_pid':model.pid,'model_start_ticks':gen(model.pid),'model_alive':model.poll() is None,'pipe':pipe[:],'uds':uds[:],'value':value,'before_sequence':before,'after_sequence':len(pipe),'main_thread':threading.current_thread() is threading.main_thread()};(R/'CHILD_RESULT.json').write_text(json.dumps(result));return
  if before is None and (R/'INJECT_NOW').exists():
   before=len(pipe);(R/'DEBUG_IDENTITY.json').write_text(json.dumps(payload.code_identity(resources)))
  time.sleep(.005)
