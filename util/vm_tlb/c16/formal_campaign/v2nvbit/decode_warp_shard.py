#!/usr/bin/env python3
import argparse,hashlib,json,struct
from pathlib import Path
H=struct.Struct("<8sIIQQQ");R=struct.Struct("<6I32Q")
def sha(p):
 h=hashlib.sha256();
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def decode(p):
 b=Path(p).read_bytes(); magic,idx,occ,count,overflow,keep=H.unpack_from(b);
 if magic!=b"C16WARP1" or len(b)!=H.size+keep*R.size: raise ValueError("invalid C16WARP1")
 addrs=set();pages=set();lines=set();
 for off in range(H.size,len(b),R.size):
  v=R.unpack_from(b,off); mask=v[1]
  for lane,a in enumerate(v[6:]):
   if mask>>lane&1:addrs.add(a);pages.add(a>>12);lines.add(a>>7)
 return {"format":"C16WARP1","static_index":idx,"occurrence":occ,"callback_warp_records":count,"overflow":overflow,"records_written":keep,"unique_exact_addresses":len(addrs),"unique_4k_pages":len(pages),"unique_128b_lines":len(lines),"sha256":sha(p)}
def main():
 a=argparse.ArgumentParser();a.add_argument("trace");a.add_argument("--output",required=True);x=a.parse_args();Path(x.output).write_text(json.dumps(decode(x.trace),indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
