from closure_local import *
import ast
tree=ast.parse((B/'tools/collect_audit.py').read_text(encoding='utf8'))
SNAP=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SNAP' for t in n.targets))
UTIL=SNAP[:SNAP.index('x=dict(')]
def checkpoint(label):
 rs=[]
 for alias,end in [('hrl','SOURCE'),('hrl-174-new','TARGET')]:
  x=remote(alias,SNAP,60);save('resource/'+label+'_'+end+'.json',x);rs.append(x)
 print(label,[(r['host'],r['resources']['/proc/pressure/io'].splitlines()[0],len(r['processes'])) for r in rs],flush=True)
 return rs
if __name__=='__main__':checkpoint('START')
