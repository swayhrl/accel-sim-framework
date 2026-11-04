from pathlib import Path
import sys,json,gzip,hashlib,re,csv,io,math,subprocess,datetime
from fractions import Fraction
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
B=A/'agents/B_closed_samples_analysis_v1/updates/scalarProd_F256_v1'; O=A/'agents/C_scalarProd_F256_mechanism_review_v1'
assert not O.exists(), 'new independent directory required'
sha=lambda b:hashlib.sha256(b).hexdigest(); J=lambda p:json.loads(Path(p).read_bytes()); checks=[]; sources=[]
def ck(n,v,detail=None):
 assert v,n
 checks.append({'check':n,'pass':True,**({'detail':detail}if detail is not None else{})})
def close(a,b):return math.isclose(a,b,rel_tol=2e-13,abs_tol=1e-10)
m=J(B/'MANIFEST.json');ck('frozen_B_manifest',sha((B/'MANIFEST.json').read_bytes())=='854e5b81d7451c1a5b390de1eadf5e64e393211d2edd96a02d847afa0dd21ab4')
for f in m['files']:
 b=(B/f['path']).read_bytes();ck('member:'+f['path'],sha(b)==f['sha256']and len(b)==f['bytes'])
rows=json.loads(gzip.decompress((B/'CLOSED_SOURCE_KERNEL_COUNTERS.json.gz').read_bytes()))['rows'];qs=J(B/'RAW_QUEUE_AND_LATENCY_HISTOGRAM.json');perfs=J(B/'EXISTING_WITHIN_KERNEL_OBSERVABILITY.json');computed=[]
ck('exact_four_closed_population',len(rows)==4 and{(r['cell'],r['profile'])for r in rows}=={(c,p)for c in ['CH','DH']for p in ['P0','F256']})
for r in rows:
 label=r['cell']+'-'+r['profile']; rb=Path(r['RESULT_path']).read_bytes(); result=json.loads(rb); exitb=Path(r['native_exit_path']).read_bytes(); ex=json.loads(exitb)
 ck(label+':RESULT_EXIT_binding',sha(rb)==r['RESULT_sha256']and sha(exitb)==r['native_exit_sha256']and result['uuid']==r['uuid']and result['cycles']==r['cycles']and result['proof']['cycles']==r['cycles'])
 ck(label+':accepted_natural_no_retry',result['state'] in {'PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE','PASS_STAGEII48_CH_STRICT_ARCHIVE_NATIVE_RESTORE'}and ex['launcher_wait_returncode']==0 and not ex['automatic_retry']and ex['native_simulator_observed'],{'state':result['state']})
 ck(label+':fixed_scientific_identity',r['input_digest']=='2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954'and r['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70'and r['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'and r['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'and sha(Path(r['input_binding_path']).read_bytes())==r['input_binding_sha256'])
 compressed=Path(r['raw_gzip_path']).read_bytes(); rawb=gzip.decompress(compressed);raw=rawb.decode();ck(label+':full_closed_raw_sha',sha(compressed)==r['raw_gzip_sha256']and sha(rawb)==r['raw_plain_sha256']and ex['raw_uncompressed_sha256']==sha(rawb))
 ck(label+':one_actual_kernel_ROI',re.findall(r'^kernel_name = (\S+)',raw,re.M)==['_Z13scalarProdGPUPfS_S_ii']and[int(x)for x in re.findall(r'^gpu_sim_cycle = (\d+)',raw,re.M)]==[r['cycles']]and[int(x)for x in re.findall(r'^gpu_sim_insn = (\d+)',raw,re.M)]==[730610912]and[int(x)for x in re.findall(r'^gpu_tot_issued_cta = (\d+)',raw,re.M)]==[128])
 q=next(q for q in qs if(q['cell'],q['profile'])==(r['cell'],r['profile'])); blocks=re.split(r'^Memory Partition (\d+):[ \t]*$',raw,flags=re.M); ctr=[];ck(label+':20controllers',len(blocks)==41)
 for i in range(1,len(blocks),2):
  cid=int(blocks[i]);block=blocks[i+1]; bq=q['controller_rows'][cid];line=re.search(r'^n_cmd=[^\r\n]+',block,re.M)[0];n={k:int(v)for k,v in re.findall(r'\b(n_cmd|n_act|n_pre|n_req|n_rd|n_rd_L2_A|n_write|n_wr_bk)=(\d+)',line)};avg=float(re.search(r'^queue_avg = (\S+)',block,re.M)[1]);peak=int(re.search(r'^mrqq: max=(\d+)',block,re.M)[1]);banks={k:{'read_command_count':int(a),'idle_cycle_count':int(z)}for k,a,z in re.findall(r'bk(\d+): (\d+)a (\d+)i',block)};miss=list(map(int,re.findall(r'^Miss queue \((\d+) entries\):',block,re.M)));lat=int(re.search(r'^In Dram Latency Queue \(total = (\d+)\):',block,re.M)[1]);
  ck(label+':controller'+str(cid)+':all_explicit_fields',bq['controller']==cid and n==bq['cumulative']and avg==bq['FRFCFS_pending_queue_mean_printed']and peak==bq['FRFCFS_pending_queue_peak_after_scheduler']and banks==bq['bank_read_commands']and miss==bq['terminal_L2_miss_queue_entries']and lat==bq['terminal_DRAM_latency_queue_entries'])
  ck(label+':controller'+str(cid)+':conservation_and_scope',len(banks)==16 and sum(x['read_command_count']for x in banks.values())==n['n_rd']+n['n_rd_L2_A']and sum(x['read_command_count']>0 for x in banks.values())==4 and miss==[0,0]and lat==0 and 0<=avg<=peak<=(64 if r['profile']=='P0'else 256)and peak*n['n_cmd']<2**32)
  ctr.append((n,avg,peak))
 reads=sum(n['n_rd']+n['n_rd_L2_A']for n,_,_ in ctr);writes=sum(n['n_write']+n['n_wr_bk']for n,_,_ in ctr);nr=sum(n['n_req']for n,_,_ in ctr);avg=sum(Fraction(str(v))*n['n_cmd']for n,v,_ in ctr)/sum(n['n_cmd']for n,_,_ in ctr)
 ck(label+':read_atoms_and_requests',reads==3563520==r['totals']['DRAM_read_atoms32B']and writes==r['totals']['DRAM_write_atoms32B']and nr==r['totals']['DRAM_controller_n_req']and len({n['n_rd']+n['n_rd_L2_A']for n,_,_ in ctr})==1)
 ck(label+':aggregate_printed_mean',close(float(avg),q['aggregate']['pooled_queue_pending_mean_per_controller_per_DRAM_tick_from_printed_floats']))
 hist=list(map(int,re.search(r'^mrq_lat_table:([^\r\n]*)',raw,re.M)[1].split()));hq=q['MRQ_latency_histogram'];ck(label+':all_32_bins_and_population',len(hist)==32 and hist==hq['bins']and sum(hist)==nr==hq['n']);maxmrq=int(re.search(r'^maxmrqlatency\s*=\s*(\d+)',raw,re.M)[1]);bounds=[Fraction(sum(v*(0 if j==0 else 2**j)for j,v in enumerate(hist)),nr),Fraction(sum(v*min(2**(j+1)-1,maxmrq)for j,v in enumerate(hist)),nr)]
 ck(label+':hist_mean_bounds',all(close(float(a),b)for a,b in zip(bounds,hq['derived_mean_core_cycle_bounds']))and hq['mean_is_bounded_not_exact'])
 for name,frac in [('median_bounds',Fraction(1,2)),('p99_bounds',Fraction(99,100)),('p999_bounds',Fraction(999,1000))]:
  target=(nr*frac.numerator+frac.denominator-1)//frac.denominator;c=0
  for j,v in enumerate(hist):
   c+=v
   if c>=target:break
  ck(label+':'+name,hq[name]=={'bucket':j,'core_cycle_bounds':[0 if j==0 else 2**j,min(2**(j+1)-1,maxmrq)],'rank':target,'n_requests':nr})
 ck(label+':tails',close(sum(hist[9:])/nr,hq['fraction_ge_512_core_cycles'])and close(sum(hist[10:])/nr,hq['fraction_ge_1024_core_cycles']))
 ck(label+':unprinted_latency_means_remain_missing',q['strict_mean_latencies']=={}and r['strict_latency_diagnostic_only']=={}and not re.search(r'^\s*(?:averagemflatency|averagemrqlatency|avg_mrq_lat|avg_icnt2mem_latency|avg_icnt2sh_latency)\s*=',raw,re.M))
 for key,value in r['totals'].items():
  if key.startswith(('DRAM_','L2_GLOBAL_')):continue
  found=re.findall(r'^\s*'+re.escape(key)+r'\s*=\s*(\d+)\s*$',raw,re.M);ck(label+':literal_counter:'+key,bool(found)and int(found[-1])==value)
 k=r['kernels'][0];ck(label+':single_kernel_cumulative_is_interval',k['selected_cumulative']==k['print_interval_additive']and k['selected_cumulative']==r['totals'])
 for reason,value in k['positive_only_retry_reasons'].items():
  found=re.findall(re.escape(reason.split(':')[0]+'['+reason.split(':')[1]+']['+reason.split(':')[2]+']')+r'\s*=\s*(\d+)',raw);ck(label+':explicit_reason:'+reason,bool(found)and int(found[-1])==value)
 p=next(x for x in perfs if(x['cell'],x['profile'])==(r['cell'],r['profile']));ck(label+':one_closed_perf_file',len(p['closed_perf_files'])==1)
 for pf in p['closed_perf_files']:
  z=Path(pf['path']).read_bytes();data=list(csv.DictReader(io.StringIO(gzip.decompress(z).decode())));projection={k:data[0][k]for k in pf['cycle_instruction_columns']};ck(label+':terminal_perf_not_phases',sha(z)==pf['sha256']and len(data)==1==pf['complete_data_rows']and projection==pf['first_data_projection']==pf['last_data_projection']and int(projection['gpu_sim_cycle'])+int(projection['gpu_tot_sim_cycle'])==r['cycles'])
 computed.append({'cell':r['cell'],'profile':r['profile'],'cycles':r['cycles'],'uuid':r['uuid'],'RESULT_sha256':r['RESULT_sha256'],'raw_plain_sha256':sha(rawb),'queue_mean_from_rounded_printed_means':float(avg),'read_atoms32B':reads,'write_atoms32B':writes,'request_objects':nr,'hist_mean_bounds':[float(x)for x in bounds],'hist_tail_ge512':sum(hist[9:])/nr,'hist_tail_ge1024':sum(hist[10:])/nr})
 sources.append({k:r[k]for k in ['cell','profile','RESULT_path','RESULT_sha256','raw_gzip_path','raw_gzip_sha256','raw_plain_sha256','native_exit_path','native_exit_sha256']})
for cell in ['CH','DH']:
 a=next(r for r in rows if(r['cell'],r['profile'])==(cell,'P0'))['effective_options'];z=next(r for r in rows if(r['cell'],r['profile'])==(cell,'F256'))['effective_options'];diff={k:[a.get(k),z.get(k)]for k in set(a)|set(z)if a.get(k)!=z.get(k)};ck(cell+':only_F_option_changes',diff=={'-gpgpu_frfcfs_dram_sched_queue_size':[['64'],['256']]})
cycles={(r['cell'],r['profile']):r['cycles']for r in rows};sch=Fraction(cycles['CH','P0'],cycles['CH','F256']);sdh=Fraction(cycles['DH','P0'],cycles['DH','F256']);rf=Fraction(cycles['CH','F256'],cycles['DH','F256']);r0=Fraction(cycles['CH','P0'],cycles['DH','P0']);improve=sdh/sch;claimed=J(B/'MATCHED_COMPARISONS.json')[0]
ck('exact_integer_metrics',all(close(float(v),claimed['metrics'][k])for k,v in {'S_CH':sch,'S_DH':sdh,'R':rf,'I':improve}.items())and rf/r0==improve)
ck('preserved_negative_positive',cycles['CH','F256']-cycles['CH','P0']==1535 and cycles['DH','F256']-cycles['DH','P0']==-1828 and sch<1<sdh and improve>1)
fixed=J(B/'QUEUE_LATENCY_FIXED_SOURCE_SEMANTICS.json')
for s in fixed:
 b=Path(s['path']).read_bytes();rel=str(Path(s['path']).relative_to('/root/data/dtc_failure_repair_20261025_v1/core'));gitb=subprocess.check_output(['git','-c','safe.directory=/root/data/dtc_failure_repair_20261025_v1/core','-C','/root/data/dtc_failure_repair_20261025_v1/core','show',s['commit']+':'+rel]);ck('fixed_source:'+rel,sha(b)==s['sha256']and b==gitb);ls=b.decode().splitlines()
 for e in s['excerpts']:ck('exact_source_excerpt:'+rel+':'+str(e['start']),e['text']=='\n'.join(str(i+1)+': '+ls[i]for i in range(e['start']-1,e['end'])))
report=(B/'REPORT.md').read_text();ck('report_explicit_scope_and_causality_limits',all(x in report.lower()for x in ['not','core','dram','histogram'])and not m['F128_comparison_performed']and m['closed_sources']==4)
# No execution or consumer imports. Only new C directory is created after all assertions.
O.mkdir(parents=True)
def write(name,d):(O/name).write_text(json.dumps(d,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
write('REVIEW.json',{'schema':'DTC_SCALARPROD_F256_INDEPENDENT_NARROW_REVIEW_V1','created_utc':now,'status':'PASS','reviewed_B_manifest_sha256':sha((B/'MANIFEST.json').read_bytes()),'scope':'Four closed scalarProd sources, P0/F256 only. Interim mechanism review; not all48 terminal review or execution authorization.','checks':checks,'check_count':len(checks),'independent_recomputed_rows':computed,'exact_ratios':{k:{'numerator':v.numerator,'denominator':v.denominator,'float':float(v)}for k,v in {'S_CH':sch,'S_DH':sdh,'R_P0':r0,'R_F256':rf,'I':improve}.items()},'limits':['FR-FCFS pending mean is sampled after scheduling per DRAM tick; excludes active bank service. Printed controller means are rounded.','MRQ histogram measures request construction to bank assignment in global core cycles, not full L2-to-DRAM service or critical-path time. Request objects differ from 32B atoms.','Histogram gives quantile buckets and overlapping mean bounds, not exact latency means. Unprinted means remain missing.','Bank RD counters show four nonzero-read banks per controller, not proof of zero write activity or a bank bottleneck.','One terminal performance row per one-kernel run supplies no within-kernel phase timeline.','Candidate scalarProd source explains vector/element parameters but capture ELF and numerical bytes are not certified. Frozen input identity is preserved.','F256 also increases shared credits from255 to447; no pure isolated queue-capacity claim.','CH active commonPIB256 and DH activeOO128 remain distinct frontends; generic DH PIB8 is not active OO capacity.','Read-active is not a cold/compulsory-miss classification under memcpy prefill.','This narrow review rehashes closed RESULT/EXIT/raw/input evidence and counters; it does not repeat the prior full typed archive restoration audit.'],'new_models':0,'live_raw_read':False,'registration_owner_history_mutations':0,'science_or_paper_changes':0})
write('SOURCE_REFERENCES.json',{'closed_sources':sources,'fixed_source_semantics_sha256':sha((B/'QUEUE_LATENCY_FIXED_SOURCE_SEMANTICS.json').read_bytes()),'B_report_sha256':sha((B/'REPORT.md').read_bytes()),'B_package_path':str(B)})
(O/'README.md').write_text('''Independent scalarProd F256 narrow review: PASS.

Four closed sources only: CH/DH × P0/F256. The four complete raw files, RESULT and natural-exit identities, frozen input/build references, all 80 controller records, all 128 explicit histogram bins, terminal performance rows and fixed Core excerpts were independently checked. No live raw, model, registration, owner or Git operation was used.

CH regresses by 1,535 cycles; DH improves by 1,828 cycles. The relative improvement I≈1.008134 is arithmetic on these two changes. The 3,563,520 read atoms remain unchanged. Reduced admission/retry counts do not establish a critical-path cause; the larger MRQ tail and queue pending mean coexist with DH improvement. Means not printed stay missing, histogram means are bounds, and four nonzero bank RD fields do not prove a bank bottleneck.

Only one terminal perf row exists per one-kernel run. The candidate source's vector loop is not measured sub-kernel segmentation or capture-ELF certification. F128 was pending in the frozen snapshot and is not consumed here. This is neither full48 final review nor execution approval. Prior original packages, histories and v0.23 remain unchanged.
''')
Path(O/'audit_scalarprod_readonly.py').write_bytes(Path(__file__).read_bytes())
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file():b=p.read_bytes();files.append({'path':str(p.relative_to(O)),'bytes':len(b),'sha256':sha(b)})
write('MANIFEST.json',{'schema':'DTC_INDEPENDENT_SCALARPROD_F256_REVIEW_MANIFEST_V1','created_utc':now,'files':files,'status':'PASS','checks':len(checks),'closed_sources':4,'not_all48_final':True})
print(json.dumps({'status':'PASS','checks':len(checks),'path':str(O),'manifest_sha256':sha((O/'MANIFEST.json').read_bytes()),'review_sha256':sha((O/'REVIEW.json').read_bytes())}))


