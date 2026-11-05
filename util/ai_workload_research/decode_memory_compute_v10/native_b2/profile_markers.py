"""NVTX-only PROFILED runner markers;never attached to native formal worker."""
class RunnerMarkers:
 def __init__(self,runner,torch):
  self.runner=runner;self.torch=torch;self.enabled=False;self.step=-1;self.point=''
  self.original_execute=runner.execute_model;self.original_sample=runner.sample_tokens
  def execute(*args,**kwargs):
   if not self.enabled:return self.original_execute(*args,**kwargs)
   self.step+=1
   schedule=args[0] if args else kwargs.get('scheduler_output')
   counts=list(schedule.num_scheduled_tokens.values()) if schedule is not None else []
   self.kind='PREFILL' if counts and max(counts)>1 else 'DECODE'
   label=f'V9_FORWARD_{self.kind}_STEP{self.step:02d}'
   self.torch.cuda.nvtx.range_push(label)
   try:return self.original_execute(*args,**kwargs)
   finally:self.torch.cuda.nvtx.range_pop()
  def sample(*args,**kwargs):
   if not self.enabled:return self.original_sample(*args,**kwargs)
   self.torch.cuda.nvtx.range_push(f'V9_SAMPLE_{self.kind}_STEP{self.step:02d}')
   try:return self.original_sample(*args,**kwargs)
   finally:self.torch.cuda.nvtx.range_pop()
  runner.execute_model=execute;runner.sample_tokens=sample
 def begin(self,point):self.point=point;self.step=-1
 def restore(self):self.runner.execute_model=self.original_execute;self.runner.sample_tokens=self.original_sample
