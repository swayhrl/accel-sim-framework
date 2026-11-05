from pathlib import Path
import json,gzip,csv,hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/ai_workload_research/runs/QWEN_DECODE_MEMORY_COMPUTE_ATTRIBUTION_109_V10'
def main():
 p=OUT/'cpu/COST_LEDGER_KERNELS.tsv.gz'
 rows=list(csv.DictReader(gzip.decompress(p.read_bytes()).decode().splitlines(),delimiter='\t'))
 copies=[v for v in rows if v['point']=='B2_N32' and 'direct_copy' in v['kernel_name']]
 ns=sum(int(v['duration_ns']) for v in copies);assert len(copies)==2232 and ns==3197527
 src=ROOT.parent/'accel-sim-aiarch-decode-cost-and-memory-mechanism-109-v9/docs/ai_workload_research/runs/QWEN_DECODE_COST_MEMORY_MECHANISM_109_V9/TIMELINE_ANALYSIS.json'
 d=next(v['profiled_CUDA_event_ms'] for v in json.loads(src.read_text())['requests'] if v['point']=='B2_N32')
 a=json.loads((OUT/'LOCAL_OPTIMIZATION_BOUND.json').read_text())
 assert a['summed_copy_ms']==ns/1e6 and a['same_profile_full_generate_ms']==d and a['fraction']==ns/1e6/d
 print('PASS exact same-profile local upper-bound derivation; not observed speedup')
if __name__=='__main__':main()
