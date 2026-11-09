"""AST only: verify opt-in edits and exact default-OFF transform."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'q1_3dgs_completion'))
from shn_candidate import install
from source_transform import transform_train

source=Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014/software_sources/gsscale/examples/simple_trainer_hybrid_optimized.py').read_text()
class Runner: pass
class Proxy: pass
class Transfer:
    def copy_(self,*a,**kw): pass
    def to(self,*a,**kw): pass
ctl=SimpleNamespace(transfer=Transfer(),shn=Proxy(),cpu_optimizer_parallel=lambda *a:None)
mod=SimpleNamespace(__dict__={},__file__='candidate_ast_only.py',Runner=Runner)
off=install(mod,source,ctl,None,enabled=False)
assert off['train_ast_sha256']
assert not hasattr(mod.Runner.train,'__candidate__')
mod2=SimpleNamespace(__dict__={},__file__='candidate_ast_only.py',Runner=type('Runner2',(),{}))
on=install(mod2,source,ctl,None,enabled=True)
assert on['candidate_train_ast_sha256'] != off['train_ast_sha256']
tree=ast.parse(source)
original=transform_train(source)
assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='cpu_optimizer_parallel' for n in ast.walk(original))
assert '_q1_shn' in mod2.__dict__
print({'status':'PASS_AST_CPU','default_off_sha256':off['train_ast_sha256'],'candidate_sha256':on['candidate_train_ast_sha256']})
