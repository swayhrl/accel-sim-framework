#!/usr/bin/env python3
"""Reproduce candidate bytes/hash without writing an input or admission receipt."""
import argparse,csv,gzip,hashlib,json,re
from pathlib import Path

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024**2),b''):h.update(chunk)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',type=Path,required=True);ap.add_argument('--index',type=Path,required=True);ap.add_argument('--original-dir',type=Path,required=True);a=ap.parse_args()
    identity=json.loads(a.identity.read_text());contract=identity['identity_contract']
    assert hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()==identity['bundle_sha256']
    assert sha(a.index)=='2266153d542547398f7ec807eb92a3be1c68678b2bab888bd50011d5220c15b7'
    with gzip.open(a.index,'rt') as f:risk={int(r['line']):r for r in csv.DictReader(f,delimiter='\t') if r['workload']=='btree'}
    assert len(risk)==6000
    oldhash=hashlib.sha256();replayhash=hashlib.sha256();n=changed=size=0
    with (a.original_dir/'kernel-1.traceg').open('rb') as f:
        for number,line in enumerate(f,1):
            oldhash.update(line);result=line
            if number in risk:
                assert hashlib.sha256(line).hexdigest()==risk[number]['original_line_sha256']
                spans=list(re.finditer(rb'\S+',line));tokens=[v.group() for v in spans]
                assert int(tokens[4],16)==0x1c40
                mask=int(tokens[5],16);assert mask.bit_count()==1
                opi=7+int(tokens[6]);widthi=opi+2+int(tokens[opi+1]);modei=widthi+1
                assert tokens[opi]==b'LDG.E.SYS' and int(tokens[widthi])==4 and tokens[modei]==b'0' and len(tokens[modei+1:])==32
                lane=mask.bit_length()-1;selected=tokens[modei+1+lane]
                result=line[:spans[modei+1].start()]+selected+b'\n';n+=1;changed+=int(tokens[modei+1],16)!=int(selected,16)
            replayhash.update(result);size+=len(result)
    assert oldhash.hexdigest()==contract['original_sha256']['kernel-1.traceg'] and (n,changed)==(6000,5792)
    for member in contract['files']:
        name=member['name'];candidate=Path(identity['owned_input_directory'])/name
        assert sha(candidate)==member['sha256'] and candidate.stat().st_size==member['bytes']
        if name=='kernel-1.traceg':assert replayhash.hexdigest()==member['sha256'] and size==member['bytes']
        else:assert sha(a.original_dir/name)==member['sha256']==contract['original_sha256'][name]
    print(json.dumps(dict(status='PASS_READONLY_BYTE_REPLAY',bundle_sha256=identity['bundle_sha256'],derived_kernel1_sha256=replayhash.hexdigest(),touched=n,changed_addresses=changed,same_addresses=n-changed,new_files_written=0)))
if __name__=='__main__':main()
