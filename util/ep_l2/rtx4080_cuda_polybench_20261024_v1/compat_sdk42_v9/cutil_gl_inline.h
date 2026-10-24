#pragma once
#include <cutil_inline.h>
#include <helper_cuda_gl.h>
#define cutilGLDeviceInit(argc,argv) findCudaGLDevice(argc,(const char**)(argv))
