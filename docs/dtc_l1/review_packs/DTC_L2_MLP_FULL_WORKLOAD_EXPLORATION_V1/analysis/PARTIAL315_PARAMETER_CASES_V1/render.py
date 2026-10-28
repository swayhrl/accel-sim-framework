import json,pathlib,hashlib
p=pathlib.Path(__file__).resolve().parent
d=json.loads((p/'EVIDENCE.json').read_text(encoding='utf-8'))
rows=d['pairs']; profiles=list(d['statistics'])
def fmt(v): return 'missing' if v is None else f'{v:.6f}'
def names(rs): return ', '.join(f"{r['program']} {r['DH_self_speedup']:.4f}x" for r in rs) or 'none'
text=['# 315 accepted-cell fixed-snapshot parameter cases',
'Read-only evidence consumption of commit `280abe32e1090366cfaabaf5895662300c2f9f27`, checkpoint `PARTIAL_DASHBOARD_20261028_1627_V1/report.json`, snapshot UTC `'+d['snapshot_utc']+'`. The 315 cells comprise 309 new accepted runs and 6 legal references; this is neither 315 workloads nor a finished experiment. No live results, huge raw logs, models, registration or policy changes were used.',
'## Population discipline',
'Ratios are **DH P0 cycles / same-input DH variant cycles**. Every GM uses one uniform profile. `available` is that profile\'s currently paired population; `common30` is the exact intersection across all eight non-P0 profiles. Different available populations cannot establish a final winner. Original scan/M16 negative stays unaccepted; supplemental R2 and seven unresolved inputs are excluded. No accepted non-P0 CH exists: CH speedup, CH/DH variant ratios and DTC relative improvement remain unavailable.',
'| Profile | Available n/35 | Available GM | Fixed common30 GM |',
'|---|---:|---:|---:|']
for profile,z in d['statistics'].items():
 s=z['ALL'];text.append(f"| {profile} | {s['available']['n']}/35 | {s['available']['GM']:.6f} | {s['common30']['GM']:.6f} |")
excluded=sorted(set(r['program'] for r in rows if r['input_digest'] not in d['common30_population']))
text+=['Common30 excludes '+', '.join(excluded)+'. The F available31 adds scan to common30; its M16 technical negative prevents scan entering the all-profile intersection. This explains part of the F GM difference without imputing any missing cycle.',
'## Uniform F128/F256: benefit and regression both retained',
'| Profile / suite | Available n/expected | Available GM | + / = / - | Common n / GM |',
'|---|---:|---:|---:|---:|']
for profile in ['F128','F256']:
 for suite,z in d['statistics'][profile].items():
  a,c=z['available'],z['common30'];text.append(f"| {profile} / {suite} | {a['n']}/{a['expected_n']} | {a['GM']:.6f} | {a['positive']} / {a['neutral']} / {a['negative']} | {c['n']} / {c['GM']:.6f} |")
for profile,c in d['uniform_F_cases'].items():
 text += [f"**{profile} positive:** {names(c['positive'])}.",f"**{profile} negative:** {names(c['negative'])}.",
          f"**{profile} missing:** "+'; '.join(f"{r['program']} (DH P0 {r['P0']['state']}; variant {r['variant']['state']})" for r in c['missing'])+'.']
