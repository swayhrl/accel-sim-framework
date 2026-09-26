#include <cuda_runtime.h>
#include <nvToolsExt.h>
#include <sys/sysinfo.h>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

#define CK(x) do{cudaError_t e=(x);if(e!=cudaSuccess){fprintf(stderr,"CUDA_ERROR %s:%d %s\n",__FILE__,__LINE__,cudaGetErrorString(e));return 2;}}while(0)
struct Range{uint64_t off,bytes;int layer,expert;bool expert_group;};
struct Route{int event,step,token,layer;std::vector<int> experts;};
__global__ void touch(const uint32_t* p,uint64_t b,uint64_t e,unsigned long long*out){unsigned long long s=0;for(uint64_t i=b+blockIdx.x*blockDim.x+threadIdx.x;i<e;i+=(uint64_t)gridDim.x*blockDim.x)s+=p[i];atomicAdd(out,s);}
static std::string arg(int n,char**v,const char*k,const char*d=""){for(int i=1;i+1<n;i++)if(!strcmp(v[i],k))return v[i+1];return d;}
static std::vector<std::string> split(const std::string&s,char c){std::vector<std::string>v;std::stringstream q(s);std::string x;while(std::getline(q,x,c))v.push_back(x);return v;}
static std::vector<Range> ranges(const std::string&p,bool moe){std::ifstream f(p);std::string l;std::getline(f,l);std::vector<Range>v;while(std::getline(f,l)){auto x=split(l,'\t');if(moe)v.push_back({std::stoull(x[1]),std::stoull(x[2]),x[4]=="N/A"?-1:std::stoi(x[4]),x[5]=="N/A"?-1:std::stoi(x[5]),x[3]=="EXPERT"});else v.push_back({std::stoull(x[1]),std::stoull(x[2]),-1,-1,false});}return v;}
static std::vector<Route> routes(const std::string&p){std::ifstream f(p);std::string l;std::getline(f,l);std::vector<Route>v;while(std::getline(f,l)){auto x=split(l,'\t');Route r{std::stoi(x[0]),std::stoi(x[1]),std::stoi(x[2]),std::stoi(x[3]),{}};for(auto&e:split(x[5],','))r.experts.push_back(std::stoi(e));v.push_back(r);}return v;}
static uint64_t avail(){std::ifstream f("/proc/meminfo");std::string k,u;uint64_t v;while(f>>k>>v>>u)if(k=="MemAvailable:")return v*1024;return 0;}
static void launch(const uint32_t*p,const Range&r,unsigned long long*out){uint64_t b=r.off/4,e=(r.off+r.bytes)/4;if(e>b)touch<<<std::min<uint64_t>(256,(e-b+255)/256),256>>>(p,b,e,out);}
int main(int argc,char**argv){
 std::string pat=arg(argc,argv,"--pattern"),mode=arg(argc,argv,"--mode","M0"),root=arg(argc,argv,"--root"),point=arg(argc,argv,"--point","NA"),outdir=arg(argc,argv,"--out");uint64_t bytes=std::stoull(arg(argc,argv,"--bytes"));if(bytes>(20ull<<30)){fprintf(stderr,"CAP_EXCEEDED\n");return 3;}CK(cudaSetDevice(0));size_t free0,total;CK(cudaMemGetInfo(&free0,&total));uint64_t host0=avail();uint32_t*p=nullptr;unsigned long long*out=nullptr;CK(cudaMallocManaged(&p,bytes));CK(cudaMallocManaged(&out,8));memset(p,1,bytes);*out=0;
 std::vector<Range> rr;if(pat=="D1")rr=ranges(root+"/D1_DENSE_TENSOR_RANGES.tsv",false);else if(pat=="D3")rr=ranges(root+"/D3_MOE_TENSOR_RANGES.tsv",true);std::vector<Route> rt;if(pat=="D3")rt=routes(root+"/D3_DECODE_ROUTE.tsv");
 std::ofstream sf(outdir+"/steps.tsv");sf<<"pattern\tpoint\tmode\trepetition\tstep\tactive_bytes\tselected_experts\tstep_ms\n";float gtot[2]={};double wall[2]={};
 for(int rep=0;rep<2;rep++){const char*rn=rep?"repeat":"cold";auto ws=std::chrono::steady_clock::now();cudaEvent_t ga,gb;CK(cudaEventCreate(&ga));CK(cudaEventCreate(&gb));CK(cudaEventRecord(ga));
  int steps=pat=="D1"?3:(pat=="D2"?16:(int)rt.size());
  for(int s=0;s<steps;s++){std::string label="MODEL_UVM="+pat+";POINT="+point+";MODE="+mode+";REP="+rn+";STEP="+std::to_string(s);nvtxRangePushA(label.c_str());cudaEvent_t a,b;CK(cudaEventCreate(&a));CK(cudaEventCreate(&b));CK(cudaEventRecord(a));uint64_t active=0;std::string selected="";
   if(pat=="D1"){for(auto&r:rr){if(mode=="M1")CK(cudaMemPrefetchAsync((char*)p+r.off,r.bytes,0));launch(p,r,out);active+=r.bytes;}}
   else if(pat=="D2"){uint64_t end=bytes*(s+1)/steps,end4=end/4*4,beg=bytes*s/steps/4*4;if(mode=="M1")CK(cudaMemPrefetchAsync((char*)p+beg,end4-beg,0));Range r{0,end4,-1,-1,false};launch(p,r,out);active=end4;}
   else {auto&e=rt[s];if(s==0||rt[s-1].token!=e.token){for(auto&r:rr)if(!r.expert_group){launch(p,r,out);active+=r.bytes;}}for(size_t j=0;j<e.experts.size();j++){if(j)selected+=",";selected+=std::to_string(e.experts[j]);for(auto&r:rr)if(r.expert_group&&r.layer==e.layer&&r.expert==e.experts[j]){if(mode=="M1")CK(cudaMemPrefetchAsync((char*)p+r.off,r.bytes,0));launch(p,r,out);active+=r.bytes;}}}
   CK(cudaEventRecord(b));CK(cudaEventSynchronize(b));float ms;CK(cudaEventElapsedTime(&ms,a,b));sf<<pat<<'\t'<<point<<'\t'<<mode<<'\t'<<rn<<'\t'<<s<<'\t'<<active<<'\t'<<selected<<'\t'<<ms<<'\n';CK(cudaEventDestroy(a));CK(cudaEventDestroy(b));nvtxRangePop();}
  CK(cudaEventRecord(gb));CK(cudaEventSynchronize(gb));CK(cudaEventElapsedTime(&gtot[rep],ga,gb));wall[rep]=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-ws).count();CK(cudaEventDestroy(ga));CK(cudaEventDestroy(gb));}
 CK(cudaDeviceSynchronize());unsigned long long checksum=*out;CK(cudaFree(out));CK(cudaFree(p));size_t free1,t2;CK(cudaMemGetInfo(&free1,&t2));printf("{\"status\":\"MODEL_DERIVED_UVM_COMPLETE\",\"pattern\":\"%s\",\"point\":\"%s\",\"mode\":\"%s\",\"bytes\":%llu,\"cold_gpu_ms\":%.6f,\"repeat_gpu_ms\":%.6f,\"cold_wall_ms\":%.6f,\"repeat_wall_ms\":%.6f,\"checksum\":%llu,\"gpu_free_before\":%zu,\"gpu_free_after\":%zu,\"host_available_before\":%llu,\"host_available_after\":%llu}\n",pat.c_str(),point.c_str(),mode.c_str(),(unsigned long long)bytes,gtot[0],gtot[1],wall[0],wall[1],checksum,free0,free1,(unsigned long long)host0,(unsigned long long)avail());return 0;
}
