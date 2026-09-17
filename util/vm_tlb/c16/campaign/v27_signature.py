import json,sqlite3
from pathlib import Path
r=Path('/data/c16/deepseek_v27');out={}
for k,db,name in [('in_context',r/'qk_incontext.sqlite','C16_V27_MIXED_PERSISTENT_QK_INCONTEXT'),('replay',r/'qk_replay.sqlite','C16_V27_MIXED_PERSISTENT_QK_REPLAY')]:
 c=sqlite3.connect(db);q='''select s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,count(*) from NVTX_EVENTS z join CUPTI_ACTIVITY_KIND_KERNEL k on k.start>=z.start and k.end<=z.end join StringIds s on s.id=k.demangledName where z.text=? group by s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ order by s.value''';out[k]=[{'function':x[0],'grid':[x[1],x[2],x[3]],'block':[x[4],x[5],x[6]],'count':x[7]} for x in c.execute(q,(name,))]
target=lambda rows:[x for x in rows if 'internal::gemvx::kernel' in x['function']]
out['target_gemv_in_context']=target(out['in_context']);out['target_gemv_replay']=target(out['replay']);out['asynchronous_non_target_in_context']=[x for x in out['in_context'] if x not in out['target_gemv_in_context']];out['equivalent']=out['target_gemv_in_context']==out['target_gemv_replay'];(r/'QK_SIGNATURE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if not out['equivalent']:raise SystemExit(1)