text+=['## Requested program cases',
'All eight requested programs have all eight DH variant/P0 pairs at this snapshot; their original input identities stay fixed. Full input and binding SHA, P0/variant cycles, cohort, UUID, RESULT path/SHA and Core/Framework/binary are in each `EVIDENCE.json:pairs[]` record. The table gives input SHA prefixes only for readability.',
'| Program / input SHA prefix | E384 | E768 | M8 | M16 | Q64 | Q128 | F128 | F256 |',
'|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for name in d['focus_programs']:
 rs=[r for r in rows if r['program']==name];text.append('| '+name+' / '+rs[0]['input_digest'][:16]+' | '+' | '.join(fmt(next(r['DH_self_speedup'] for r in rs if r['profile']==pr)) for pr in profiles)+' |')
text += [
'The following are **counter associations**, not a causal cycle decomposition. Changes compare the same design and input with DH P0:',
'- **ATAX F256:** 31,880,220 -> 31,321,955 cycles (1.017823x); DRAM reads -2.213%, L2 reads -2.809%, reservation-fail events -3.100%. Last-printed MRQ average rises 745 -> 1,873 despite faster completion. Q128 regresses to 0.943917x while DRAM reads rise 6.118%; E384 and E768 both yield 1.028813x. More queue capacity does not imply lower reported latency or universal benefit.',
'- **MVT F256:** 34,687,540 -> 35,093,446 cycles (0.988434x); DRAM reads +0.996%, L2 reads +1.664%, reservation-fail events -2.572%, MRQ 738 -> 1,798. M8/M16 are effectively flat (1.000052x/1.000039x). Fewer reservation failures alone do not prove higher throughput.',
'- **BICG M16:** 28,685,812 -> 28,338,906 cycles (1.012241x), DRAM reads -0.575%, reservation-fail events -3.624%, MRQ 791 -> 777. F256 instead yields 0.993156x despite DRAM reads -1.297%, with MRQ 791 -> 2,074. Q128 also regresses despite fewer reservation-fail events.',
'- **3MM / GEMM:** all eight configurations are exactly flat at 2,402,871 / 826,089 cycles. Recorded DRAM reads are explicitly **0 -> 0**, so percentage change is null due to zero denominator, not missing counters. L2 reads are 5,186,824 / 1,716,504; L2 read misses and reservation failures are zero; MRQ average is missing. These are simulator trace/kernel statistics, not proof that the real application never accesses DRAM. GEMM is PolyBench input fc0705..., distinct from Parboil sgemm ffc8.... Prior GEMM source/trace mapping is archived in `agents/E/gemm_counter_addendum_v1/`; no new source audit is claimed here.',
'- **2DCONV:** F256 1.078012x and M8/M16 1.036346x, with unchanged 2,097,152 DRAM reads. F256 reservation-fail events -47.937%; M16 -57.977%. MRQ average is missing. Benefits correlate with reduced visible blocking rather than fewer DRAM requests.',
'- **3DCONV:** M8/M16 1.006512x while reservation-fail events fall 98.807%; F256 regresses to 0.994891x with reservation-fail events +28.782%, MRQ 151 -> 243. Large event reductions translate into only modest cycle savings; the critical-path contribution is unproven.',
'- **particlefilter_naive:** all eight variants exactly 1.0x at 384,601 cycles; 12,960 L2 reads, 2 DRAM reads, zero reservation failures and MRQ 11 are unchanged. This preserves its input and observed flat sensitivity; it does not establish absence of other bottlenecks or its absolute CH/DH advantage.',
'- **F contrast:** convolutionSeparable F256 1.422263x has nearly unchanged DRAM reads (-0.00475%) but reservation-fail events -31.402%; MRQ rises 321 -> 905. scan F256 1.283635x has essentially unchanged DRAM reads (-0.001%) and MRQ 184 -> 628. vectorAdd F256 regresses to 0.919938x despite unchanged DRAM reads and reservation-fail events -51.212%. Event counts are not elapsed latency or unique blocked-cycle attribution.',
'## At most three next directions within existing V3',
'These are evidence rationales for the **already declared policy**, not new proposals, final winners, new grants or overrides of the initial-terminal/full35-parent gates. Every actual configuration must cover all frozen35; never restrict it to the named motivating cases.',
'1. **Entries x FRFCFS:** existing E768_F256 seed. Entries alone are mostly flat while F helps several streaming cases; their combination tests masked concurrency interactions. FRFCFS also changes partition credits. Conditional continuation and saturation/retreat use the existing full35 V3 rules.',
'2. **Merge x sending/scheduling:** existing M8_Q128 and M8_F256 seeds. 2DCONV/3DCONV respond to merge while ATAX/MVT/BICG expose Q/F regressions; combining them tests whether producer/queue constraints conceal OFAT benefits. M8 is the predeclared seed, not selected because of M16 failure. Contextual M16/32 trials require their own full35 parents; original standalone M16 remains incomplete.',
'3. **Entries x miss queue / wide ablation:** existing E768_Q128 plus wide E768_M8_Q128_F256 and declared ablations. Q alone often regresses, which cannot prove a coupled configuration ineffective. Whole35 comparisons of wide and ablated profiles can distinguish marginal resources; retain resource-native qualification, no initial-profile RSS discount for combinations, and no area-equivalence claim.',
'## Evidence and limits',
'Source generator SHA `'+d['source_generator']['sha256']+'`; source report SHA `'+d['source_report_sha256']+'`. `analyze.py` independently recomputes ratios, suite coverage and common intersection and cross-checks source report; it does not rerun scientific qualification. Installed V3 policy SHA `c69b8c3a4a6a11237546d8617a742ebf9e73b918c4b59bde9369377977cc3ed1` is unchanged.',
'Every pair retains the source stream/header binding. L2 whole-declared-trace counters are used only under its declared complete single-stream scope; DRAM is global cumulative. `avg_mrq_latency_last_printed` is not a weighted application average, and `gpu_stall_dramfull` labels ICNT-to-memory blocking rather than DRAM service time. Specific MSHR reasons are missing, not zero. These counters cannot yet prove queue occupancy, memory-level parallelism or latency criticality. No new observation instrumentation was added.']
body=text[0]
for previous,current in zip(text,text[1:]):
 body+=('\n' if previous.startswith('|') and current.startswith('|') else '\n\n')+current
(p/'REPORT.md').write_text(body+'\n',encoding='utf-8')
manifest={'schema':'PARTIAL315_CASES_MANIFEST_V1','source_commit':d['source_commit'],'files':[{'name':x.name,'sha256':hashlib.sha256(x.read_bytes()).hexdigest(),'bytes':x.stat().st_size} for x in sorted(p.iterdir()) if x.is_file() and x.name!='MANIFEST.json']}
(p/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest))
