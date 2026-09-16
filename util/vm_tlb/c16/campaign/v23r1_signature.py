import json,sqlite3
from pathlib import Path
root=Path('/data/c16/deepseek_v23r1');out={}
for target,inside,replay in [('MLA','C16_V23R1_MLA_KV_B_INCONTEXT','C16_V23R1_MLA_KV_B_EXPAND_REPLAY'),('MOE','C16_V23R1_MOE_EXPERT_DOWN_INCONTEXT','C16_V23R1_MOE_EXPERT_DOWN_REPLAY')]:
 out[target]={}
 for kind,db,name in [('in_context',root/'incontext.sqlite',inside),('replay',root/f'{target}_replay.sqlite',replay)]:
  con=sqlite3.connect(db);sql='''select s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,count(*) from NVTX_EVENTS z join CUPTI_ACTIVITY_KIND_KERNEL k on k.start>=z.start and k.end<=z.end join StringIds s on s.id=k.demangledName where z.text=? group by s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ order by s.value''';out[target][kind]=[{'function':x[0],'grid':[x[1],x[2],x[3]],'block':[x[4],x[5],x[6]],'count':x[7]} for x in con.execute(sql,(name,))]
 out[target]['equivalent']=out[target]['in_context']==out[target]['replay']
(root/'SIGNATURE_GATE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if not all(x['equivalent'] for x in out.values()):raise SystemExit(1)
