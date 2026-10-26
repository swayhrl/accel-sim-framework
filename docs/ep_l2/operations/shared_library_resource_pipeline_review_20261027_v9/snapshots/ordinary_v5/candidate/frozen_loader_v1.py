"""Exact frozen ordinary validator loader; function bodies stay byte-for-byte."""
import pathlib,hashlib,types,ast
HERE=pathlib.Path(__file__).resolve().parent
PRE=HERE.parent/'preimages'
VALIDATOR_SHA='f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1'
HELPER_SHA='f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b'
OLD_HELPER='/data/c16/ada_trace_semantics_20261024_v1/frozen/ada7_contract_v1/validate_v7.py'
def load():
 p=PRE/'validate_v7_stream_v3.py';h=PRE/'validate_v7_frozen.py';raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=VALIDATOR_SHA or hashlib.sha256(h.read_bytes()).hexdigest()!=HELPER_SHA:raise RuntimeError('FROZEN_CHECKER_PIN')
 text=raw.decode();assert text.count(OLD_HELPER)==1
 relocated=text.replace(OLD_HELPER,str(h))
 oldast=ast.parse(text);newast=ast.parse(relocated)
 for a,b in zip(oldast.body,newast.body):
  if isinstance(a,(ast.FunctionDef,ast.AsyncFunctionDef)):
   assert ast.get_source_segment(text,a)==ast.get_source_segment(relocated,b),'checker function bytes changed'
 ns=dict(__name__='frozen_ordinary_cpu',__file__=str(p))
 exec(compile(relocated,str(p),'exec'),ns)
 return types.SimpleNamespace(**ns)
