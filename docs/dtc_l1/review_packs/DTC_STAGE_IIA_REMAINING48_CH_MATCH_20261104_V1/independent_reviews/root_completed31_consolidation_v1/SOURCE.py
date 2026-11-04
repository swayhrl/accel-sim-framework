"""Consolidate an independently audited, explicitly incomplete CORE31 snapshot."""
from pathlib import Path
import gzip,hashlib,json,datetime
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
S=A/'root_independent_cycle_statistics_v1/20261104T071015468833Z'
WANT='60f89782895950134e3946333dbf78dd9fed3d102c131cb5db64435ae80c71bd'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S/'MANIFEST.json')==WANT
for member in json.loads((S/'MANIFEST.json').read_bytes())['files']:
 p=S/member['path'];assert p.stat().st_size==member['bytes']and sha(p)==member['sha256']
v=json.loads(gzip.decompress((S/'AUDIT.json.gz').read_bytes()))
assert v['status']=='PASS'and v['accepted_slots_rechecked']==190 and v['new48_raw_cycle_endpoints_rechecked']==46 and v['common_both_F_n']==31 and not v['final_full32']
rows=v['all_programs'];pending=[r for r in rows if not r['common']]
assert len(rows)==32 and len(pending)==1 and pending[0]['program']=='GESUMMV'
core=v['statistics']['CORE32'];summary=v['source_provider']['summary']
assert summary['accepted_CH']==46 and summary['await_result']==2 and summary['verification_hold']==summary['archived_negative_CH']==0
def val(x):return '—'if x is None else f'{x:.9f}'if isinstance(x,float)else str(x)
def table(headers,body):
 return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(val(x)for x in row)+' |'for row in body])
gm=[];signs=[];suite=[];direct=[]
for f in ['F128','F256']:
 d=core['common'][f];gm.append([f,31]+[d[k]['GM']for k in ['S_CH','S_DH','R_P0','R','I']])
 for k in ['S_CH','S_DH','R','I']:
  x=d[k];signs.append([f,k,x['positive'],x['zero'],x['negative'],x['minimum'],x['median'],x['maximum']])
for name,entry in sorted(v['statistics'].items()):
 if name=='CORE32':continue
 for f in ['F128','F256']:
  d=entry['common'][f];suite.append([name,entry['common_n'],entry['expected_n'],f]+[d[k]['GM']for k in ['S_CH','S_DH','R','I']])
for name,d in core['direct'].items():direct.append([name,d['n'],d['GM'],d['positive'],d['zero'],d['negative'],d['minimum'],d['median'],d['maximum']])
cycle_rows=[]
for r in sorted(rows,key=lambda r:(r['suite'],r['program'])):
 c=r['cycles'];rat=r['exact_ratios'];cycle_rows.append([r['program'],r['input_digest']]+[c.get(k)for k in ['CH_P0','CH_F128','CH_F256','DH_P0','DH_F128','DH_F256']]+[None if f not in rat else rat[f]['I']['value']for f in ['F128','F256']]+[r['common']])
