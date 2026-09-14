#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from pipeline import validate_ack,transition
a=argparse.ArgumentParser();a.add_argument('--ack',required=True);a.add_argument('--run-id',required=True);a.add_argument('--manifest-sha',required=True);a.add_argument('--destination',required=True);a.add_argument('--file-count',type=int,required=True);a.add_argument('--total-bytes',type=int,required=True);a.add_argument('--ready',required=True);a.add_argument('--transferred',required=True);x=a.parse_args();validate_ack(json.loads(Path(x.ack).read_text()),x.run_id,x.manifest_sha,x.destination,x.file_count,x.total_bytes);print(json.dumps({'transferred':str(transition(x.ready,x.transferred,x.run_id))}))
