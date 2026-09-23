#include <cuda_runtime.h>
#include <cstdio>
#include <vector>
#include <numeric>
#include <algorithm>
#include <random>
__global__ void initp(unsigned* d,const unsigned* p,unsigned n,unsigned stride){unsigned i=blockIdx.x*blockDim.x+threadIdx.x;if(i<n*32){unsigned node=i/32,word=i%32;d[node*stride+word]=p[(node+1)%n];}}
__global__ void chasep(const unsigned*d,unsigned n,unsigned stride,int steps,int samples,unsigned long long*out){int lane=threadIdx.x&31;for(int s=0;s<samples;s++){unsigned idx=s%n;__syncwarp();auto t=clock64();for(int j=0;j<steps;j++){unsigned x=((volatile const unsigned*)d)[idx*stride+lane];idx=__shfl_sync(0xffffffff,x,0);__syncwarp();}if(!lane)out[s]=(clock64()-t)/steps;}}
int main(int c,char**v){unsigned n=c>1?atoi(v[1]):16,stride=c>2?atoi(v[2]):1024;int steps=c>3?atoi(v[3]):512,samples=c>4?atoi(v[4]):50;std::vector<unsigned>p(n);std::iota(p.begin(),p.end(),0);std::mt19937_64 r(102);std::shuffle(p.begin(),p.end(),r);unsigned*d,*q;unsigned long long*o;cudaMalloc(&d,(size_t)n*stride*4);cudaMalloc(&q,n*4);cudaMalloc(&o,samples*8);cudaMemcpy(q,p.data(),n*4,cudaMemcpyHostToDevice);initp<<<(n*32+255)/256,256>>>(d,q,n,stride);cudaDeviceSynchronize();chasep<<<1,32>>>(d,n,stride,steps,2,o);cudaDeviceSynchronize();chasep<<<1,32>>>(d,n,stride,steps,samples,o);cudaDeviceSynchronize();std::vector<unsigned long long>x(samples);cudaMemcpy(x.data(),o,samples*8,cudaMemcpyDeviceToHost);printf("locations\tstride_words\tsteps\tsamples\tcycles\n");for(auto z:x)printf("%u\t%u\t%d\t%d\t%llu\n",n,stride,steps,samples,z);}
