"""CPU-only operational RSS history: exact closed UUID/full-input identities.

Capture runs outside registry EX and outside candidate/claim admission calls.
Forecast binding reads only that captured immutable snapshot, never registry,
FUSE, raw logs or performance acceptance. No model/spec/guardcap is changed.
"""
from pathlib import Path
import copy,hashlib,json,re,uuid
class HistoryHold(RuntimeError):pass
def need(x,why):
 if not x:raise HistoryHold(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def fullsha(value):return isinstance(value,str)and re.fullmatch('[0-9a-f]{64}',value)is not None

def validate_closed_sample(request,cohort,row,spec,canonical_spec_sha,intent,intent_sha,done,native_exit,allowed_inputs):
 """Pure validation; a real negative can supply RSS, never performance cycles."""
 need(spec['cohort']==cohort and spec['request']==request,'HISTORY_REQUEST_COHORT')
 inp=spec['input_digest'];need(fullsha(inp)and inp in allowed_inputs,'HISTORY_FOREIGN_OR_INVALID_FULL_INPUT_SHA')
 try:canonical_uuid=str(uuid.UUID(row['uuid']))
 except (ValueError,TypeError,AttributeError):raise HistoryHold('HISTORY_INVALID_ORIGINAL_UUID')
 need(canonical_uuid==row['uuid'],'HISTORY_CANONICAL_ORIGINAL_UUID')
 need(canonical_spec_sha==spec['_history_expected_spec_sha'],'HISTORY_CANONICAL_SPEC_PIN')
 need(row['uuid']==intent['uuid']==done['uuid']and intent['cohort']==done['cohort']==cohort,
      'HISTORY_ORIGINAL_UUID_COHORT')
 need(row['intent_sha256']==intent_sha and done==row['execution_receipt']==native_exit,
      'HISTORY_DONE_EXIT_CONSUMED_IDENTITY')
 need(done['new_attempt_consumed']==1 and done['automatic_retry']is False,'HISTORY_ORIGINAL_ONCE_ONLY_IDENTITY')
 value=done.get('peak_observed_rss_bytes')
 if type(value)is not int or value<=0:
  return None,dict(reason='MISSING_OR_NONPOSITIVE_MEASURED_RSS_REJECTED_NOT_ZERO',cohort=cohort,uuid=row['uuid'],input_digest=inp)
 return dict(request=request,cohort=cohort,uuid=row['uuid'],input_digest=inp,peak_RSS_bytes=value,
             source_field='DONE.peak_observed_rss_bytes',performance_acceptance_not_consulted=True),None

def capture(contexts,allowed_inputs):
 """EXTERNAL call sites only; no hidden fallback to a scan during forecast."""
 need(all(fullsha(x)for x in allowed_inputs),'FULL_FROZEN_INPUT_DOMAIN_REQUIRED')
 rows=[];rejected=[];source_contexts=[]
 for ctx in contexts:
  root=Path(ctx['root']);q=ctx['e'].registered()[2] # bounded SH, not registry EX
  need(q['request']==ctx['request'],'HISTORY_EXACT_CONTEXT_REQUEST')
  source_contexts.append(dict(request=q['request'],execution_root=str(root),consumed_UUIDs=len(q['consumed'])))
  for c,row in sorted(q['consumed'].items()):
   if row.get('execution_receipt')is None:continue
   sp=root/'control/specs'/(c+'.json');spec=rd(sp);spec['_history_expected_spec_sha']=q['admitted_specs'][c]
   ip=root/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json');intent=rd(ip);done=rd(dp)
   out=root/'DTC/run/results'/row['uuid'];need(Path(intent['output'])==out,'HISTORY_EXACT_NATIVE_UUID_OUTPUT')
   exitpath=out/'NATIVE_EXIT.json';native=rd(exitpath)
   sample,discard=validate_closed_sample(q['request'],c,row,spec,sha(sp),intent,sha(ip),done,native,allowed_inputs)
   if discard is not None:rejected.append(discard);continue
   sample['provenance']=dict(spec_path=str(sp),spec_sha256=sha(sp),intent_path=str(ip),intent_sha256=sha(ip),
      DONE_path=str(dp),DONE_sha256=sha(dp),NATIVE_EXIT_path=str(exitpath),NATIVE_EXIT_sha256=sha(exitpath),
      consumed_receipt_sha256=digest(row['execution_receipt']))
   rows.append(sample)
 rows.sort(key=lambda x:(x['input_digest'],x['request'],x['cohort'],x['uuid']))
 body=dict(schema='DTC_ORACLE_EXACT_INPUT_CLOSED_RSS_HISTORY_V1',rows=rows,rejected_samples=rejected,source_contexts=source_contexts,
           collection_scope='Outside registry EX, never in candidate/claim forecast',performance_selection_used=False,
           missing_history_is_not_zero=True,spec_guardcaps_modified=False)
 body['snapshot_sha256']=digest(body);return body

def verify_snapshot(snapshot):
 need(snapshot is not None,'HISTORY_NOT_CAPTURED_YET')
 body={k:v for k,v in snapshot.items()if k!='snapshot_sha256'}
 need(snapshot['snapshot_sha256']==digest(body),'HISTORY_SNAPSHOT_MUTATED')
 return snapshot

def bind_forecast(resource,snapshot_provider):
 """Same snapshot for picker, preclaim and postclaim. No IO/authority here."""
 if hasattr(resource,'_exact_RSS_original_forecast'):return
 original=resource.forecast;resource._exact_RSS_original_forecast=original
 def forecast(spec,history=None,policy=None):
  snapshot=verify_snapshot(snapshot_provider());rows=snapshot['rows']
  need(history is None or history is rows,'FORECAST_MUST_USE_SAME_CAPTURED_HISTORY_OBJECT')
  value=original(spec,rows,policy)
  need(type(value)is int and value>=spec['estimated_peak_model_RAM_bytes'],'HISTORY_MUST_NEVER_LOWER_FROZEN_FORECAST')
  return value
 resource.forecast=forecast

def choose(resource,snapshot,pending,sample,claims,**kwargs):
 verify_snapshot(snapshot)
 value=resource.choose_dispatch(pending,sample,claims,history=snapshot['rows'],**kwargs)
 if value is not None:
  spec=next(s for s in pending if s['cohort']==value['cohort'])
  need(value['predicted_peak_RAM_bytes']==resource.forecast(spec,snapshot['rows']),
       'PICKER_AND_ACTUAL_CLAIM_PREDICTION_MUST_MATCH')
  value['RSS_history_snapshot_sha256']=snapshot['snapshot_sha256']
 return value
