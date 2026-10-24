"""Replay the original 13-case exactAST CPU gate with input/output path literals only relocated."""
from pathlib import Path
import argparse,hashlib,json,ast,copy
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--out',required=True,help='ABSENT directory below this review namespace');a=p.parse_args();out=Path(a.out).resolve()
assert B in out.parents and not out.exists(),'new output must be ABSENT beneath review namespace'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
original=B/'qualify_final_gate_exact_ast_v1_original.py';before=B/'SYNTHETIC_FINAL_GATE_QUALIFICATION.json'
assert sha(original)=='0e294486f19e99edfe2c1e7057270a063aa9d52aeee89d50b3405f725cc9d91a'
assert sha(before)=='034be47785c417172e3446ca1307c3b3c40b92b51b737cb8f8e6fe337b17e980'
F=B/'replay_frozen_inputs';manifest=json.loads((B/'REPLAY_FROZEN_INPUTS.json').read_text());assert len(manifest['files'])==7
for row in manifest['files']:
 path=F/row['path'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
text=original.read_text();oldR='/root/data/shared_sm70_trace_library_20261024_v1';oldO='/root/data/sm70_cross_project_independent_review_20261025_v1'
needleR='pathlib.Path('+repr(oldR)+')';needleO='pathlib.Path('+repr(oldO)+')';assert text.count(needleR)==text.count(needleO)==1
adapted=text.replace(needleR,'pathlib.Path('+repr(str(F))+')',1).replace(needleO,'pathlib.Path('+repr(str(out))+')',1)
class NormalizePaths(ast.NodeTransformer):
 def visit_Constant(self,node):
  if isinstance(node.value,str):
   if node.value in (oldR,str(F)):return ast.copy_location(ast.Constant(value='REVIEW_INPUT_ROOT'),node)
   if node.value in (oldO,str(out)):return ast.copy_location(ast.Constant(value='REVIEW_OUTPUT_ROOT'),node)
  return node
assert ast.dump(NormalizePaths().visit(ast.parse(text)),include_attributes=False)==ast.dump(NormalizePaths().visit(ast.parse(adapted)),include_attributes=False),'only the two lookup/output path literals may differ'
exec(compile(adapted,str(original),'exec'),{'__name__':'__exact_cpu_guard_replay__','__file__':str(original)})
result=out/'SYNTHETIC_FINAL_GATE_QUALIFICATION.json';assert sha(result)==sha(before)=='034be47785c417172e3446ca1307c3b3c40b92b51b737cb8f8e6fe337b17e980'
(out/'PATH_ONLY_REPLAY_SOURCE.py').write_text(adapted)
q={'status':'EXACT13_CASE_CPU_REPLAY_BYTE_IDENTICAL_ORIGINAL_RESULT_PASS','original_script_sha256':sha(original),'replay_source_sha256':hashlib.sha256(adapted.encode()).hexdigest(),'result_sha256':sha(result),'original_result_unchanged_sha256':sha(before),'AST_identical_except_two_path_literals':True,'small_input_files':7,'production_module_imports':0,'large_trace_payload_bytes_read':0,'sender_starts_or_signals':0,'109_accesses':0,'GPU_starts':0,'SIM_starts':0,'actual_data_acceptance_executed':False,'source_KEEP':True}
(out/'REPLAY_PROVENANCE.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
