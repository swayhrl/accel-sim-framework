#pragma once
#include <cuda_runtime.h>
#include <cutil.h>
#include "ep_cuda_helpers.h"
#include <helper_functions.h>
#define cutilSafeCall checkCudaErrors
#define cutilCheckError(a) do {if(!(a)){fprintf(stderr,"CUTIL_CHECK_FAILED %s\n",#a);exit(1);}} while(0)
#define cutilCheckMsg(msg) ep_helper_lastCudaError(msg,__FILE__,__LINE__)
#define cutilDeviceInit(argc,argv) ep_helper_findCudaDevice(argc,(const char**)(argv))
#define cutilDeviceReset cudaDeviceReset
#define cutilDeviceSynchronize cudaDeviceSynchronize
#define cutGetMaxGflopsDeviceId ep_helper_gpuGetMaxGflopsDeviceId
#define cutilSafeMalloc(p) do {if(!(p)){fprintf(stderr,"HOST_MALLOC_FAILED\n");exit(1);}} while(0)

#define cutilChooseCudaDevice(argc,argv) ep_helper_findCudaDevice(argc,(const char**)(argv))
#define cutilSafeCallNoSync checkCudaErrors
#define cutilCondition(a) cutilCheckError(a)

#define cutilDrvSafeCallNoSync cutilDrvSafeCall

#undef cutilDrvSafeCallNoSync
#define cutilDrvSafeCallNoSync checkCudaErrors
