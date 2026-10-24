#define GL_GLEXT_PROTOTYPES 1
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GL/gl.h>
#include <GL/glext.h>
#include <cuda_runtime.h>
#include <cuda_gl_interop.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
static void ck(cudaError_t e,const char*op){if(e!=cudaSuccess){fprintf(stderr,"CUDA_ERROR %s %s\n",op,cudaGetErrorString(e));exit(3);}}
static void eg(bool ok,const char*op){if(!ok){fprintf(stderr,"EGL_ERROR %s 0x%x\n",op,eglGetError());exit(4);}}
__global__ void write_pattern(unsigned* p,int n){int i=blockIdx.x*blockDim.x+threadIdx.x;if(i<n)p[i]=0x12340000U+(unsigned)i;}
int main(){
 auto q=(PFNEGLQUERYDEVICESEXTPROC)eglGetProcAddress("eglQueryDevicesEXT");
 auto g=(PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");
 auto a=(PFNEGLQUERYDEVICEATTRIBEXTPROC)eglGetProcAddress("eglQueryDeviceAttribEXT");
 eg(q&&g,"extension entrypoints");EGLDeviceEXT ds[16];EGLint n=0;eg(q(16,ds,&n),"query devices");printf("EGL_DEVICE_COUNT %d\n",n);
 EGLDisplay display=EGL_NO_DISPLAY;EGLint major=0,minor=0;
 for(int i=0;i<n;i++){EGLAttrib cudaDevice=-1;bool got=a&&a(ds[i],0x323A,&cudaDevice);printf("EGL_DEVICE %d cuda_attr_ok=%d cuda_device=%ld\n",i,got,(long)cudaDevice);EGLDisplay d=g(EGL_PLATFORM_DEVICE_EXT,ds[i],0);if(eglInitialize(d,&major,&minor)){const char*v=eglQueryString(d,EGL_VENDOR);printf("EGL_VENDOR_CANDIDATE %s\n",v?v:"");if(v&&strstr(v,"NVIDIA")){display=d;break;}eglTerminate(d);}}
 eg(display!=EGL_NO_DISPLAY,"select NVIDIA device display");eg(eglBindAPI(EGL_OPENGL_API),"bind OpenGL");
 EGLint cfgattrs[]={EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_ALPHA_SIZE,8,EGL_DEPTH_SIZE,24,EGL_NONE};EGLConfig cfg;EGLint count;eg(eglChooseConfig(display,cfgattrs,&cfg,1,&count)&&count,"choose config");EGLint pattrs[]={EGL_WIDTH,64,EGL_HEIGHT,64,EGL_NONE};EGLSurface surface=eglCreatePbufferSurface(display,cfg,pattrs);eg(surface!=EGL_NO_SURFACE,"create pbuffer");EGLContext ctx=eglCreateContext(display,cfg,EGL_NO_CONTEXT,0);eg(ctx!=EGL_NO_CONTEXT,"create context");eg(eglMakeCurrent(display,surface,surface,ctx),"make current");
 const char*vendor=(const char*)glGetString(GL_VENDOR);const char*renderer=(const char*)glGetString(GL_RENDERER);printf("GL_VENDOR %s\nGL_RENDERER %s\nGL_VERSION %s\n",vendor,renderer,glGetString(GL_VERSION));eg(vendor&&strstr(vendor,"NVIDIA")&&renderer&&strstr(renderer,"4080"),"hardware renderer identity");GLboolean dbl;glGetBooleanv(GL_DOUBLEBUFFER,&dbl);GLint draw,read;glGetIntegerv(GL_DRAW_BUFFER,&draw);glGetIntegerv(GL_READ_BUFFER,&read);printf("GL_DOUBLEBUFFER %d DRAW 0x%x READ 0x%x\n",(int)dbl,draw,read);
 glViewport(0,0,64,64);glClearColor(.2f,.4f,.6f,1);glClear(GL_COLOR_BUFFER_BIT);unsigned char pixel[4]={};glReadPixels(0,0,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);printf("CLEAR_RGBA %u %u %u %u GL_ERROR 0x%x\n",pixel[0],pixel[1],pixel[2],pixel[3],glGetError());eg(abs((int)pixel[0]-51)<=1&&abs((int)pixel[1]-102)<=1&&abs((int)pixel[2]-153)<=1&&pixel[3]==255,"GL clear readback");
 unsigned cudaCount=0;int devs[16];ck(cudaGLGetDevices(&cudaCount,devs,16,cudaGLDeviceListAll),"cudaGLGetDevices");eg(cudaCount==1&&devs[0]==0,"GL CUDA device correspondence");ck(cudaSetDevice(0),"set CUDAdevice");cudaDeviceProp prop;ck(cudaGetDeviceProperties(&prop,0),"properties");printf("CUDA_DEVICE %s\n",prop.name);
 GLuint buffer;glGenBuffers(1,&buffer);glBindBuffer(GL_ARRAY_BUFFER,buffer);const int len=4096;glBufferData(GL_ARRAY_BUFFER,len*sizeof(unsigned),0,GL_DYNAMIC_DRAW);eg(glGetError()==GL_NO_ERROR,"allocate GLbuffer");cudaGraphicsResource* resource=0;ck(cudaGraphicsGLRegisterBuffer(&resource,buffer,cudaGraphicsRegisterFlagsWriteDiscard),"register GLbuffer");ck(cudaGraphicsMapResources(1,&resource,0),"map");unsigned*ptr;size_t bytes;ck(cudaGraphicsResourceGetMappedPointer((void**)&ptr,&bytes,resource),"mapped pointer");eg(bytes>=len*sizeof(unsigned),"mapped size");write_pattern<<<16,256>>>(ptr,len);ck(cudaGetLastError(),"launch");ck(cudaDeviceSynchronize(),"sync");ck(cudaGraphicsUnmapResources(1,&resource,0),"unmap");std::vector<unsigned> result(len);glGetBufferSubData(GL_ARRAY_BUFFER,0,len*sizeof(unsigned),result.data());eg(glGetError()==GL_NO_ERROR,"GLbuffer readback");for(int i=0;i<len;i++)if(result[i]!=0x12340000U+(unsigned)i){fprintf(stderr,"MISMATCH index=%d\n",i);return 5;}printf("REAL_GPU_EGL_CUDA_GL_INTEROP_PASSED words=%d\n",len);
 ck(cudaGraphicsUnregisterResource(resource),"unregister");glDeleteBuffers(1,&buffer);eglMakeCurrent(display,EGL_NO_SURFACE,EGL_NO_SURFACE,EGL_NO_CONTEXT);eglDestroyContext(display,ctx);eglDestroySurface(display,surface);eglTerminate(display);return 0;
}
