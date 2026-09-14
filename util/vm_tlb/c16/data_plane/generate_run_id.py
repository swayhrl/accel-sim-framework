#!/usr/bin/env python3
import argparse,json
from pipeline import run_id
a=argparse.ArgumentParser();[a.add_argument(x,required=True) for x in ['--model','--scenario','--phase','--instrument','--target']];x=a.parse_args();print(json.dumps({'run_id':run_id(x.model,x.scenario,x.phase,x.instrument,x.target)}))
