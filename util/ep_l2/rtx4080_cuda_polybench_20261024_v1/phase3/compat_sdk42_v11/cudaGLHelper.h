#pragma once
#include <cutil_gl_inline.h>
inline bool sdkCheckErrorGL(const char*file,int line){GLenum e=glGetError();if(e!=GL_NO_ERROR){fprintf(stderr,"GL_ERROR %s:%d code=%u\n",file,line,(unsigned)e);return false;}return true;}
#define SDK_CHECK_ERROR_GL() do{if(!sdkCheckErrorGL(__FILE__,__LINE__))exit(1);}while(0)
