from pathlib import Path
import subprocess,json,hashlib,base64,datetime
repo=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-cost-r2-fanout-v3');book=Path('/workspace/ep_l2_rtl_cost_timing_r2');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();pack='docs/ep_l2/review_packs/RTL_COST_TIMING_REFINEMENT_R2_r1';api='repos/swayhrl/accel-sim-framework/'
refs=['hrl/ep-l2-ft20261016-lane2-v1','hrl/ep-l2-rtl-cost-r2','hrl/ep-l2-rtl-cost-r2-fanout-v3']
lines=subprocess.check_output(['git','-c','gc.auto=0','-c','credential.helper=','-c','credential.helper=!gh auth git-credential','ls-remote','https://github.com/swayhrl/accel-sim-framework.git']+['refs/heads/'+r for r in refs],cwd=repo,text=True).splitlines();remote={x.split()[1].removeprefix('refs/heads/'):x.split()[0] for x in lines};assert remote=={r:head for r in refs}
def gh(path):return json.loads(subprocess.check_output(['gh','api',api+path],text=True))
for ref in refs:assert gh('git/ref/heads/'+ref)['object']['sha']==head
local_tree=subprocess.check_output(['git','rev-parse',head+':'+pack],cwd=repo,text=True).strip();tree=gh('git/trees/'+local_tree+'?recursive=1');assert not tree.get('truncated');actual={x['path']:(x['type'],x['sha']) for x in tree['tree'] if x['type']=='blob'}
expected={}
for line in subprocess.check_output(['git','ls-tree','-r',head+':'+pack],cwd=repo,text=True).splitlines():
 info,name=line.split('\t');_,typ,oid=info.split();expected[name]=(typ,oid)
assert actual==expected
paths=[pack+'/'+x for x in ('README.md','RTL_COST_R2_RECEIPT.json','COST_SUMMARY.csv','SHA256SUMS','SIM_RTL_TIMING_DELTA.md') if (repo/(pack+'/'+x)).exists()]+['docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane2/STATUS.md','docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane2/RECEIPT.json','rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv','rtl/ep_l2/rtl/ep_l2_metadata_word.sv','rtl/ep_l2/flow/run_dc.tcl','rtl/ep_l2/flow/run_dc_r2.sh','rtl/ep_l2/flow/common.sdc','rtl/ep_l2/flow/filelist.f']
rows=[]
for p in paths:
 obj=gh('contents/'+p+'?ref='+head);assert obj['encoding']=='base64';data=base64.b64decode(obj['content']);local=(repo/p).read_bytes();assert data==local;rows.append({'path':p,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'remote_git_blob':obj['sha']})
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True)
result={'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'EXACT_THREE_REF_HEADS_PACK_BLOB_TREE_AND_SELECTED_FILE_BYTES_PASS','publication_commit':head,'refs':remote,'review_pack':pack,'review_pack_tree':local_tree,'all_pack_file_blob_identities_matched':len(expected),'readback_bytes':rows,'no_remote_mutation_by_verifier':True}
(book/'REMOTE_VERIFICATION_FINAL.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='readback_bytes'}))
