import sys,os,pathlib
_R=pathlib.Path('/data/c16/aiarch_a65_igb_small_compiled_numeric_109_v1/resume_20261016').resolve();_W=pathlib.Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-a65-igb-small-compiled-numeric-109-v1').resolve()
def _allowed(p):
 if not isinstance(p,(str,bytes,os.PathLike)):return True
 q=pathlib.Path(os.fsdecode(p)).resolve()
 return q==pathlib.Path('/dev/null') or q.is_relative_to(_R) or q.is_relative_to(_W)
def _audit(event,args):
 if event=='open' and len(args)>2 and isinstance(args[2],int) and args[2]&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
  if not _allowed(args[0]):raise PermissionError('A65_OUTSIDE_WRITE_BLOCKED '+str(args[0]))
 if event in ['os.remove','os.rmdir','os.mkdir','os.chmod'] and not _allowed(args[0]):raise PermissionError('A65_OUTSIDE_WRITE_BLOCKED')
 if event in ['os.rename','os.replace'] and (not _allowed(args[0]) or not _allowed(args[1])):raise PermissionError('A65_OUTSIDE_MOVE_BLOCKED')
sys.addaudithook(_audit)
