"""Deterministic small Markdown view. Complete source evidence stays lossless."""
import math
PROFILES=('P0','M8','M16','E384','E768','F128','F256','Q64','Q128')
SLOTS=[('CH','P0')]+[('DH',p) for p in PROFILES]
def f(v):return 'MISSING' if v is None else format(v,'.9g')
def esc(v):return str(v).replace('|','/').replace('\n',' ')
def state(row,typed=None):
 if typed and row['cohort'] in typed:return 'NEG_TYPED'
 if row.get('valid'):return 'PASS'
 if row.get('apparent_accepted') or row.get('acceptance_uncertain'):return 'HOLD'
 return 'NEG' if row.get('raw_state')=='FAIL_L2MLP_ARCHIVED_NO_RETRY' else 'WAIT'
def cell_text(row,typed=None):
 o=row['original'];s=row['selected'];a=row.get('alternate')
 if s:
  role='O-ref' if s.get('raw_state')=='REFERENCE_ACCEPTED_NO_NEW_START' else 'O' if s['scientific_role']=='ORIGINAL_PRIMARY_SLOT' else 'IR' if s['scientific_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL' else 'R2'
  return str(s['cycles'])+' '+role+' PASS'+(';O:'+state(o,typed) if s['cohort']!=o['cohort'] else '')
 text='MISSING O:'+state(o,typed)
 if a:text+=';'+('IR' if a['scientific_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL' else 'R2')+':'+state(a)
 return text
def gm(rows):return math.exp(sum(math.log(v) for v in rows)/len(rows)) if rows else None
def render(report):
 value=report['derived35'];orig=report['original350_summary'];named=value['summary'];formal=named['formal_GM_generated'];historical=report.get('historical_fixed3',{'configured':False})
 points={};programs=named['programs'];typed=report['coverage'].get('original_terminal_certificates',{})
 for row in value['rows']:
  key=tuple(row['key'][k] for k in ['input_digest','cell','profile']);assert key not in points;points[key]=row
 assert len(points)==350 and len(programs)==35
 lines=['# Registered-tail results', '', 'Snapshot: '+esc(value['UTC'])+'. Original350 valid '+str(orig['selected_measurement_references'])+'/350; independent named references '+str(named['selected_measurement_references'])+'/350. Registered raw budget 360; runtime display 366. These populations are distinct.', '', 'This readable view preserves every slot and original negative. Complete values, exact populations, SHA/UUID evidence and reasons: `REPORT.json.gz`; all350 rows: `results.csv.gz`. Missing is never zero. Formal metrics: '+str(formal)+'. CH/combination trials are next-stage HOLD and add no scope.', '', 'O PASS = strictly validated original; O-ref PASS = ratified P0 no-new-start reference; IR PASS / R2 PASS = only the fixed named-view alternate. `O:NEG` retains an original failure even when an alternate supplies named-view cycles. WAIT/HOLD/NEG have no accepted cycles. All input rows appear below.', '', '## All35 fixed inputs', '', '<!-- FIXED35_TABLE_START -->','| Program | Suite | Input digest | CH P0 | DH P0 | DH M8 | DH M16 | DH E384 | DH E768 | DH F128 | DH F256 | DH Q64 | DH Q128 |','|---|---|---|---|---|---|---|---|---|---|---|---|---|']
 for digest,p in sorted(programs.items(),key=lambda x:(x[1]['suite'],x[1]['program'],x[0])):
  cells=[cell_text(points[(digest,c,profile)],typed) for c,profile in SLOTS]
  lines.append('| '+' | '.join(map(esc,[p['program'],p['suite'],digest[:16],*cells]))+' |')
 lines+=['<!-- FIXED35_TABLE_END -->','','## Source-role and negative record','','Original failed slots retain their state; this list includes all twelve fixed alternate links, accepted or unavailable. No alternate enters the original ledger.','','| Original cohort | Original state | Alternate cohort / role | Alternate state | Named selection |','|---|---|---|---|---|']
 for row in value['rows']:
  a=row.get('alternate')
  if a:
   s=row['selected'];lines.append('| '+' | '.join(map(esc,[row['original_cohort'],state(row['original'],typed),a['cohort']+' / '+a['scientific_role'],state(a),s['cohort'] if s else 'MISSING']))+' |')
 if typed:lines+=['','Typed negative without fabricated DONE: '+', '.join(c+' certificate '+z['sha256'] for c,z in sorted(typed.items()))+'. The original scan M16 remains negative; R2 is a separate named reference.']
 lines+=['','','## Available and common population metrics','','DH speedup = own DH P0 / profile cycles. Each common row uses the same inputs across all nine profiles within its labelled view. These are partial populations, not full-suite winners. CH speedup and relative-DTC improvement remain missing where a non-P0 CH measurement is unavailable.','','| View | Profile | DH available n/35; GM | DH all-profile common n/35; GM | CH speedup available n/35; GM | Relative DTC available n/35; GM |','|---|---|---|---|---|---|']
 for label,summary in [('Original350',orig),('Named35',named)]:
  for profile in PROFILES:
   metrics=summary['aggregates'][profile]['ALL'];dh=metrics['DH_speedup'];ch=metrics['CH_speedup']['available'];rel=metrics['relative_DTC_improvement']['available'];a=dh['available'];c=dh['all_profile_common']
   lines.append('| '+' | '.join([label,profile,str(a['n'])+'/35; '+f(a['GM']),str(c['n'])+'/35; '+f(c['GM']),str(ch['n'])+'/35; '+f(ch['GM']),str(rel['n'])+'/35; '+f(rel['GM'])])+' |')
 lines+=['','','## Matched inputs across both views and every profile','','For each suite, both columns use exactly the intersection with a lawful DH-speedup pair in all nine profiles in both views. Suite totals retain all frozen inputs; missing rows are excluded, never imputed. Full digest populations remain in REPORT.json.gz.','','| Suite | Profile | Matched n / suite total | Original DH GM | Named DH GM |','|---|---|---|---|---|']
 if formal:
  suites=['ALL']+sorted({p['suite'] for p in programs.values()})
  for suite in suites:
   ids=[d for d,p in programs.items() if suite=='ALL' or p['suite']==suite]
   common=[d for d in ids if all(summary['per_input'][d][profile]['DH_speedup'] is not None for summary in [orig,named] for profile in PROFILES)]
   for profile in PROFILES:
    vals=[[summary['per_input'][d][profile]['DH_speedup']['value'] for d in common] for summary in [orig,named]]
    lines.append('| '+' | '.join([esc(suite),profile,str(len(common))+'/'+str(len(ids)),f(gm(vals[0])),f(gm(vals[1]))])+' |')
 else:lines.append('| NOT_RELEASED | MISSING | MISSING | MISSING | MISSING |')
 lines+=['','','## Historical fixed3: separate scope','','No historical EP measurement enters DTC populations or GMs. Overall authorized completion requires DTC plus these fixed3 only when configured. Historical configured: '+str(historical.get('configured',False))+'.','','| Program / mode | UUID | Strict/status | Accepted cycles | Own baseline UUID | cycles / own baseline | own baseline / cycles |','|---|---|---|---|---|---|---|']
 for row in historical.get('objects',[]):
  base=row.get('baseline_comparison',{});lines.append('| '+' | '.join(map(esc,[row['program']+' / '+row['mode'],row['uuid'],row['status'],row['cycles'] if row['accepted'] else 'MISSING',base.get('baseline_uuid','MISSING'),f(base.get('cycles_over_baseline')),f(base.get('baseline_cycles_over_cycles'))]))+' |')
 if not historical.get('configured'):lines.append('| NOT_CONFIGURED | MISSING | outside authorized scope | MISSING | MISSING | MISSING | MISSING |')
 lines+=['','','## Historical downstream18: own P0 = 1','','Immutable baseline only, separate from DTC350 and the three live EP objects. Values use each input/design own strictly accepted P0.','','| Program | Design | Profile | Cycles | Strict accepted | cycles / own P0 | own P0 / cycles |','|---|---|---|---|---|---|---|']
 for row in historical.get('downstream18',{}).get('P0_equals_1_table',[]):
  accepted=row['performance_accepted'];lines.append('| '+' | '.join(map(esc,[row['program'],row['cell'],row['profile'],row['cycles'] if accepted else 'MISSING',accepted,f(row.get('cycles_over_own_P0')),f(row.get('speedup_own_P0_over_cycles'))]))+' |')
 lines+=['','','DTC registered completion: '+str(report['coverage'].get('registered_tail_complete'))+'; historical fixed3 completion: '+str(report['coverage'].get('historical_fixed3_complete'))+'; all authorized populations complete: '+str(report['coverage'].get('all_authorized_populations_complete'))+'. This does not claim completion of unregistered CH/combination research.','']
 return '\n'.join(lines).encode('utf-8')
