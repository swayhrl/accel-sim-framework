"""One finite controller process; Conv pair accepted before FWT intake. No watcher."""
from pathlib import Path
import json,sys
sys.path.insert(0,"/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e")
import coordinator as c
from controller import step
p=Path(__file__).resolve().parent
receipt=json.loads((p/"RECEIPT.json").read_text());coord=c.Coordinator()
for queue in receipt["queues"]:
 c.require(c.digest(queue["path"])==queue["sha256"],"frozen queue changed")
 result=step(coord,queue["path"])
 c.write_json(p/(queue["workload"]+"_CONTROLLER_RESULT.json"),result)
 pair=coord.snapshot()["accepted_pairs"].get(queue["pair_id"])
 if not pair or pair["status"]!="CURRENT_ACCEPTED":
  print(json.dumps({"status":"AFFECTED_FIRST_PAIR_REVIEW_REQUIRED_NO_FURTHER_DISPATCH","queue":queue,"controller":result}),flush=True)
  break
 print(json.dumps({"status":"PAIR_CURRENT_ACCEPTED_DELIVERED_TO_D","pair":pair}),flush=True)
