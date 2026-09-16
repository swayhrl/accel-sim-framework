import sqlite3,json
d=sqlite3.connect('/data/c16/qwen3_runtime_v14/v18r2_repeatk.sqlite')
for n in ['C16_V18R2_REPEAT_K_DIRECT']:
 q="""select s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,count(*) from NVTX_EVENTS z join CUPTI_ACTIVITY_KIND_KERNEL k on k.start>=z.start and k.end<=z.end join StringIds s on s.id=k.demangledName where z.text=? group by s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ order by s.value""";print(n,json.dumps(d.execute(q,(n,)).fetchall()))
