#!/usr/bin/env python3
"""Exact EP leaf route; the shell wrapper delegates every other operation unchanged."""
import sys,json,os
sys.dont_write_bytecode=True
import experiment_runtime as v
def main(args):
 v.need(len(args)>=3 and args[0] in ['experiment','result'] and args[2] in [v.E1,v.E2],'exact EP request required')
 v.need('--project' in args and args[args.index('--project')+1]=='EP_L2','EP project binding required')
 if args[0]=='result':
  v.need(args[1]=='archive','unsupported EP result operation')
  import archive_results
  return archive_results.archive(args[2])
 v.need(args[1] in ['prepare','inspect','status','qualify','register','run-native','accept'],'unsupported EP operation')
 v.bind(args[2]);os.environ['EP_MEMORY_NATIVE_ENTRY']='1'
 return v.main([args[1]])
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),ensure_ascii=False,indent=2))
 except Exception as e:print(json.dumps({'status':'HOLD','reason':str(e),'automatic_retry':False}),file=sys.stderr);sys.exit(2)
