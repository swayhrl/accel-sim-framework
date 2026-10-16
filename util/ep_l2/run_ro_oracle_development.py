#!/usr/bin/env python3
"""Serial full-trace oracle preprocessing; never launches a GPU simulation."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROSTER = {
    "vectorAdd_4M": "decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_4000000",
    "convolutionSeparable": "decoupled-l2-pretraces/cudasdk/9.1/convolutionSeparable/__size_3072",
    "FWT_7_21": "decoupled-l2-pretraces/cudasdk/9.1/fastWalshTransform/_logK_7__logD_21",
    "cfd_097k": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/cfd-rodinia-3.1/__data_fvcorr_domn_097K",
    "sad": "decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sad/_i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin",
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trace-root", type=Path, required=True)
    p.add_argument("--result-root", type=Path, required=True)
    p.add_argument("--workloads", nargs="+", choices=list(ROSTER), default=list(ROSTER))
    args = p.parse_args()
    root = Path(__file__).resolve().parents[2]
    source = subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    for rel in ["util/ep_l2/ro_oracle.py", "util/ep_l2/run_ro_oracle_development.py"]:
        if subprocess.check_output(["git","-C",str(root),"show",source+":"+rel]) != (root/rel).read_bytes():
            raise ValueError("unfrozen source")
    args.result_root.mkdir(parents=True,exist_ok=False)
    statuses = []
    for workload in args.workloads:
        target = args.result_root / workload
        if not (args.trace_root/ROSTER[workload]/"traces/kernelslist.g").is_file():
            statuses.append(dict(workload=workload,status="MISSING_INPUT"));continue
        command = [sys.executable,str(root/"util/ep_l2/ro_oracle.py"),
                   "--commandlist",str(args.trace_root/ROSTER[workload]/"traces/kernelslist.g"),
                   "--output",str(target),"--model-scope","TRACE_MODEL_CLOSED_WORLD",
                   "--framework-source",source]
        print(json.dumps(dict(workload=workload,status="PREPROCESSING",source=source)),flush=True)
        before=time.monotonic()
        with (args.result_root/(workload+".log")).open("w") as log:
            result=subprocess.run(["/usr/bin/time","-v",*command],stdout=log,stderr=subprocess.STDOUT)
        status=dict(workload=workload,framework_source=source,command=command,
                    exit_code=result.returncode,wall_seconds=time.monotonic()-before,
                    status="INPUT_GENERATED" if result.returncode==0 else "FAILED",
                    result_directory=str(target))
        statuses.append(status)
        (args.result_root/"PREPROCESSING_STATUS.json").write_text(json.dumps(statuses,indent=2)+"\n")
        print(json.dumps(status),flush=True)
    if any(s["status"]!="INPUT_GENERATED" for s in statuses):
        sys.exit(1)


if __name__=="__main__":
    main()
