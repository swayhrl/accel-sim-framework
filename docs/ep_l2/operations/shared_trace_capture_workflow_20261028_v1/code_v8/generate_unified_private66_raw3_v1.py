from pathlib import Path
import sys,hashlib,types,argparse,json,resource,os,time
HERE=Path(__file__).parent
def load():
 p=HERE/"unified_metadata_refresh_common_v1.py";b=p.read_bytes()
 manifest=json.loads((HERE/"CODE_MANIFEST.json").read_bytes());r=manifest["files"][p.name];assert len(b)==r["bytes"]and hashlib.sha256(b).hexdigest()==r["sha256"]
 m=types.ModuleType("fixed_private_refresh");m.__file__=str(p);exec(compile(b,str(p),"exec"),m.__dict__);return m
def main():
 resource.setrlimit(resource.RLIMIT_AS,(128*2**20,128*2**20));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,{494});os.nice(15)
 a=argparse.ArgumentParser();a.add_argument("--output-root",required=True);a.add_argument("--selfcheck-only",action="store_true");args=a.parse_args();m=load();out=m.safe_private_output(args.output_root);start=time.monotonic();snapshot,proof=m.collect();blob=m.canonical(snapshot);m.need(len(blob)<=16*2**20,"query compatibility cap");out.mkdir()
 if not args.selfcheck_only:
  snap=m.save_new(out/"PRIVATE_UNIFIED_DISCOVERY66_RAW3_SNAPSHOT_V1.json",snapshot);freeze=m.save_new(out/"SOURCE_FREEZE66_RAW3_V1.json",proof)
 else:snap=dict(bytes=len(blob),sha256=m.h(blob),not_written_selfcheck=True);freeze=None
 result=dict(status="GENERATE_ONLY66_66_RAW3_AND125_METADATA_SELF_CHECK_PASS",selfcheck_only=args.selfcheck_only,output_snapshot_ref=snap,source_freeze_ref=freeze,counts=snapshot["counts"],SM70_exact_values_preserved=True,historical242_states_preserved=True,typed_exact_scopes=8,remaining_deferred=153,no_public_CURRENT_or_tool_write=True,body_bytes_read=0,AS=resource.getrlimit(resource.RLIMIT_AS),peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,elapsed_seconds=time.monotonic()-start)
 m.save_new(out/"GENERATION_RESULT_V1.json",result);print(json.dumps(result))
if __name__=="__main__":main()
