#include <cuda_runtime.h>
#include <cuda_profiler_api.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
#define CK(x) do { auto e=(x); if(e!=cudaSuccess){fprintf(stderr,"%s:%d %s\n",__FILE__,__LINE__,cudaGetErrorString(e));exit(2);} }while(0)
constexpr unsigned N=1u<<25, THREADS=304*128, ROUNDS=1024;
__device__ __forceinline__ unsigned ld(const unsigned* p){unsigned x;asm volatile("ld.global.ca.u32 %0, [%1];":"=r"(x):"l"(p):"memory");return x;}
template<int MODE,int ILP> __global__ void diag(const unsigned* a,unsigned* out){
 unsigned tid=blockIdx.x*blockDim.x+threadIdx.x, sum=0;
 if constexpr(MODE>=8){
  unsigned mask=MODE==8?8191:N-1, p=tid&mask;
  #pragma unroll 1
  for(unsigned r=0;r<ROUNDS;r++) p=ld(a+p)&mask;
  out[tid]=p;
 }else{
  #pragma unroll 1
  for(unsigned r=0;r<ROUNDS;r+=ILP){
   unsigned vals[ILP];
   #pragma unroll
   for(int j=0;j<ILP;j++){
    unsigned id=(r+j)*THREADS+tid;
    if constexpr(MODE==1)id*=32;
    if constexpr(MODE==2)id*=257;
    if constexpr(MODE==3)id=(r+j)*THREADS+tid/4;
    if constexpr(MODE==4)id=(r+j)*THREADS+tid/32;
    if constexpr(MODE==5)id=((r+j)*32+tid)&8191;
    vals[j]=ld(a+(id&(N-1)));
   }
   #pragma unroll
   for(int j=0;j<ILP;j++)sum+=vals[j];
  }
  out[tid]=sum;
 }
}
struct Cell{const char* name;int mode,ilp;};
Cell cells[]={ {"independent_i1",0,1},{"independent_i4",0,4},{"independent_i8",0,8},
 {"address_stride1",0,4},{"address_stride32",1,4},{"address_stride257",2,4},
 {"consumers_g1",0,4},{"consumers_g4",3,4},{"consumers_g32",4,4},
 {"control_hit32k",5,4},{"control_chain32k",8,1},{"control_chain128m",9,1} };
int main(int argc,char** argv){
 if(argc!=3){fprintf(stderr,"usage: diagnostic CONDITION timing|profile\n");return 2;}
 Cell* c=nullptr;for(auto &x:cells)if(x.name==std::string(argv[1]))c=&x;if(!c)return 2;
 const void* fun=nullptr;
 if(c->mode==0){if(c->ilp==1)fun=(void*)diag<0,1>;if(c->ilp==4)fun=(void*)diag<0,4>;if(c->ilp==8)fun=(void*)diag<0,8>;}
 if(c->mode==1)fun=(void*)diag<1,4>;if(c->mode==2)fun=(void*)diag<2,4>;
 if(c->mode==3)fun=(void*)diag<3,4>;if(c->mode==4)fun=(void*)diag<4,4>;if(c->mode==5)fun=(void*)diag<5,4>;
 if(c->mode==8)fun=(void*)diag<8,1>;if(c->mode==9)fun=(void*)diag<9,1>;
 std::vector<unsigned> host(N,1);if(c->mode>=8)for(unsigned i=0;i<N;i++)host[i]=(i+104729)&(N-1);
 unsigned *a,*out;CK(cudaMalloc(&a,N*sizeof(unsigned)));CK(cudaMalloc(&out,THREADS*sizeof(unsigned)));CK(cudaMemcpy(a,host.data(),N*sizeof(unsigned),cudaMemcpyHostToDevice));
 cudaFuncAttributes attr;CK(cudaFuncGetAttributes(&attr,fun));int blocks;CK(cudaOccupancyMaxActiveBlocksPerMultiprocessor(&blocks,fun,128,0));
 auto launch=[&](){void* args[]={&a,&out};CK(cudaLaunchKernel(fun,dim3(304),dim3(128),args,0,nullptr));};
 for(int i=0;i<3;i++)launch();CK(cudaDeviceSynchronize());
 printf("{\"condition\":\"%s\",\"mode\":%d,\"ilp\":%d,\"grid\":304,\"block\":128,\"registers\":%d,\"static_shared\":%zu,\"local_bytes\":%zu,\"max_active_blocks_per_sm\":%d,\"logical_loads\":%u,\"allocation_bytes\":%u,\"warmups\":3,\"samples_ms\":[",c->name,c->mode,c->ilp,attr.numRegs,attr.sharedSizeBytes,attr.localSizeBytes,blocks,THREADS*ROUNDS,N*4);
 if(std::string(argv[2])=="profile") {CK(cudaProfilerStart());launch();CK(cudaDeviceSynchronize());CK(cudaProfilerStop());}
 else {cudaEvent_t begin,end;CK(cudaEventCreate(&begin));CK(cudaEventCreate(&end));for(int i=0;i<10;i++){CK(cudaEventRecord(begin));launch();CK(cudaEventRecord(end));CK(cudaEventSynchronize(end));float ms;CK(cudaEventElapsedTime(&ms,begin,end));printf("%s%.9g",i?",":"",ms);}CK(cudaEventDestroy(begin));CK(cudaEventDestroy(end));}
 std::vector<unsigned> result(THREADS);CK(cudaMemcpy(result.data(),out,THREADS*4,cudaMemcpyDeviceToHost));
 for(unsigned i=0;i<THREADS;i++){unsigned want=ROUNDS;if(c->mode>=8){unsigned mask=c->mode==8?8191:N-1;want=(i+ROUNDS*104729)&mask;}if(result[i]!=want){fprintf(stderr,"mismatch tid=%u got=%u want=%u\n",i,result[i],want);return 3;}}
 printf("],\"correctness\":\"PASS_ALL_OUTPUTS\"}\n");CK(cudaFree(a));CK(cudaFree(out));return 0;
}
