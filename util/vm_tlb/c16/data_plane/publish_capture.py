#!/usr/bin/env python3
import argparse,json
from pipeline import publish_argv
a=argparse.ArgumentParser();a.add_argument('--ssh-alias',required=True);a.add_argument('--destination-root',required=True);a.add_argument('--run-id',required=True);a.add_argument('--source',required=True);a.add_argument('--dry-run',action='store_true',required=True);x=a.parse_args();print(json.dumps({'dry_run':True,'remote_mutation':False,'argv':publish_argv(x.ssh_alias,x.destination_root,x.run_id,x.source)}))
