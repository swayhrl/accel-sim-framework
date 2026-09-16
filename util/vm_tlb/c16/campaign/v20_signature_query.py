import json,sqlite3
from pathlib import Path
root=Path('/data/c16/qwen3_runtime_v14/v20')
out={}
for scenario in ('S2_TEXT','S3_TEXT'):
 out[scenario]={}
 for kind,name in [('incontext',f'C16_V20_{scenario}_INCONTEXT_REPEAT_K'),('isolated',f'C16_V20_{scenario}_ISOLATED_REPEAT_K')]:
  db=root/f'{scenario}_{"incontext_full" if kind=="incontext" else "isolated_full"}.sqlite'
  con=sqlite3.connect(db)
  sql='''select s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,count(*) from NVTX_EVENTS z join CUPTI_ACTIVITY_KIND_KERNEL k on k.start>=z.start and k.end<=z.end join StringIds s on s.id=k.demangledName where z.text=? group by s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ order by s.value'''
  rows=[{'function':r[0],'grid':[r[1],r[2],r[3]],'block':[r[4],r[5],r[6]],'count':r[7]} for r in con.execute(sql,(name,))]
  out[scenario][kind]={'nvtx':name,'kernels':rows}
 for_kind=out[scenario]
 for_kind['signature_equivalent']=for_kind['incontext']['kernels']==for_kind['isolated']['kernels']
(root/'v20_signature_gate.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
if not all(out[s]['signature_equivalent'] for s in out):raise SystemExit(1)
