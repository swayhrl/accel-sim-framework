"""Sole epoch2 entry extension; frozen migration engine stays byte-identical."""
import json,sys,pathlib
N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2');B=pathlib.Path('/root/data/ep_l2_main_vector_r5_20261023_v1')
sys.path.insert(0,str(B));import vector_runtime as v
def main(args):
 if len(args)>=3 and args[2]==v.C and args[0] in ['experiment','result']:
  if '--project' in args:v.need(args[args.index('--project')+1]=='EP_L2','project mismatch')
  if args[0]=='experiment':
   if args[1]=='accept':
    import vector_accept;return vector_accept.acceptance()
   return v.main([args[1]])
  import vector_result
  if args[1]=='archive':return vector_result.archive(v.C)
  if args[1]=='restore':return vector_result.restore(args[2],args[args.index('--destination')+1])
  raise RuntimeError('unsupported exact result operation')
 sys.path.insert(0,str(N/'tools'));import native_v2
 out=native_v2.main(args)
 if len(args)>=2 and args[:2]==['project','status']:
  out['native_research_requests']=v.read(v.REG).get('registered_future_requests',{})
 return out
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),ensure_ascii=False,indent=2))
 except Exception as e:print(json.dumps({'status':'HOLD','reason':str(e),'automatic_retry':False},ensure_ascii=False),file=sys.stderr);sys.exit(2)
