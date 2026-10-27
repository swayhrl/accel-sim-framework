import collections,hashlib,json,math,pathlib
P=pathlib.Path;HERE=P(__file__).resolve().parent
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):P(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
capture=read(HERE/'LATEST_CAPTURE.json');run=P(capture['run_path']);a=read(run/'ANALYSIS.json');r=read(run/'report.json')
pairs=a['all_matched_DH_pairs'];profiles=sorted(a['partial_uniform_DH_statistics']);by={p['input_digest']+'|'+p['profile']:p for p in pairs}
common=sorted(set.intersection(*[{p['input_digest']for p in pairs if p['profile']==profile}for profile in profiles]))
suite_expected=collections.Counter(x['suite']for x in r['programs'].values())
def stat(rows,expected):
 vals=[p['DH_speedup']for p in rows]
 return dict(n=len(vals),expected_n=expected,missing_n=expected-len(vals),GM=math.exp(math.fsum(math.log(v)for v in vals)/len(vals))if vals else None,
  positive=sum(v>1 for v in vals),neutral=sum(v==1 for v in vals),negative=sum(v<1 for v in vals),minimum=min(vals)if vals else None,maximum=max(vals)if vals else None,population=[p['input_digest']for p in rows])
stats={profile:dict(available=stat([p for p in pairs if p['profile']==profile],35),
 common_all8=stat([by[d+'|'+profile]for d in common],len(common)),
 suites={suite:dict(available=stat([p for p in pairs if p['profile']==profile and p['suite']==suite],n),
  common_all8=stat([by[d+'|'+profile]for d in common if r['programs'][d]['suite']==suite],sum(r['programs'][d]['suite']==suite for d in common)))for suite,n in suite_expected.items()})for profile in profiles}
new=a['new_or_newly_matched_pairs']
byfactor={prefix:dict(new_pairs=[p for p in new if p['profile'].startswith(prefix)],
 best_new=max([p for p in new if p['profile'].startswith(prefix)],key=lambda x:x['DH_speedup'],default=None),
 worst_new=min([p for p in new if p['profile'].startswith(prefix)],key=lambda x:x['DH_speedup'],default=None))for prefix in 'EMQF'}
io=read(run/'IO_CHAIN_AUDIT.json');iostat=collections.Counter(x['status']for x in io)
A=HERE.parent.parent.parent
typedACK=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/typed_negative_full35_v2/ACK.json')
cert=A/'engineering_negative_evidence_v1/E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1/1e968456ccefd837eacee605d7ffacc712860114e8a7fea17b4633b25cecbf5f/ENGINEERING_TERMINAL_NEGATIVE.json'
assert sha(cert)=='37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7'
out=dict(schema='DTC_L2_MLP_INCREMENT_V2_SUPPLEMENT',utc=r['utc'],run_path=str(run),suite_expected=dict(suite_expected),common_all8_population=common,
 profile_statistics=stats,factor_new_cases=byfactor,CH_nonP0_accepted_pairs=sum(p['CH_variant_accepted']for p in pairs),
 relative_values_present=sum(p['relative_DTC_improvement']is not None for p in pairs),IO_chain_status_counts=dict(iostat),
 typed_engineering_negative=dict(certificate=str(cert),sha256=sha(cert),state=read(cert)['state'],accepted_cycles=None,performance_accepted=False,
  actual_gate_ACK=str(typedACK),actual_gate_ACK_sha256=sha(typedACK),original_report_state_preserved=True),
 coverage_summary=dict(CH_P0_accepted=sum(x['CH_P0_accepted']for x in a['coverage']),DH_P0_accepted=sum(x['DH_P0_accepted']for x in a['coverage']),
  all8_DH_variants_accepted=sum(len(x['accepted_DH_variants'])==8 for x in a['coverage']),all9_DH_accepted=sum(len(x['accepted_DH_variants'])==8 and x['DH_P0_accepted']for x in a['coverage']),
  full35_profiles=a['full35_profile_count']),all_pairs= len(pairs),new_or_newly_matched=len(new),identity_errors=a['pair_identity_validation_errors'])
put(run/'SUPPLEMENT.json',out);put(HERE/'LATEST_SUPPLEMENT.json',out)
def brief(p):return dict(program=p['program'],profile=p['profile'],speedup=p['DH_speedup'],DRAM_pct=p['counter_changes']['DRAM_read_atoms']['change_pct'])if p else None
print(json.dumps(dict(utc=r['utc'],coverage=out['coverage_summary'],common_n=len(common),IO=dict(iostat),
 stats={p:dict(available_n=v['available']['n'],available_GM=v['available']['GM'],common_GM=v['common_all8']['GM'])for p,v in stats.items()},
 factor_extremes={p:dict(best=brief(v['best_new']),worst=brief(v['worst_new']))for p,v in byfactor.items()},
 new_pairs=[brief(p)for p in sorted(new,key=lambda x:x['DH_speedup'])]),indent=2))
