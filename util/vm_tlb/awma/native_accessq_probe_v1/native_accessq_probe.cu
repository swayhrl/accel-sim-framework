#include <cuda_runtime.h>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <numeric>
#include <random>
#include <string>
#include <vector>

#define CK(x) do { cudaError_t e=(x); if(e!=cudaSuccess){fprintf(stderr,"CUDA: %s\n",cudaGetErrorString(e));return 2;} } while(0)
constexpr uint32_t kLineWords=32, kLocations=256, kGroupBytes=65536;

__global__ void init_nodes(uint32_t* data,const uint32_t* perm,int fanout,uint64_t group_words){
  uint32_t i=blockIdx.x*blockDim.x+threadIdx.x; if(i>=kLocations*fanout*kLineWords)return;
  uint32_t lane_word=i%kLineWords, node=(i/kLineWords)%kLocations, group=i/(kLineWords*kLocations);
  data[group*group_words+(uint64_t)node*kLineWords+lane_word]=perm[(node+1)%kLocations];
}
__global__ void accessq_chase(const uint32_t* data,int fanout,int steps,int samples,uint64_t group_words,uint64_t* cycles){
  int lane=threadIdx.x&31, warp=threadIdx.x>>5; int group=lane/(32/fanout); int word=lane%(32/fanout);
  for(int s=0;s<samples;s++){
    uint32_t index=(uint32_t)((s*17+warp*131)%kLocations); __syncwarp(); uint64_t t0=clock64();
    for(int j=0;j<steps;j++){
      const volatile uint32_t* p=(const volatile uint32_t*)(data+group*group_words+(uint64_t)index*kLineWords+word);
      uint32_t next=*p; index=__shfl_sync(0xffffffffu,next,0); __syncwarp();
    }
    uint64_t t1=clock64(); if(lane==0)cycles[warp*samples+s]=(t1-t0)/(uint64_t)steps;
  }
}
int main(int argc,char**argv){
 int fanout=1,warps=1,steps=256,samples=50,warmup=2; uint64_t seed=102;
 for(int i=1;i<argc;i++){std::string a=argv[i];auto v=[&](){return argv[++i];};if(a=="--fanout")fanout=atoi(v());else if(a=="--warps")warps=atoi(v());else if(a=="--steps")steps=atoi(v());else if(a=="--samples")samples=atoi(v());else if(a=="--warmup-batches")warmup=atoi(v());else if(a=="--seed")seed=strtoull(v(),0,0);else return 64;}
 if((fanout!=1&&fanout!=8&&fanout!=32)||warps<1||warps>8||steps<1||samples<1)return 64;
 uint64_t group_words=kGroupBytes/4, words=(uint64_t)fanout*group_words; size_t bytes=words*4,free_b,total_b;CK(cudaMemGetInfo(&free_b,&total_b));if(bytes>free_b/4)return 3;
 std::vector<uint32_t> perm(kLocations);std::iota(perm.begin(),perm.end(),0);std::mt19937_64 rng(seed);std::shuffle(perm.begin(),perm.end(),rng);
 uint32_t* data=nullptr,*pd=nullptr;uint64_t*out=nullptr;CK(cudaMalloc(&data,bytes));CK(cudaMalloc(&pd,kLocations*4));CK(cudaMalloc(&out,(size_t)warps*samples*8));CK(cudaMemcpy(pd,perm.data(),kLocations*4,cudaMemcpyHostToDevice));
 init_nodes<<<(fanout*kLocations*kLineWords+255)/256,256>>>(data,pd,fanout,group_words);CK(cudaGetLastError());CK(cudaDeviceSynchronize());
 if(warmup){accessq_chase<<<1,warps*32>>>(data,fanout,steps,warmup,group_words,out);CK(cudaGetLastError());CK(cudaDeviceSynchronize());}
 accessq_chase<<<1,warps*32>>>(data,fanout,steps,samples,group_words,out);CK(cudaGetLastError());CK(cudaDeviceSynchronize());std::vector<uint64_t>x((size_t)warps*samples);CK(cudaMemcpy(x.data(),out,x.size()*8,cudaMemcpyDeviceToHost));
 printf("fanout\twarps\tlocations\tsteps\tsamples\twarmup_batches\tseed\tgroup_separation_bytes\tcycles_per_step\n");for(size_t i=0;i<x.size();i++)printf("%d\t%d\t%d\t%d\t%d\t%d\t%llu\t%d\t%llu\n",fanout,warps,kLocations,steps,samples,warmup,(unsigned long long)seed,kGroupBytes,(unsigned long long)x[i]);cudaFree(out);cudaFree(pd);cudaFree(data);
}
