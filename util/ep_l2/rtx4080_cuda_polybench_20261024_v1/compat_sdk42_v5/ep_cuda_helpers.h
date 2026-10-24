#pragma once
#define __getLastCudaError ep_helper_lastCudaError
#define gpuDeviceInit ep_helper_gpuDeviceInit
#define gpuGetMaxGflopsDeviceId ep_helper_gpuGetMaxGflopsDeviceId
#define findCudaDevice ep_helper_findCudaDevice
#include <helper_cuda.h>
#undef gpuDeviceInit
#undef gpuGetMaxGflopsDeviceId
#undef findCudaDevice
#undef __getLastCudaError
#ifndef ConvertSMVer2Cores
#define ConvertSMVer2Cores _ConvertSMVer2Cores
#endif
