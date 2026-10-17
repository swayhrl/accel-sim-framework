import sys,runpy,json,argparse
from pathlib import Path
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1/docs/ep_l2/review_packs/FT20261017_LANE5_LOCAL_PARSER_DEPENDENCY_RECOVERY_r1/deps')
parse=runpy.run_path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1/docs/ep_l2/review_packs/FT20261017_LANE5_CUMULATIVE_TERMINAL_READER_FIX_r1/parse_local_ideal_terminal.py')["parse"]
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();s=json.loads(Path("input_spec.json").read_text());a.out.write_text(json.dumps(parse(a.raw,s),indent=2)+"\n")
