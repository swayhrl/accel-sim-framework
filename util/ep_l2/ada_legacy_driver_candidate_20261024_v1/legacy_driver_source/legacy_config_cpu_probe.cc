#include "legacy_launch_config_v1.h"
#include <cassert>
#include <cstdio>
template<class F>void reject(F f){bool caught=false;try{f();}catch(const std::runtime_error&){caught=true;}assert(caught);}
int main(){
 static_assert(sizeof(cuLaunch_params)<sizeof(cuLaunchKernel_params),"legacy layout not modern");
 static_assert(sizeof(cuLaunchGrid_params)<sizeof(cuLaunchKernel_params),"legacy layout not modern");
 AdaLegacyLaunchState s;CUfunction f=reinterpret_cast<CUfunction>(0x1234);CUstream stream=reinterpret_cast<CUstream>(0x4567);
 cuFuncSetBlockShape_params shape{f,37,1,1};cuFuncSetSharedSize_params shared{f,0};
 cuLaunchGrid_params grid{f,2,1};cuLaunchGridAsync_params async{f,2,1,stream};cuLaunch_params launch{f};
 reject([&]{s.decode(1,"cuLaunchGrid",&grid);});
 s.block(1,shape,CUDA_SUCCESS);reject([&]{s.decode(1,"cuLaunchGrid",&grid);});s.shared(1,shared,CUDA_SUCCESS);
 auto a=s.decode(1,"cuLaunchGrid",&grid);assert(a.gx==2&&a.gy==1&&a.gz==1&&a.bx==37&&a.by==1&&a.bz==1&&a.shared==0&&a.stream==nullptr);
 auto b=s.decode(1,"cuLaunchGridAsync",&async);assert(b.gx==2&&b.bx==37&&b.stream==stream);
 shape.x=65;s.block(1,shape,CUDA_ERROR_INVALID_VALUE);assert(s.decode(1,"cuLaunch",&launch).bx==37);
 s.block(1,shape,CUDA_SUCCESS);auto c=s.decode(1,"cuLaunch",&launch);assert(c.gx==1&&c.gy==1&&c.bx==65);
 reject([&]{s.decode(2,"cuLaunch",&launch);});reject([&]{s.decode(1,"cuLaunchUnknown",&launch);});grid.grid_width=0;reject([&]{s.decode(1,"cuLaunchGrid",&grid);});
 puts("CPU_TYPED_LEGACY_CONFIG_PASS three_API_layouts block_shared successful_return_only generation_isolation negatives");
}
