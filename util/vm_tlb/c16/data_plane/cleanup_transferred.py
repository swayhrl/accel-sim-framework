#!/usr/bin/env python3
import argparse,json
from pipeline import cleanup
a=argparse.ArgumentParser();a.add_argument('--root',required=True);x=a.parse_args();print(json.dumps(cleanup(x.root),sort_keys=True))
