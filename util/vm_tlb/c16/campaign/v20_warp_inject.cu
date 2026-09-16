#include "warp_common.h"
extern "C" __device__ __noinline__ void c16_warp_record(int pred,uint64_t addr,uint32_t idx,uint64_t sp,uint64_t cap,int cb,int ce){ unsigned m=__ballot_sync(__activemask(),pred); if(!m)return; if((int)blockIdx.x<cb||(int)blockIdx.x>=ce)return; unsigned lane=threadIdx.x&31; if(!(m&(1u<<lane)))return; uint64_t gathered[32];for(int i=0;i<32;i++)gathered[i]=__shfl_sync(m,addr,i); if(lane!=(unsigned)(__ffs(m)-1))return; WState*s=(WState*)sp; unsigned long long n=atomicAdd(&s->count,1ULL); if(n>=cap){atomicAdd(&s->overflow,1ULL);return;} WRec&r=s->rec[n];r.static_index=idx;r.active_mask=m;r.cta_x=blockIdx.x;r.cta_y=blockIdx.y;r.cta_z=blockIdx.z;r.warp=(threadIdx.z*blockDim.y*blockDim.x+threadIdx.y*blockDim.x+threadIdx.x)/32;for(int i=0;i<32;i++)r.addr[i]=gathered[i];}

extern "C" __device__ __noinline__ void c16_warp_record_reg(int pred,uint32_t lo,uint32_t hi,uint32_t idx,uint64_t sp,uint64_t cap,int cb,int ce){c16_warp_record(pred,((uint64_t)hi<<32)|lo,idx,sp,cap,cb,ce);}

// Retains the injected device helper in the shared object's fatbin. NVBit
// resolves instrumentation callbacks by this exact device symbol; this
// never launches and therefore cannot affect the producer workload.
extern "C" __global__ void c16_v20_keep_warp_record_symbol(){c16_warp_record(0,0,0,0,0,0,0);c16_warp_record_reg(0,0,0,0,0,0,0,0);}
