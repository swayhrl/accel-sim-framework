#pragma once
#include <cuda.h>
#include "generated_cuda_meta.h"
#include <map>
#include <utility>
#include <stdexcept>
#include <string>
#include <cstdint>
struct AdaLaunchConfig {
 CUfunction function=nullptr; unsigned gx=1,gy=1,gz=1,bx=0,by=0,bz=0,shared=0;CUstream stream=nullptr;
};
class AdaLegacyLaunchState {
 struct State { unsigned bx=0,by=0,bz=0,shared=0;bool block=false,shared_set=false; };
 std::map<std::pair<uint64_t,uintptr_t>,State> states;
 State&state(uint64_t generation,CUfunction f){
  if(!generation||!f)throw std::runtime_error("missing context generation/function");
  return states[{generation,reinterpret_cast<uintptr_t>(f)}];
 }
 public:
 void block(uint64_t generation,const cuFuncSetBlockShape_params&p,CUresult result){
  if(result!=CUDA_SUCCESS)return;
  if(p.x<=0||p.y<=0||p.z<=0)throw std::runtime_error("invalid successful legacy block");
  auto&s=state(generation,p.hfunc);s.bx=p.x;s.by=p.y;s.bz=p.z;s.block=true;
 }
 void shared(uint64_t generation,const cuFuncSetSharedSize_params&p,CUresult result){
  if(result!=CUDA_SUCCESS)return;
  auto&s=state(generation,p.hfunc);s.shared=p.bytes;s.shared_set=true;
 }
 AdaLaunchConfig decode(uint64_t generation,const std::string&api,const void *params){
  AdaLaunchConfig c;int gx=1,gy=1;
  if(api=="cuLaunch"){const auto&p=*static_cast<const cuLaunch_params*>(params);c.function=p.f;}
  else if(api=="cuLaunchGrid"){const auto&p=*static_cast<const cuLaunchGrid_params*>(params);c.function=p.f;gx=p.grid_width;gy=p.grid_height;}
  else if(api=="cuLaunchGridAsync"){const auto&p=*static_cast<const cuLaunchGridAsync_params*>(params);c.function=p.f;gx=p.grid_width;gy=p.grid_height;c.stream=p.hStream;}
  else throw std::runtime_error("unknown legacy launch API");
  if(gx<=0||gy<=0)throw std::runtime_error("nonpositive legacy grid");
  auto&s=state(generation,c.function);
  if(!s.block||!s.shared_set)throw std::runtime_error("missing explicit successful legacy block/shared source");
  c.gx=gx;c.gy=gy;c.bx=s.bx;c.by=s.by;c.bz=s.bz;c.shared=s.shared;return c;
 }
};
