"""Additional parent-release gate: launch entry/exit function-handle identity and source-derived count."""
import argparse,json,pathlib,hashlib
def need(v,m):
 if not v:raise ValueError(m)
def verify(path,expected_count):
 entries={};joins=[]
 for line in path.read_text().splitlines():
  t=line.split('\t')
  if t[0]=='LAUNCH_ENTRY':
   need(len(t)==10 and int(t[1])not in entries,'entry pairing');entries[int(t[1])]=t
  elif t[0]=='LAUNCH_EXIT':
   need(len(t)==10 and int(t[1])in entries,'exit pairing');e=entries.pop(int(t[1]))
   need(e[2:7]==t[2:7],'API/context/stream/function-handle/name changed across launch')
   need(0<int(t[5],16)<2**64,'function handle range');joins.append(dict(ordinal=int(t[1]),api=t[2],context=t[3],stream=t[4],function_handle=t[5],function=t[6]))
 need(not entries and len(joins)==expected_count,'unclosed launch or source-derived count mismatch')
 return joins
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('attempt');p.add_argument('--expected-launch-count',required=True,type=int);p.add_argument('--source-oracle-reference',required=True);a=p.parse_args();R=pathlib.Path(a.attempt);q=json.loads((R/'INPUT_CAPSULE_QUALIFICATION_V4R2.json').read_text())
 need(q['tool_sha256']=='c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352','wrong producer')
 need(a.expected_launch_count>=0 and bool(a.source_oracle_reference),'invalid source oracle')
 journal=R/'traces/ada-lifecycle.tsv';result=dict(status='SOURCE_COUNT_AND_FUNCTION_HANDLE_JOIN_PASS',source_oracle_reference=a.source_oracle_reference,expected_source_launch_count=a.expected_launch_count,joins=verify(journal,a.expected_launch_count),journal_sha256=hashlib.sha256(journal.read_bytes()).hexdigest(),whole_application_coverage='Still requires the independently frozen source/API oracle; self-consistency alone is insufficient')
 with(R/'LAUNCH_FUNCTION_HANDLE_QUALIFICATION.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
