#!/usr/bin/env python3
"""Recompute contextual overlap at the accepted VM-entry boundary."""
import argparse,csv,lzma,pathlib
PREFIXES={"P1":33,"P2":32,"P4":30,"P8":26,"P16":18,"P34":0}
LOCAL_MEM_SIZE_MAX=1<<24

def base(op): return op.split('.',1)[0]
def lanes(mask): return [i for i in range(32) if int(mask,16)&(1<<i)]
def space(op,first,shmem,local):
 b=base(op)
 if b in {"LDG","STG","ATOMG","RED","LDGSTS"}: return "global"
 if b in {"LDL","STL"}: return "local"
 if b not in {"LD","ST"}: return "excluded"
 if not shmem or not local: return "shared"
 if shmem<=first<local:return "shared"
 if local<=first<local+LOCAL_MEM_SIZE_MAX:return "local"
 return "global"
def parse(parts,shmem,local):
 i=0
 if not parts or parts[0].startswith('#'):return None
 int(parts[i],16);i+=1; mask=parts[i];i+=1; nd=int(parts[i]);i+=1+nd
 op=parts[i];i+=1; ns=int(parts[i]);i+=1+ns; width=int(parts[i]);i+=1
 if not width:return None
 mode=int(parts[i]);i+=1; active=lanes(mask)
 if mode==0: addrs=[int(parts[i+n],16) for n in range(len(active))]
 elif mode==1:
  addr,stride=int(parts[i],16),int(parts[i+1]); addrs=[addr+n*stride for n in range(len(active))]
 elif mode==2:
  addr=int(parts[i],16);i+=1;addrs=[addr+int(parts[i+n]) for n in range(len(active))]
 else:raise ValueError('unknown address mode %s'%mode)
 return (space(op,addrs[0],shmem,local),addrs) if addrs else None
def member(path):
 shmem=local=0;p4=set();p64=set();counts={x:0 for x in ('global','local','shared','excluded')}
 with lzma.open(path,'rt',errors='strict') as f:
  for line in f:
   if line.startswith('-shmem base_addr = '):shmem=int(line.rsplit(' ',1)[1],16);continue
   if line.startswith('-local mem base_addr = '):local=int(line.rsplit(' ',1)[1],16);continue
   if not line or line[0] in '#-' or '=' in line or line.startswith(('thread ','warp ','insts ','BEGIN')):continue
   x=parse(line.split(),shmem,local)
   if not x:continue
   sp,addrs=x;counts[sp]+=len(addrs)
   if sp in {'global','local','param_local'}:p4.update(a>>12 for a in addrs);p64.update(a>>16 for a in addrs)
 return p4,p64,counts
def overlap(path,q,members,shift):
 with open(path,'w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['prefix','predecessor_union_pages','q05_pages','intersection_pages','q05_coverage_fraction'])
  for label,first in PREFIXES.items():
   u=set().union(*(members[n][shift] for n in range(first,34)));x=u&q
   w.writerow([label,len(u),len(q),len(x),'%.12f'%(len(x)/len(q) if q else 0)])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=pathlib.Path,required=True);ap.add_argument('--output-dir',type=pathlib.Path,required=True);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
 files=lambda n:next((a.bundle/'traces').glob('kernel-%d-*.traceg.xz'%n))
 m={}
 for n in range(35):
  x,y,z=member(files(n));m[n]={12:x,16:y,'counts':z}
 q4,q64=m[34][12],m[34][16]
 overlap(a.output_dir/'TRANSLATION_RELEVANT_PAGE_OVERLAP_4K.tsv',q4,m,12);overlap(a.output_dir/'TRANSLATION_RELEVANT_PAGE_OVERLAP_64K.tsv',q64,m,16)
 with open(a.output_dir/'TRANSLATION_RELEVANT_Q05_PAGE_DISTANCE.tsv','w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['page_size','q05_page','nearest_predecessor_member','distance_kernels','observed_in_predecessor'])
  for name,shift,q in [('4K',12,q4),('64K',16,q64)]:
   for page in sorted(q):
    near=next((n for n in range(33,-1,-1) if page in m[n][shift]),None);w.writerow([name,hex(page),'' if near is None else near,'' if near is None else 34-near,'YES' if near is not None else 'NO'])
 with open(a.output_dir/'TRANSLATION_RELEVANT_SCOPE_COUNTS.tsv','w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['member','global_lane_addresses','local_lane_addresses','shared_lane_addresses','excluded_lane_addresses'])
  for n in range(35):
   c=m[n]['counts'];w.writerow([n,c['global'],c['local'],c['shared'],c['excluded']])
if __name__=='__main__':main()