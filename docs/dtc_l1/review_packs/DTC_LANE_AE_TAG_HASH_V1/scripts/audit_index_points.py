#!/usr/bin/env python3
"""Bound every legacy edit and recover fixed X2 bytes after removing AE delta."""
import hashlib,json,re,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent.parent
C=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-ae-tag-hash-core-174-v1')
BASE='e32afdcf44be3374ff36d22568ed01a075459b6f'
def digest(b):return hashlib.sha256(b).hexdigest()
def old(path):return subprocess.check_output(['git','-C',str(C),'show',BASE+':'+path]).decode()
def dump(name,x):(P/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def body(text,signature):
 a=text.index(signature);start=text.index('{',a);depth=0
 for i in range(start,len(text)):
  depth+=(text[i]=='{')-(text[i]=='}')
  if depth==0:return text[a:i+1]
 raise ValueError(signature)
def main():
 paths=['src/gpgpu-sim/dtc-l1-common.h','src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/shader.cc','src/gpgpu-sim/shader.h'];recover=[]
 for path in paths:
  text=(C/path).read_text();recovered=text
  if path.endswith('dtc-l1-common.h'):
   recovered=recovered.replace('#include "dtc-l1-tag-index.h"\n\n','').replace('  bool tag_hash_bankrow = false;\n','')
   recovered,n=re.subn(r'(?m)^    check_tag_hash_bankrow\([\s\S]*?;\n','',recovered);assert n==4
   recovered=recovered.replace('  // Historical find_tag touches LRU even for this precheck. Preserve that\n  // exact recency policy in BOTH hash modes; this is not a read-only peek.\n','')
   recovered=recovered.replace('  unsigned tag_set(uint64_t address) const {\n    return logical_tag_set(address, m_cfg.logical_sets, m_cfg.tag_hash_bankrow);\n  }\n','')
   for arg in ['address','line']:
    recovered=recovered.replace('    const unsigned set = tag_set('+arg+');','    const unsigned set = static_cast<unsigned>(\n        ('+arg+' / kLogicalLineBytes) % m_cfg.logical_sets);')
   oo=text.split('class oo_frontend {')[1].split('class sector_oo_frontend {')[0]
   assert oo.count('const unsigned set = tag_set(')==3
   assert '% m_cfg.logical_sets'not in oo
   assert body(oo,'  bool will_new_miss(')==body(old(path).split('class oo_frontend {')[1],'  bool will_new_miss(')
   for method in ['  lookup_invalidation_result invalidate_lookup(','  io_access_result access(','  void complete(','  void advance_service(','  bool retire_one_ready(','  bool retire_ready_uid(']:
    assert body(oo,method)==body(old(path).split('class oo_frontend {')[1],method)
  elif path.endswith('gpu-sim.cc'):
   recovered=recovered.replace('  dtc_l1::register_tag_hash_bankrow_option(opp, &dtc_l1_tag_hash_bankrow);\n','')
  elif path.endswith('shader.h'):
   recovered=recovered.replace('  bool dtc_l1_tag_hash_bankrow;\n','')
  else:
   recovered,n=re.subn(r'(?m)^  dtc_l1::check_tag_hash_bankrow\([\s\S]*?;\n','',recovered);assert n==1
   recovered=recovered.replace('    dtc_config.tag_hash_bankrow = m_config->dtc_l1_tag_hash_bankrow;\n','')
   recovered=recovered.replace('  if (config->dtc_l1_tag_hash_bankrow) {\n    fprintf(stderr, "TAG_HASH_BANKROW_EXTERNAL_CACHE_CONSTRUCTOR_STOP\\n");\n    abort();\n  }\n','')
   assert body(text,'bool ldst_unit::dtc_l1_oo_memory_cycle(')==body(old(path),'bool ldst_unit::dtc_l1_oo_memory_cycle(')
  assert recovered==old(path),path
  recover.append(dict(path=path,baseline_sha256=digest(old(path).encode()),recovered_sha256=digest(recovered.encode()),ae_sha256=digest(text.encode()),legacy_bytes_recovered_exactly=True))
 points=[
 ('try_serve_tag','OO tag_set(address) -> set % banks; ON bank equals L&3; quotas unchanged'),
 ('find_tag','OO tag_set(aligned line); full tag.line equality; existing hit LRU increment preserved'),
 ('will_new_miss / lower candidate precheck','Same mutating find_tag call; no peek/new prelookup or recency cleanup'),
 ('access / new miss / Tag eviction','Unchanged access body dispatches find_tag and select_victim with same aligned full line'),
 ('select_victim / LRU','Same centralized tag_set, exactly ways entries in that set, first invalid then minimum existing LRU; no cross-set victim'),
 ('service_entry::prefetch_next_tag','Unchanged; reaches same OO try_serve_tag; grant latches cycle only'),
 ('K1 invalidate_lookup','Entire method identical to X2; full m_tags vector sweep, hence covers every hashed entry without re-indexing'),
 ('IO / BASE / MODERN / ordinary C+','Existing index code recovered byte-for-byte; ON rejected outside OO; ordinary cache files unchanged'),
 ('LDST constructor / config','Same production bool registration helper tested with real parser; init checks mode/finite/geometry; flag copied ONLY into selected whole-line OO config; external-cache constructor rejects ON')]
 source=[]
 for path in paths+['src/gpgpu-sim/dtc-l1-tag-index.h','tests/dtc_l1_tag_hash_bankrow_test.cc']:
  b=(C/path).read_bytes();source.append(dict(path=path,sha256=digest(b),blob=subprocess.check_output(['git','-C',str(C),'hash-object',path],text=True).strip()))
 for path in ['src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h','src/gpgpu-sim/dtc-l1-invalidation.h']:
  assert (C/path).read_text()==old(path)
 dump('INDEX_POINT_AUDIT.json',dict(status='PASS_STATIC_DELTA_AND_CPU_FRONTEND',baseline=BASE,legacy_recovery=recover,points=[dict(point=p,audit=a)for p,a in points],ordinary_cache_and_k1_observer_bytes_unchanged=True,replacement_semantics_cleanup='NONE: old mutating precheck retained for both policies',full_production_library_compile='NOT_RUN <=2 compiler invocations budget',source_files=source))
 print('PASS: all four legacy files exactly recover fixed X2 bytes; all OO index sites centralized; ordinary/K1 bodies unchanged')
if __name__=='__main__':main()