body=['# Completed31 / fixed CORE32 scientific review: GES pending','',
f"Frozen source observation: {summary['observed_utc']}. **46/48 new CH identities accepted;2 awaiting GESUMMV-F128/F256;0 archived simulation negatives;0 verification HOLD.** The exact same31 accepted six-cell inputs are used for both F profiles. All32 frozen identities remain in the table. This is an incomplete completed-subset report, not final32/35/42 coverage, and completion order is not a selection criterion.",'',
'All48 one-use science identities were already consumed. Original128 reference slots, first16CH slots and new48 slots retain independent provenance. Six P0 wrappers preserve their underlying accepted identity. No repaired/IR/R2/EP/PQPS source is substituted. Frozen EnglishLaTeXv0.23 and all historical matrices remain unchanged.','',
'## Matched performance','',
'S_CH=CH0/CHF; S_DH=DH0/DHF; R0=CH0/DH0; R=CHF/DHF; I=S_DH/S_CH=R/R0. R>1 describes absolute DH advantage; I>1 describes incremental relative improvement from P0. The Hash family is fixed: these F comparisons concern FR/shared-credit changes and do not newly isolate Hash gains. No program-specific bestF GM is formed.','',
table(['F','Same common n/32','GM S_CH','GM S_DH','GM R0','GM CH/DH','GM I'],gm),'',
'Counts below use exact integer/Fraction signs; rounded1.000000 values do not establish exact zero. A performance regression is retained accepted data, distinct from an archived failed simulation.','',
table(['F','Metric','Positive','Exact zero','Regression','Min','Median','Max'],signs),'',
'## Suite coverage on the same common set','',
table(['Suite','Common n','Fixed n','F','GM S_CH','GM S_DH','GM CH/DH','GM I'],suite),'',
'## DirectF comparison','',
'CH128/CH256 and DH128/DH256 above1 mean F256 is faster. R256/R128 above1 means the same-set absolute DH/CH ratio is larger atF256. All rows use the same31 accepted inputs.','',
table(['Metric','n','GM','Positive','Exact zero','Regression','Min','Median','Max'],direct),'',
'## All32 frozen input identities and source cycles','',
table(['Program','Full input SHA','CH0','CH128','CH256','DH0','DH128','DH256','I128','I256','BothF complete'],cycle_rows),'',
'## New closed controls and evidence levels','',
'3MM has CH4191465/DH2402871 at all three settings;myocyte has CH145909578/DH145147976;srad has CH8043823/DH7324411. Every actual kernel and selected additive interval has exact zero within-design F response in these inputs. Their absolute CH/DH differences are distinct architecture comparisons under the same Hash family. All earlier positive, zero and negative cases remain included: scalarProd has opposite small CH/DH changes;MRI-Q retains its negativeK3;histo retains negative phases;3DCONV retains both DH regressions;vectorAdd,ATAX,MVT,BICG and particlefilter_float retain their previously reviewed limitations and absolute negatives.','',
'3MM issues zero timed DRAM read/write commands in this prefilled replay. myocyte issues exactly one32B read atom atK1;srad issues13 read atoms inK3/K5/K6. These exposures do not establish compute-bound execution. All-type L2 write misses are not DRAM reads; GLOBAL accepted sectors are32B units; request objects and ICNT blocked-admission events have different meanings. CH common and DH OO counters do not describe equal structures. Missing positive-only reason counters and latency means stay unavailable. Means, gauges and running peaks are not differenced. No live progress preview contributes a cycle, performance ratio, application fraction or ETA.','',
'The myocyte compact6-source evidence contains35958 kernel records.5993=13x461 is arithmetic compatibility with candidate13-RHS logic, not a measured461 solver-attempt count,100ODE steps or full-application certification. Accepted-step/retry IDs and phase_epoch-to-ordinal mappings remain unbound. Its repeated CPU state/parameter HtoD operations require a numerical-coherence boundary: actual simulator hit/new-miss counters do not certify correct reuse of CPU-updated values.','',
'The independent fixed9eed source review binds the effective flush_l1=1,flush_l2=0,prefill=1,invalidate_on_source_event=0 and specific idle invalidation/memcpy callsites. At the reviewed invalidate entry, flag0 takes the ordinary m_L1D invalidation path; the reviewed memcpy path fills L2. This does not exhaust every OO reset path or prove a stale-data bug. Downstream matching alone is not numerical-coherence certification. Candidate source/ELF/y/params binding and runtime OO upload coherence are separate unresolved questions.','',
'3MM candidate source S copies uninitialized E/F/G and uses +=; its binding to historical capture source/ELF/macros and numerical correctness remains unproved. Nominal E=A*B/F=C*D/G=E*F phase labels do not newly certify values. The registered srad502-kernel ROI has seven exact selectors, including distinct450CTA and1CTA reduce phases sharing a symbol. Its extract phase retains a22cycle absolute DH regression. None of these limitations permits repairing or replacing frozen inputs, dropping rows, changing historical acceptance or promoting full-application correctness.','',
'## Hardware, resources and next-step boundary','',
'Core9eedb3131937748f0492fa83aad37d3691118d70,Framework02775fd795cde5aae1480d81cee6eb481d0a08f4,binary02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d,850MHz DRAM and10MiB L2 stay fixed. FR64/128/256 couples to shared credits255/319/447. Across20 controllers F128/F256 add1280/3840 request slots; credits are not another separately counted data buffer.','',
'CH has96KiB ordinary L1/commonPIB256. DH has512 searchable logical Tags,640x128B physical identities,activeOO PIB128 and finite completion service. Its16KiB compatibility cache retains eligible fallback routes.80+16KiB is not a unified effective96KiB cache or equal area. Metadata,ports,wiring,coherence implementation,area,frequency and energy costs remain unquantified. Host RSS/elapsed/storage observations are separate from simulated hardware cost. The public40-point resource snapshot retains its own date; it is not46-point resource coverage.','',
'The recommended next work is conditional: first read-only source/ELF and invalidation-path/coherence qualification; then existing counter/phase attribution; only after full32 evidence and explicit new authorization consider uniform M8xF,Tag/pool/activePIB/finite-service experiments or new observational probes. Any numerical/native GPU validation,new instrumentation or simulation needs its own authorization. No such action starts here.','',
'## Provenance and remaining closure','',
f"Root audit `{S}/MANIFEST.json`,SHA`{WANT}`,independently rechecks190 accepted RESULT identities,46 new raw terminal-cycle endpoints,exact signs,suite/common/available distributions,directF and effective-option differences. It does not reopen144 inherited raw lifecycles or replace the final full48 archive/recovery audit.",'',
'B/C closed supplements:3MM ad4898379cf92922f72026f5b507a9d6e3b47584dc64c9edde756dbfdc71ec4a /4d1b892eea5a3af681f1d26535d9fa77917ddd7cccf3016e923cd8b38d5c0251;myocyte77ba3712318a44e4061997fa564d0f6bcd78196eca04da3c528241616ae82db3 /e060ab9d4e89cadf40b2172a98e0adead5b6c17f72d777475c493b12f211aa64;srad ee24d41079833803fa033c2df67f5475c6e4b7f6c582ab48a8d7c2567e256606 /b035a78eb92ebffcf0620969dfa466d4784f836f3950b2884ed4f2ac294e993f. Packet directories and individual witnesses remain in the Git review package. myocyte invalidation facts72587e571dfde4f1b834f4cce48176205ec1d4e0ce64dd79ea78d26520fa5697 are source facts with explicit scope, not a new model experiment.','',
'GESUMMV-F128/F256 remain missing in this snapshot. The original final CPU waiter still waits for all48 legal terminal outcomes and runs its frozen C/B/Root/render chain once. Final48 lifecycle/true164/native restore audit,final32 statistics/narrative,final48 measured-resource consumption,independent end review,visual approval,immutable final Git/SHA readback and requirement-by-requirement completion audit remain pending. This report does not complete the Goal or release any further experiment.','']
out=A/'root_completed31_consolidation_v1';assert not out.exists();out.mkdir()
(out/'REPORT.md').write_text('\n'.join(body))
data=dict(schema='DTC_COMPLETED31_INTERIM_CONSOLIDATION_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_audit_manifest=str(S/'MANIFEST.json'),source_audit_manifest_sha256=WANT,summary=summary,statistics=v['statistics'],all_programs=rows,final_core32_claim=False,uniform_F_selected=False,new_models=0,native_writes=0)
(out/'CONSOLIDATION.json.gz').write_bytes(gzip.compress((json.dumps(data,indent=2)+'\n').encode(),mtime=0));(out/'SOURCE.py').write_bytes(Path(__file__).read_bytes())
(out/'MANIFEST.json').write_text(json.dumps(dict(schema='DTC_COMPLETED31_CONSOLIDATION_MANIFEST_V1',files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p))for p in sorted(out.iterdir())],new_models=0,native_writes=0),indent=2)+'\n')
print(json.dumps(dict(output=str(out),manifest_sha256=sha(out/'MANIFEST.json'),GM_rows=gm,final32=False)))
