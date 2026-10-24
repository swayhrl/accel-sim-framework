#!/usr/bin/env python3
"""Stable external CTA/warp grouping. Explicitly waits for sort and XZ close/EOF."""
import argparse,collections,hashlib,itertools,json,lzma,os,pathlib,re,shutil,subprocess,tempfile
def sha(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  while True:
   block=f.read(2**20)
   if not block:break
   h.update(block)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('traces');p.add_argument('--scratch-budget',type=int,default=64*2**30);a=p.parse_args();R=pathlib.Path(a.traces).resolve()
 lists=[x for x in sorted(R.glob('kernelslist*'))if not x.name.endswith('.g')];assert lists
 receipts=[]
 for ci,cmd in enumerate(lists):
  output=R/('kernelslist.g'if len(lists)==1 else cmd.name+'.g')
  with output.open('x')as commands:
   for command in cmd.read_text().splitlines():
    if not command.strip():continue
    if command.startswith('Memcpy'):commands.write(command+'\n');continue
    source=R/command;assert source.parent==R and source.name.startswith('kernel-') and source.name.endswith('.trace.xz')
    dest=source.with_name(source.name.replace('.trace.xz','.traceg.xz'));counts=collections.Counter();header=[];total=0;records=0
    with tempfile.TemporaryDirectory(prefix='ada-sort-',dir=R.parent)as temp:
     temp=pathlib.Path(temp);body=temp/'body';ordered=temp/'ordered'
     with lzma.open(source,'rt')as inp,body.open('w')as spool:
      for line in inp:
       if not re.match(r'^\d+ \d+ \d+ \d+ ',line):
        if records:raise RuntimeError('header after records')
        header.append(line);continue
       keys=line.split(maxsplit=4);key=tuple(map(int,keys[:4]));counts[key]+=1;records+=1;total+=len(line);spool.write(line)
       if total*3>a.scratch_budget or (records%4096==0 and shutil.disk_usage(temp).free<5*2**30):raise RuntimeError('postprocess scratch reserve')
     assert records and any('-accelsim tracer version = 7'in x for x in header)
     subprocess.run(['/usr/bin/sort','-s','--parallel=1','-S64M','-T',str(temp),'-k3,3n','-k2,2n','-k1,1n','-k4,4n','-o',str(ordered),str(body)],env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},check=True)
     with dest.open('xb')as raw:
      with lzma.LZMAFile(raw,'w',format=lzma.FORMAT_XZ,preset=1)as compressed:
       def write(x):compressed.write(x.encode())
       write(''.join(header)+'\n');previous_cta=None;previous_warp=None
       with ordered.open()as seq:
        for line in seq:
         keys=line.split(maxsplit=4);cta=tuple(map(int,keys[:3]));warp=int(keys[3])
         if cta!=previous_cta:
          if previous_cta is not None:write('\n#END_TB\n')
          write('\n#BEGIN_TB\nthread block = %d,%d,%d\n'%cta);previous_cta=cta;previous_warp=None
         if warp!=previous_warp:write('\nwarp = %d\ninsts = %d\n'%(warp,counts[(*cta,warp)]));previous_warp=warp
         write(keys[4])
       write('\n#END_TB\n')
      raw.flush();os.fsync(raw.fileno())
    # Complete reopen/decompression is mandatory; returning before compressor EOF is forbidden.
    expanded=0
    with lzma.open(dest,'rb')as readback:
     while True:
      block=readback.read(2**20)
      if not block:break
      expanded+=len(block)
    receipts.append(dict(source=str(source),grouped=str(dest),source_sha256=sha(source),grouped_sha256=sha(dest),records=records,warps=len(counts),ctas=len(set(x[:3]for x in counts)),expanded_bytes=expanded,compressor_eof_and_reopen=True))
    commands.write(dest.name+'\n');commands.flush();os.fsync(commands.fileno())
 with(R/'POSTPROCESS_V7.json').open('x')as f:json.dump(receipts,f,indent=2);f.write('\n')
 print(json.dumps(receipts))
if __name__=='__main__':main()
