"""Directed synthetic qualification for exact tree-partial prefix resume."""
from local_common import *

CODE=r'''
import pathlib,sys,importlib.util,tempfile,hashlib,json,ast,time,os
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');Q=T/'qualification/tree_partial_resume_v1';sys.path.insert(0,str(T/'tools'))
spec=importlib.util.spec_from_file_location('qualified_tree_resume',Q/'copy_engine.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
c.pace_bytes=lambda count,rate:None
checks={};gates=[]
def gate():gates.append(True)
body=(b'alpha0123456789'*7)+(b'betaXYZ'*11)+(b'omega'*13);parts=[body[:37],body[37:101],body[101:]]
with tempfile.TemporaryDirectory(prefix='tree_resume_',dir=Q) as tmp:
 root=P(tmp);bundle=root/'bundle';folder=bundle/'chunks'/c.digest(b'member.bin');folder.mkdir(parents=True);(bundle/'tree').mkdir()
 ranges=[];offset=0
 for k,part in enumerate(parts):
  name=str(offset).zfill(20)+'.part';p=folder/name;p.write_bytes(part);ranges.append(dict(name=name,offset=offset,size=len(part),sha256=hashlib.sha256(part).hexdigest()));offset+=len(part)
 row=dict(relative_path='member.bin',size=len(body),sha256=hashlib.sha256(body).hexdigest())
 chunk_before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
 p=bundle/'tree/exact.writing';p.write_bytes(body[:55]);before=p.read_bytes();assert c.materialize_tree_from_ranges(p,bundle,row,ranges,gate)==55 and p.read_bytes()==body
 checks['mid_range_exact_prefix_appended']='PASS'
 assert all(hashlib.sha256((folder/n).read_bytes()).hexdigest()==h for n,h in chunk_before.items());checks['immutable_ranges_unchanged']='PASS'
 p=bundle/'tree/zero.writing';p.write_bytes(b'');assert c.materialize_tree_from_ranges(p,bundle,row,ranges,gate)==0 and p.read_bytes()==body;checks['existing_zero_partial_appended']='PASS'
 p=bundle/'tree/absent.writing';assert c.materialize_tree_from_ranges(p,bundle,row,ranges,gate)==0 and p.read_bytes()==body;checks['absent_partial_created']='PASS'
 p=bundle/'tree/full.writing';p.write_bytes(body);snapshot=p.read_bytes();assert c.materialize_tree_from_ranges(p,bundle,row,ranges,gate)==len(body) and p.read_bytes()==snapshot;checks['complete_partial_verified_without_rewrite']='PASS'
 p=bundle/'tree/wrong.writing';p.write_bytes(body[:20]+b'!'+body[21:55]);snapshot=p.read_bytes()
 try:c.materialize_tree_from_ranges(p,bundle,row,ranges,gate)
 except RuntimeError as e:assert 'prefix differs' in str(e)
 else:raise AssertionError('wrong prefix admitted')
 assert p.read_bytes()==snapshot;checks['wrong_prefix_rejected_and_retained']='PASS'
 p=bundle/'tree/gap.writing';bad=[dict(ranges[0]),dict(ranges[1])];bad[1]['offset']+=1
 try:c.materialize_tree_from_ranges(p,bundle,row,bad,gate)
 except RuntimeError as e:assert 'assembly gap' in str(e)
 else:raise AssertionError('range gap admitted')
 assert not p.exists();checks['range_gap_rejected_before_output']='PASS'
 p=bundle/'tree/oversize.writing';p.write_bytes(body+b'x');snapshot=p.read_bytes()
 try:c.materialize_tree_from_ranges(p,bundle,row,ranges,gate)
 except RuntimeError as e:assert 'larger' in str(e)
 else:raise AssertionError('oversize admitted')
 assert p.read_bytes()==snapshot;checks['oversize_partial_rejected_and_retained']='PASS'
 assert gates;checks['resource_callback_retained']='PASS'
before=(Q/'BEFORE_copy_engine.py').read_text();after=(Q/'copy_engine.py').read_text();bt=ast.parse(before);at=ast.parse(after)
b={n.name:ast.dump(n,include_attributes=False) for n in bt.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))};a={n.name:ast.dump(n,include_attributes=False) for n in at.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
assert 'materialize_tree_from_ranges' not in b and 'materialize_tree_from_ranges' in a
assert {n for n in b if b[n]!=a[n]}=={'migrate'}
checks['all_existing_top_level_functions_except_migrate_AST_unchanged']='PASS'
assert "owned tree partial needs range recovery; retained" in before and "tree_partial_resumes" in after and "materialize_tree_from_ranges(partial,bundle,row" in after
checks['migrate_change_binds_exact_helper_and_receipt']='PASS'
x=dict(schema='LANE_T2_TREE_PARTIAL_RESUME_QUALIFICATION_V1',unix=time.time(),checks=checks,before_sha256=hashlib.sha256((Q/'BEFORE_copy_engine.py').read_bytes()).hexdigest(),after_sha256=hashlib.sha256((Q/'copy_engine.py').read_bytes()).hexdigest(),fixture_bytes=len(body),gate_callbacks=len(gates),scientific_payload_reads=0,archive_or_science_processes_started_or_signalled=0)
(Q/'QUALIFICATION.json').write_bytes(c.canon(x));print(json.dumps(x))
'''

if __name__=='__main__':
    q='qualification/tree_partial_resume_v1/'
    raw=remote('hrl-174-new',"import pathlib,json,base64\np=pathlib.Path("+repr(NATIVE+'/tools/copy_engine.py')+");print(json.dumps({'b':base64.b64encode(p.read_bytes()).decode()}))")
    install(q+'BEFORE_copy_engine.py',base64.b64decode(raw['b']))
    install(q+'copy_engine.py',(R/'tools/copy_engine.py').read_bytes())
    x=remote('hrl-174-new',CODE,90);save('t2/tree_partial_repair/QUALIFICATION.json',x);print(json.dumps(x))
