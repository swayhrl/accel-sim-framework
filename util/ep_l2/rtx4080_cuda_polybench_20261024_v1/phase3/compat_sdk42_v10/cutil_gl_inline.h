#pragma once
#include <GL/glew.h>
#include <GL/glu.h>
#include <cuda_gl_interop.h>
#include <cutil_inline.h>
template<class T> inline int findCudaGLDevice(int argc,T argv){int dev=ep_helper_findCudaDevice(argc,(const char**)argv);checkCudaErrors(cudaGLSetGLDevice(dev));return dev;}
template<class T> inline int gpuGLDeviceInit(int argc,T argv){return findCudaGLDevice(argc,argv);}
#define cutilGLDeviceInit(argc,argv) findCudaGLDevice(argc,argv)
