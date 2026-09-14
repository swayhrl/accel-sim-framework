#!/usr/bin/env python3
import argparse,json
from pipeline import finalize
a=argparse.ArgumentParser();a.add_argument('--staging',required=True);a.add_argument('--ready',required=True);a.add_argument('--manifest',required=True);a.add_argument('--run-id',required=True);x=a.parse_args();d,c=finalize(x.staging,x.ready,x.manifest,x.run_id);print(json.dumps({'ready':str(d),'close':c},sort_keys=True))
