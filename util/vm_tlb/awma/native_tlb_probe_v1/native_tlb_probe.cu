#include <cuda_runtime.h>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <numeric>
#include <random>
#include <string>
#include <vector>

#define CK(x) do { cudaError_t e=(x); if(e!=cudaSuccess){fprintf(stderr,"CUDA: %s\n",cudaGetErrorString(e)); return 2;} } while(0)

__device__ __forceinline__ uint32_t load_default(const uint32_t* p) { return *p; }
__device__ __forceinline__ uint32_t load_cg(const uint32_t* p) {
  uint32_t v; asm volatile("ld.global.cg.u32 %0, [%1];" : "=r"(v) : "l"(p)); return v;
}
__global__ void init_chain(uint32_t* data, const uint32_t* permutation, uint32_t n, uint64_t words_stride) {
  uint32_t i=blockIdx.x*blockDim.x+threadIdx.x; if(i<n) data[(uint64_t)permutation[i]*words_stride]=permutation[(i+1)%n];
}
__global__ void chase(const uint32_t* data,uint32_t n,uint64_t words_stride,int steps,int samples,bool cg,uint64_t* cycles) {
  int lane=threadIdx.x&31, warp=threadIdx.x>>5; if(lane || warp>=blockDim.x/32) return;
  for(int s=0;s<samples;s++) { uint32_t idx=(uint32_t)((s*17+warp*131)%n); uint64_t t0=clock64();
    for(int j=0;j<steps;j++) idx=cg?load_cg(data+(uint64_t)idx*words_stride):load_default(data+(uint64_t)idx*words_stride);
    uint64_t t1=clock64(); cycles[warp*samples+s]=(t1-t0)/(uint64_t)steps; if(idx==0xffffffffu) cycles[warp*samples+s]=0; }
}
__global__ void overhead(int steps,int samples,uint64_t* cycles) {
  int lane=threadIdx.x&31, warp=threadIdx.x>>5; if(lane || warp>=blockDim.x/32) return;
  for(int s=0;s<samples;s++){ volatile uint32_t x=(uint32_t)(s+warp); uint64_t t0=clock64(); for(int j=0;j<steps;j++) x=x*1664525u+1013904223u; uint64_t t1=clock64(); cycles[warp*samples+s]=(t1-t0)/(uint64_t)steps; }
}
int main(int argc,char**argv){
 uint64_t stride=4096,thrash_stride=0; uint32_t n=16,thrash_n=0; int samples=50,steps=512,warps=1,warmup=1; uint64_t seed=1; bool cg=false;
 for(int i=1;i<argc;i++){std::string a=argv[i]; auto val=[&](){return argv[++i];}; if(a=="--stride")stride=strtoull(val(),0,0); else if(a=="--locations")n=strtoul(val(),0,0); else if(a=="--samples")samples=atoi(val()); else if(a=="--steps")steps=atoi(val()); else if(a=="--warps")warps=atoi(val()); else if(a=="--seed")seed=strtoull(val(),0,0); else if(a=="--policy")cg=std::string(val())=="cg"; else if(a=="--warmup-batches")warmup=atoi(val()); else if(a=="--thrash-stride")thrash_stride=strtoull(val(),0,0); else if(a=="--thrash-locations")thrash_n=strtoul(val(),0,0); else {fprintf(stderr,"unknown arg %s\n",a.c_str());return 64;}}
 if(!n||!samples||!steps||!warps||stride<4||stride%4){fprintf(stderr,"invalid dimensions\n");return 64;}
 size_t bytes=(size_t)n*(size_t)stride,thrash_bytes=(size_t)thrash_n*(size_t)thrash_stride; size_t free_b,total_b; CK(cudaMemGetInfo(&free_b,&total_b)); if(bytes+thrash_bytes>free_b/2){fprintf(stderr,"SAFE_FOOTPRINT_EXCEEDED bytes=%zu thrash=%zu free=%zu\n",bytes,thrash_bytes,free_b);return 3;}
 uint32_t *d=nullptr,*perm_d=nullptr,*td=nullptr,*tperm_d=nullptr; uint64_t *out=nullptr; std::vector<uint32_t> perm(n);std::iota(perm.begin(),perm.end(),0);std::mt19937_64 rng(seed);std::shuffle(perm.begin(),perm.end(),rng);
 CK(cudaMalloc(&d,bytes)); CK(cudaMalloc(&perm_d,n*sizeof(uint32_t))); CK(cudaMalloc(&out,(size_t)warps*samples*sizeof(uint64_t))); CK(cudaMemcpy(perm_d,perm.data(),n*sizeof(uint32_t),cudaMemcpyHostToDevice));
 init_chain<<<(n+255)/256,256>>>(d,perm_d,n,stride/4); CK(cudaGetLastError()); CK(cudaDeviceSynchronize());
 if(thrash_n){std::vector<uint32_t> tp(thrash_n);std::iota(tp.begin(),tp.end(),0);std::shuffle(tp.begin(),tp.end(),rng);CK(cudaMalloc(&td,thrash_bytes));CK(cudaMalloc(&tperm_d,thrash_n*sizeof(uint32_t)));CK(cudaMemcpy(tperm_d,tp.data(),thrash_n*sizeof(uint32_t),cudaMemcpyHostToDevice));init_chain<<<(thrash_n+255)/256,256>>>(td,tperm_d,thrash_n,thrash_stride/4);CK(cudaGetLastError());CK(cudaDeviceSynchronize());chase<<<1,32>>>(td,thrash_n,thrash_stride/4,steps,1,cg,out);CK(cudaGetLastError());CK(cudaDeviceSynchronize());}
 if(warmup){chase<<<1,warps*32>>>(d,n,stride/4,steps,warmup,cg,out);CK(cudaGetLastError());CK(cudaDeviceSynchronize());}
 chase<<<1,warps*32>>>(d,n,stride/4,steps,samples,cg,out); CK(cudaGetLastError()); CK(cudaDeviceSynchronize()); std::vector<uint64_t> x((size_t)warps*samples);CK(cudaMemcpy(x.data(),out,x.size()*sizeof(uint64_t),cudaMemcpyDeviceToHost));
 overhead<<<1,warps*32>>>(steps,samples,out); CK(cudaGetLastError()); CK(cudaDeviceSynchronize()); std::vector<uint64_t> ov(x.size());CK(cudaMemcpy(ov.data(),out,ov.size()*sizeof(uint64_t),cudaMemcpyDeviceToHost));
 printf("stride_bytes\tlocations\tbytes\twarps\tsteps\tsamples\tpolicy\twarmup_batches\tthrash_bytes\tcycles_per_load\toverhead_cycles\n"); for(size_t i=0;i<x.size();i++)printf("%llu\t%u\t%zu\t%d\t%d\t%d\t%s\t%d\t%zu\t%llu\t%llu\n",(unsigned long long)stride,n,bytes,warps,steps,samples,cg?"cg":"default",warmup,thrash_bytes,(unsigned long long)x[i],(unsigned long long)ov[i]);
 cudaFree(tperm_d);cudaFree(td);cudaFree(out);cudaFree(perm_d);cudaFree(d);return 0;
}
