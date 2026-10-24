/* Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *  * Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *  * Neither the name of NVIDIA CORPORATION nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
 * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <stdlib.h>

Display *display;
int screen;
Window win = 0;

#include <GLES3/gl31.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>

#define GET_GLERROR(ret)                                                       \
  \
{                                                                         \
    GLenum err = glGetError();                                                 \
    if (err != GL_NO_ERROR) {                                                  \
      fprintf(stderr, "[%s line %d] OpenGL Error: 0x%x\n", __FILE__, __LINE__, \
              err);                                                            \
      fflush(stderr);                                                          \
                                                                               \
      switch (err) {                                                           \
        case GL_INVALID_ENUM:                                                  \
          printf("GL_INVALID_ENUM\n");                                         \
          break;                                                               \
        case GL_INVALID_VALUE:                                                 \
          printf("GL_INVALID_VALUE\n");                                        \
          break;                                                               \
        case GL_INVALID_OPERATION:                                             \
          printf("GL_INVALID_OPERATION\n");                                    \
          break;                                                               \
        case GL_OUT_OF_MEMORY:                                                 \
          printf("GL_OUT_OF_MEMORY\n");                                        \
          break;                                                               \
        case GL_INVALID_FRAMEBUFFER_OPERATION:                                 \
          printf("GL_INVALID_FRAMEBUFFER_OPERATION\n");                        \
          break;                                                               \
        default:                                                               \
          printf("UKNOWN OPENGL ERROR CODE 0x%x\n", err);                      \
      };                                                                       \
    }                                                                          \
  \
}

EGLDisplay eglDisplay = EGL_NO_DISPLAY;
EGLSurface eglSurface = EGL_NO_SURFACE;
EGLContext eglContext = EGL_NO_CONTEXT;

int graphics_setup_window(int xpos,int ypos,int width,int height,const char*windowname) {
 auto q=(PFNEGLQUERYDEVICESEXTPROC)eglGetProcAddress("eglQueryDevicesEXT");auto g=(PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");if(!q||!g)error_exit("Missing EGL device extensions");EGLDeviceEXT devices[16];EGLint count=0;if(!q(16,devices,&count))error_exit("EGL device query failed");
 for(int i=0;i<count;i++){EGLDisplay d=g(EGL_PLATFORM_DEVICE_EXT,devices[i],0);if(eglInitialize(d,0,0)){const char*v=eglQueryString(d,EGL_VENDOR);if(v&&strstr(v,"NVIDIA")){eglDisplay=d;break;}eglTerminate(d);}}
 if(eglDisplay==EGL_NO_DISPLAY)error_exit("No NVIDIA hardware EGL device");if(!eglBindAPI(EGL_OPENGL_ES_API))error_exit("EGL ES bind failed");EGLint attrs[]={EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES3_BIT_KHR,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_ALPHA_SIZE,8,EGL_DEPTH_SIZE,24,EGL_NONE};EGLConfig cfg;EGLint n=0;if(!eglChooseConfig(eglDisplay,attrs,&cfg,1,&n)||!n)error_exit("EGL pbuffer config failed");EGLint pa[]={EGL_WIDTH,width,EGL_HEIGHT,height,EGL_NONE};eglSurface=eglCreatePbufferSurface(eglDisplay,cfg,pa);EGLint ca[]={EGL_CONTEXT_CLIENT_VERSION,3,EGL_NONE};eglContext=eglCreateContext(eglDisplay,cfg,EGL_NO_CONTEXT,ca);if(eglSurface==EGL_NO_SURFACE||eglContext==EGL_NO_CONTEXT||!eglMakeCurrent(eglDisplay,eglSurface,eglSurface,eglContext))error_exit("EGL ES pbuffer context failed");const char*v=(const char*)glGetString(GL_VENDOR);const char*r=(const char*)glGetString(GL_RENDERER);printf("EP_EGL_GL_VENDOR %s\nEP_EGL_GL_RENDERER %s\nEP_EGL_GL_VERSION %s\n",v,r,glGetString(GL_VERSION));if(!v||!strstr(v,"NVIDIA")||!r||!strstr(r,"4080"))error_exit("Not actual NVIDIA RTX4080 renderer");glViewport(0,0,width,height);return 1;
}

void graphics_set_windowtitle(const char *windowname) {
  (void)windowname;
}

void graphics_swap_buffers() { eglSwapBuffers(eglDisplay, eglSurface); }

void graphics_close_window() {
  if (eglDisplay != EGL_NO_DISPLAY) {
    eglMakeCurrent(eglDisplay, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);

    if (eglContext != EGL_NO_CONTEXT) eglDestroyContext(eglDisplay, eglContext);

    if (eglSurface != EGL_NO_SURFACE) eglDestroySurface(eglDisplay, eglSurface);

    eglTerminate(eglDisplay);
  }

  if (win) XDestroyWindow(display, win);

  XCloseDisplay(display);
}
