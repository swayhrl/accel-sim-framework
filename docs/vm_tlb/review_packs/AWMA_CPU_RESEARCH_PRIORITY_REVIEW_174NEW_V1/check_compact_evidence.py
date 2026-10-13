#!/usr/bin/env python3
"""Checks published compact evidence with CPU standard library only."""
import argparse, collections, csv, hashlib, io, json, subprocess
from pathlib import Path
C = '7bd31fae4c54e121d54743a803d978ee02a64959'
P = 'docs/vm_tlb/review_packs/AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1/'
def main():
    a=argparse.ArgumentParser(); a.add_argument('--output',required=True); args=a.parse_args()
    names=['B0_REPEATABILITY.json','FAILURE_COORDINATES.tsv','TOKEN_FREQUENCIES.tsv','PRE_DIAGNOSTIC_PLAN.json','NUMERIC_ATTRIBUTION.json']
    data={n:subprocess.check_output(['git','show',C+':'+P+n]) for n in names}
    repeat=json.loads(data[names[0]])
    coords=list(csv.DictReader(io.StringIO(data[names[1]].decode()),delimiter='\t'))
    freq={int(r['token_id']):r for r in csv.DictReader(io.StringIO(data[names[2]].decode()),delimiter='\t')}
    first=[r for r in coords if r['category']=='first_row_major']
    top=[r for r in coords if r['category']=='largest_excess']
    keys=lambda rows:{(int(r['row']),int(r['column'])) for r in rows}
    assert len(first)==25 and len(top)==25 and keys(first)==keys(top)
    checked=[]
    for r in first:
        row,col=int(r['row']),int(r['column'])
        ref,got=float(r['reference']),float(r['candidate'])
        delta,allowed=abs(got-ref),0.01+0.01*abs(ref)
        assert delta>allowed and int(r['flat_index'])==row*2048+col
        assert float(r['abs_diff'])==delta and abs(float(r['allowed'])-allowed)<1e-7
        assert int(r['input_frequency'])==int(freq[row]['input_count'])
        assert int(r['label_frequency'])==int(freq[row]['label_count'])
        checked.append({'row':row,'column':col,'delta':delta,'allowed_double':allowed})
    counts=collections.Counter(r['row'] for r in checked)
    assert dict(counts)=={198:12,284:13}
    assert repeat['metrics']['gradient']['violations']==25
    assert keys(first)=={(r['row'],r['column']) for r in repeat['metrics']['gradient']['first32_row_major']}
    out={'status':'PASS','kind':'CPU_COMPACT_PUBLISHED_COORDINATE_RECHECK','commit':C,
         'input_blob_sha256':{n:hashlib.sha256(b).hexdigest() for n,b in data.items()},
         'unique_failure_coordinates':25,'row_counts':dict(counts),
         'all_failed_rows_present_in_input':all(int(freq[row]['input_count'])>0 for row in counts),
         'row198_input_label_count':[int(freq[198]['input_count']),int(freq[198]['label_count'])],
         'row284_input_label_count':[int(freq[284]['input_count']),int(freq[284]['label_count'])],
         'input_label_count_sums':[sum(int(r['input_count']) for r in freq.values()),sum(int(r['label_count']) for r in freq.values())],
         'failure_fraction':25/(128256*2048),
         'largest_excess':max(checked,key=lambda r:r['delta']-r['allowed_double']),
         'required_observable_qualifications':{n:m['qualified'] for n,m in repeat['metrics'].items()},
         'scope':'Published coordinate arithmetic only; no raw tensors, torch, model, CUDA or kernel execution.'}
    Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':'PASS','unique_coordinates':25,'row_counts':dict(counts)}))
if __name__=='__main__': main()
