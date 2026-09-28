#!/usr/bin/env python3
"""CPU-safe frozen contracts for the split-K footprint threshold screen."""
import hashlib,json,math,struct

M=256; N=49152; GROUP_SIZE=128; KS=(2048,2560,3072,4096)
L2_BYTES=67_108_864
A_SHA="9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7"
B_SHA="1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887"
A_PATH="/data/c16/env/c16-awq-v6/lib/python3.10/site-packages/awq_ext.cpython-310-x86_64-linux-gnu.so"
B_PATH="/data/c16/e1_lowbit_splitk_native_ab_v1/build/lib/awq_split1_ext.cpython-310-x86_64-linux-gnu.so"
QWEIGHT_WORD_U32=0xECA86420; QWEIGHT_WORD_I32=QWEIGHT_WORD_U32-(1<<32)
QZERO_WORD_I32=0x77777777; SCALE=2.0**-8
SYNTH_VERSION="GPT3_SHAPE_SYNTH_V1"
TINY_SHA="bc5b86bb5c440be4fa308f3c6d85922297148cf911cad8a33e0d3373928a7e3e"

def w4_input_value(m,k): return (1+((5*m+3*k)%7))*2.0**-10
def dense_input_value(m,k): return (1+((3*m+k)%7))*2.0**-10
def dense_weight_value(k,n): return (1+((5*k+n)%11))*2.0**-12
def point_name(k): return f"K{k}"
def point_math(k,split):
 return {"K":k,"M":M,"N":N,"split":split,"gemm_grid":math.ceil(M/16)*(N//128)*split,"scratch_bytes":split*M*N*2,"reduction_grid":math.ceil(M*N/512) if split==8 else 0,"qweight_bytes":k*(N//8)*4,"qzeros_bytes":(k//GROUP_SIZE)*(N//8)*4,"scales_bytes":(k//GROUP_SIZE)*N*2,"full_w4_bytes":k*(N//8)*4+(k//GROUP_SIZE)*(N//8)*4+(k//GROUP_SIZE)*N*2}
def candidate_split8_static_bytes(k): return point_math(k,8)["qweight_bytes"]//8+(point_math(k,8)["qzeros_bytes"]+point_math(k,8)["scales_bytes"])//2
def expected_rows():
 rows=[]
 for k in KS:
  for arm,split in (("A",8),("B",1)):
   x=point_math(k,split); rows.append({"point":point_name(k),"K":k,"M":M,"N":N,"arm":arm,"split_k_iters":split,"gemm_grid":x["gemm_grid"],"gemm_block":"[32,2,1]","scratch_shape":json.dumps([split,M,N],separators=(",",":")),"scratch_bytes":x["scratch_bytes"],"reduction_expected":arm=="A","reduction_grid":x["reduction_grid"],"reduction_block":"[32,4,1]" if arm=="A" else "NA"})
 return rows
def footprint_rows():
 rows=[]
 for k in KS:
  x=point_math(k,1); rows.append({"point":point_name(k),"K":k,"full_w4_bytes":x["full_w4_bytes"],"full_w4_mib":x["full_w4_bytes"]/2**20,"full_over_l2":x["full_w4_bytes"]/L2_BYTES,"candidate_split8_static_bytes":candidate_split8_static_bytes(k),"candidate_split8_static_mib":candidate_split8_static_bytes(k)/2**20})
 return rows
def tiny_reference():
 m,k,n=2,256,16
 hb=lambda vals:b"".join(struct.pack("<e",float(v)) for v in vals)
 ib=lambda vals:b"".join(struct.pack("<i",int(v)) for v in vals)
 tensors={"dense_input_f16":hb(dense_input_value(i,j) for i in range(m) for j in range(k)),"dense_weight_f16":hb(dense_weight_value(i,j) for i in range(k) for j in range(n)),"w4_input_f16":hb(w4_input_value(i,j) for i in range(m) for j in range(k)),"qweight_i32":ib(QWEIGHT_WORD_I32 for _ in range(k*(n//8))),"qzeros_i32":ib(QZERO_WORD_I32 for _ in range((k//GROUP_SIZE)*(n//8))),"scales_f16":hb(SCALE for _ in range((k//GROUP_SIZE)*n))}
 value={"version":SYNTH_VERSION,"shape":{"M":m,"K":k,"N":n,"group_size":GROUP_SIZE},"byte_order":"little-endian; IEEE-754 binary16 and signed int32 two's complement","tensor_sha256":{name:hashlib.sha256(data).hexdigest() for name,data in tensors.items()}}
 value["reference_sha256"]=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest(); return value
