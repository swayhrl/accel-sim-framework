"""Byte/CRC resource proof only; no SASS parsing, GPU, or scientific validator."""
import pathlib,json,lzma,hashlib,time,importlib.util,shutil
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
T=B/'objects/stage_retained_native_rtx_post_epoch3_tail2_20261025_v1'
assert hashlib.sha256((T/'MANIFEST.json').read_bytes()).hexdigest()=='b4e90fa3243512e6967f342bd3f22928175f72bcf83d213b9dc6052d7e873f5b'
m=json.loads((T/'MANIFEST.json').read_text());by={r['path']:r for r in m['files']}
class Reader:
 def __init__(self,f):self.f=f;self.n=0;self.start=time.monotonic();self.h=hashlib.sha256()
 def read(self,n=-1):
  b=self.f.read(n);self.n+=len(b);self.h.update(b);time.sleep(max(0,self.n/(15*2**20)-(time.monotonic()-self.start)));return b
 def seekable(self):return False
rows=[]
for num in [99,100]:
 name='kernel-%d-ctx_0x559aa8cd3680'%num;pfx='post/'+name+'.trace_work/'
 fs=[r for r in m['files']if r['path'].startswith(pfx)]
 checkpoint=T/'tree'/pfx/'CHECKPOINT.json';cp=json.loads(checkpoint.read_text());assert cp['partition_complete']and len(cp['groups'])==9 and len(cp['partition_members'])==16
 pending=[]
 for part in cp['partition_members']:
  idx=int(pathlib.Path(part['name']).stem.split('-')[-1])
  if str(idx)in cp['groups']:continue
  rel=pfx+part['name'];src=T/'tree'/rel;expanded=0
  with src.open('rb')as inp:
   reader=Reader(inp)
   with lzma.LZMAFile(reader,'rb')as dec:
    for b in iter(lambda:dec.read(2**20),b''):expanded+=len(b)
   while reader.read(2**20):pass
  assert reader.h.hexdigest()==part['sha256']==by[rel]['sha256']and reader.n==part['bytes']
  assert expanded*3<512*2**20
  pending.append({'partition':part['name'],'compressed_bytes':reader.n,'full_sha256':reader.h.hexdigest(),'expanded_bytes_and_full_XZ_CRC':expanded})
 base=sum(r['bytes']for r in fs);scratch=max(r['expanded_bytes_and_full_XZ_CRC']for r in pending)*3
 projected=base+scratch+64*2**20+8*2**20
 assert projected<768*2**20
 rows.append({'kernel':name,'retained_single_kernel_stage_bytes':base,'source_raw_staged_on_Native':False,'raw_source_SHA_method':'NAS raw is read by pinned HOT85ff aggregate15MiB pure digest adapter; frozen5d partition_complete means no raw parse/repartition','retained_files':len(fs),'old_complete_frames_reused':9,'pending_partitions':pending,'max_shard_expanded_x3_bytes':scratch,'final_group_planning_allowance_bytes':64*2**20,'small_control_planning_allowance_bytes':8*2**20,'engineering_peak_projection_bytes':projected,'stage_limit_polled_bytes':768*2**20,'projection_is_not_filesystem_quota_or_guaranteed_fit':True})
s=importlib.util.spec_from_file_location('a',C/'read_native_foreign_reserve_v1.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);authority=a.snapshot();floor=5*2**30+authority['sum_all_records_reserved_write_bytes']+2**30+64*2**20
def admission(free,reserved,used=0,entering=False):
 f=5*2**30+reserved+2**30+64*2**20
 return free>=f+max(0,768*2**20-used)+(128*2**20 if entering else 0)
tests=[]
for reserved in [1879048192,14763950080]:
 f=5*2**30+reserved+2**30+64*2**20;threshold=f+768*2**20+128*2**20
 assert admission(threshold,reserved,entering=True)and not admission(threshold-1,reserved,entering=True)
 tests.append({'reserved':reserved,'exact_boundary':threshold,'boundary_PASS':True,'one_byte_short_REJECT':True})
result={'status':'LAST2_SINGLE_HELPER_768M_PRIVATE_BYTE_CRC_BOUNDARY_PROOF_PASS','kind':'RESOURCE_ENGINEERING_PROOF_NOT_SCIENTIFIC_REVALIDATION','kernel_rows':rows,'admission_boundary_cases':tests,'current_authority':authority,'dynamic_floor':floor,'start_free_required_including768M_and128M_hysteresis':floor+768*2**20+128*2**20,'current_free':shutil.disk_usage(N).free,'Native_payload_created':0,'all_pending14_partition_fullSHA_and_XZ_CRC_checked':True,'SASS_records_parsed':0,'GPU_SIM_109_or_authority_writes':0,'runtime_requirement':'single helper; only partition/frame work copied Native, original raw remains NAS; fresh Native work; poll whole-stage<=768MiB and recursiveRSS; stop own tree if actual output or free margin exceeds projected budget; no shortening or incomplete promotion','unix':time.time()}
p=C/'STENCIL_SINGLE768_RESOURCE_PROOF_V2.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'projected_peaks':[r['engineering_peak_projection_bytes']for r in rows],'start_free_required':result['start_free_required_including768M_and128M_hysteresis'],'free':result['current_free']}))
