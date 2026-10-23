import json,sys,pathlib
B=pathlib.Path('/root/data/ep_l2_main_vector_r5_20261023_v1')
sys.path.insert(0,str(B))
import native_dispatch as prior
import vector_runtime as v
def main(args):
 if len(args)>=3 and args[:3]==['result','restore',v.C]:
  if '--project' in args:v.need(args[args.index('--project')+1]=='EP_L2','project mismatch')
  import vector_result
  receipt=v.read(B/'control'/(v.C+'_ARCHIVE_RECEIPT.json'))
  return vector_result.restore(receipt['target_mount_path'],args[args.index('--destination')+1])
 return prior.main(args)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),ensure_ascii=False,indent=2))
 except Exception as e:print(json.dumps({'status':'HOLD','reason':str(e),'automatic_retry':False},ensure_ascii=False),file=sys.stderr);sys.exit(2)
