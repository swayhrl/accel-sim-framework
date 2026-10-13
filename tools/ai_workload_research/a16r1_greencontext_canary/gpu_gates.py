"""Sequential conditional G1/G2 then G3; no unsafe external handle reuse or model performance."""
import pathlib,os,json,subprocess,sys,traceback,hashlib
root=pathlib.Path(os.environ['TASK_DATA']);old=pathlib.Path(os.environ['OLD_TASK_DATA']);raw=root/'raw';receipt={'status':'RUNNING','G1':'NOT_RUN','G2':'NOT_RUN','G3':'NOT_RUN','G4':'NOT_RUN','formal_performance_samples':0}
def save():(raw/'GATES_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
try:
 save()
 with (raw/'DRIVER_G1_G2_RESULT.json').open('w') as out,(raw/'DRIVER_G1_G2_STDERR.log').open('w') as err:r=subprocess.run([str(root/'build/driver_probe'),str(root/'build/tiny_kernel.cubin')],stdout=out,stderr=err)
 driver=json.loads((raw/'DRIVER_G1_G2_RESULT.json').read_text());receipt['G1']=driver['G1'];receipt['G2']=driver['G2'];save()
 if r.returncode or driver['status']!='PASS_G1_G2':receipt.update(status='STOP_G1_OR_G2',G3='NOT_RUN_PRIOR_GATE_STOP',G4='NOT_RUN_PRIOR_GATE_STOP',reason=driver['error']);save();sys.exit(2)
 # No cuda kernels from libraries before runtime support/ownership is established.
 script=r'''import torch,json,inspect,importlib.metadata as m
import torch.cuda.green_contexts as g
result={'status':'G3_INTEROP_UNQUALIFIED_STOP','torch':torch.__version__,'torch_CUDA':torch.version.cuda,'python_shim_SUPPORTED':bool(g.SUPPORTED),'compiled_CUDAGreenContext_present':hasattr(torch._C,'_CUDAGreenContext'),'GreenContext_create_signature':str(inspect.signature(g.GreenContext.create)),'modern_GreenContext_Stream_method_present':hasattr(g.GreenContext,'Stream'),'ExternalStream_present':hasattr(torch.cuda,'ExternalStream'),'CUDA_context_initialized':torch.cuda.is_initialized(),'model_loaded':False,'AOT_OEQ_ALCHEMI_gpu_ops_executed':False,'model_ops_on_green_stream_proven':False,'external_stream_wrapped':False,'no_monkeypatch_library_or_AOT_changes':True,'live_driver_handles_reused_across_processes':False}
if not g.SUPPORTED:
 try:g.GreenContext.create(1,0)
 except Exception as e:result['unsupported_guard_exception']={'type':type(e).__name__,'message':str(e)}
 result['reason']='Installed torch2.10.0+cu126 lacks _CUDAGreenContext; native shim cannot create/set/pop Green Context. ExternalStream availability alone does not establish AOT/OEQ/ALCHEMI operations on the proven Driver stream.'
else:result['reason']='Python support exists, but no permitted live same-process framework ownership/dependency proof for all AOT/OEQ/ALCHEMI GPU operations was established; cannot reuse destroyed child-process handles or infer model routing.'
print(json.dumps(result))
'''
 with (raw/'G3_RUNTIME_STDOUT.json').open('w') as out,(raw/'G3_RUNTIME_STDERR.log').open('w') as err:r=subprocess.run([str(old/'venv/bin/python'),'-c',script],stdout=out,stderr=err)
 if r.returncode:receipt.update(status='STOP_G3',G3='G3_RUNTIME_INSPECTION_FAILED',G4='NOT_RUN_G3_STOP',reason='Pinned framework runtime inspection failed');save();sys.exit(3)
 framework=json.loads((raw/'G3_RUNTIME_STDOUT.json').read_text());receipt.update(status='STOP_G3_INTEROP_UNQUALIFIED',G3='G3_INTEROP_UNQUALIFIED_STOP',G4='NOT_RUN_G3_STOP',reason=framework['reason']);save();print(json.dumps(receipt),flush=True);sys.exit(3)
except Exception as e:receipt.update(status='STOP',error=str(e),traceback=traceback.format_exc());save();print(receipt['traceback'],flush=True);sys.exit(1)
