#pragma once
#include <GL/freeglut.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
namespace ep_egl {
static EGLDisplay d=EGL_NO_DISPLAY;static EGLSurface s=EGL_NO_SURFACE;static EGLContext c=EGL_NO_CONTEXT;static int w=512,h=512;
static void check(bool ok,const char*op){if(!ok){fprintf(stderr,"EP_EGL_FAILURE %s 0x%x\n",op,eglGetError());exit(81);}}
static void init(int*,char**){}
static void size(int x,int y){w=x;h=y;}
static int create(const char*){
 auto q=(PFNEGLQUERYDEVICESEXTPROC)eglGetProcAddress("eglQueryDevicesEXT");auto g=(PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");check(q&&g,"entrypoints");EGLDeviceEXT ds[16];EGLint n=0;check(q(16,ds,&n),"devices");EGLint ma,mi;
 for(int i=0;i<n;i++){EGLDisplay candidate=g(EGL_PLATFORM_DEVICE_EXT,ds[i],0);if(eglInitialize(candidate,&ma,&mi)){const char*v=eglQueryString(candidate,EGL_VENDOR);if(v&&strstr(v,"NVIDIA")){d=candidate;break;}eglTerminate(candidate);}}
 check(d!=EGL_NO_DISPLAY,"NVIDIA display");check(eglBindAPI(EGL_OPENGL_API),"OpenGL API");EGLint ca[]={EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_ALPHA_SIZE,8,EGL_DEPTH_SIZE,24,EGL_NONE};EGLConfig cfg;EGLint nc;check(eglChooseConfig(d,ca,&cfg,1,&nc)&&nc,"config");EGLint pa[]={EGL_WIDTH,w,EGL_HEIGHT,h,EGL_NONE};s=eglCreatePbufferSurface(d,cfg,pa);check(s!=EGL_NO_SURFACE,"pbuffer");c=eglCreateContext(d,cfg,EGL_NO_CONTEXT,0);check(c!=EGL_NO_CONTEXT,"context");check(eglMakeCurrent(d,s,s,c),"makeCurrent");const char*v=(const char*)glGetString(GL_VENDOR);const char*r=(const char*)glGetString(GL_RENDERER);printf("EP_EGL_GL_VENDOR %s\nEP_EGL_GL_RENDERER %s\nEP_EGL_GL_VERSION %s\n",v,r,glGetString(GL_VERSION));check(v&&strstr(v,"NVIDIA")&&r&&strstr(r,"4080"),"real RTX4080 renderer");glViewport(0,0,w,h);return 1;}
static void destroy(int){if(d!=EGL_NO_DISPLAY){eglMakeCurrent(d,EGL_NO_SURFACE,EGL_NO_SURFACE,EGL_NO_CONTEXT);eglDestroyContext(d,c);eglDestroySurface(d,s);eglTerminate(d);d=EGL_NO_DISPLAY;}}
static void swap(){check(eglSwapBuffers(d,s),"swap");}
static void(*display_cb)()=nullptr; static void(*reshape_cb)(int,int)=nullptr; static void mode(unsigned int){} static void display(void(*p)(void)){display_cb=p;}static void keyboard(void(*)(unsigned char,int,int)){}static void mouse(void(*)(int,int,int,int)){}static void motion(void(*)(int,int)){}static void reshape(void(*p)(int,int)){reshape_cb=p;}static void close(void(*)(void)){}static void post(){}static void title(const char*){}static int window(){return 1;}static void timer(unsigned int,void(*)(int),int){} static int menu(void(*)(int)){return 1;} static void entry(const char*,int){} static void attach(int){} static void mainloop(){if(reshape_cb)reshape_cb(w,h);for(int frame=0;frame<10;frame++){check(display_cb!=nullptr,"display callback");display_cb();}fprintf(stderr,"EP_EGL_FAILURE original QA did not terminate within 10 display callbacks\n");exit(82);}
}
#define glutInit ep_egl::init
#define glutInitWindowSize ep_egl::size
#define glutCreateWindow ep_egl::create
#define glutDestroyWindow ep_egl::destroy
#define glutInitDisplayMode ep_egl::mode
#define glutSwapBuffers ep_egl::swap
#define glutDisplayFunc ep_egl::display
#define glutKeyboardFunc ep_egl::keyboard
#define glutMouseFunc ep_egl::mouse
#define glutMotionFunc ep_egl::motion
#define glutReshapeFunc ep_egl::reshape
#define glutCloseFunc ep_egl::close
#define glutWMCloseFunc ep_egl::close
#define glutPostRedisplay ep_egl::post
#define glutSetWindowTitle ep_egl::title
#define glutGetWindow ep_egl::window
#define glutMainLoop ep_egl::mainloop

extern "C" void ep_glutSolidTeapot(double);
#define glutSolidTeapot ep_glutSolidTeapot
#define glutTimerFunc ep_egl::timer
#define glutCreateMenu ep_egl::menu
#define glutAddMenuEntry ep_egl::entry
#define glutAttachMenu ep_egl::attach
