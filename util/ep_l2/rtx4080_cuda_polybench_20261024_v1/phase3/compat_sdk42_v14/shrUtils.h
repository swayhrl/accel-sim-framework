#pragma once
#include <stdio.h>
#include <stdarg.h>
#include <helper_functions.h>
#define LOGCONSOLE 1
#define LOGFILE 2
#define LOGBOTH 3
#define MASTER 4
inline void shrLog(const char *f,...){va_list a;va_start(a,f);vprintf(f,a);va_end(a);}
inline void shrLogEx(int,int,const char *f,...){va_list a;va_start(a,f);vprintf(f,a);va_end(a);}
inline void shrSetLogFileName(const char*){}
#define shrCheckCmdLineFlag(argc,argv,name) checkCmdLineFlag(argc,(const char**)(argv),name)

#ifndef CLAMP
#define CLAMP(v,lo,hi) ((v)<(lo)?(lo):((v)>(hi)?(hi):(v)))
#endif

#define shrFindFilePath sdkFindFilePath
inline bool shrGetCmdLineArgumenti(int argc,const char**argv,const char*key,int*out){if(!checkCmdLineFlag(argc,argv,key))return false;*out=getCmdLineArgumentInt(argc,argv,key);return true;}
inline bool shrGetCmdLineArgumentstr(int argc,const char**argv,const char*key,char**out){return getCmdLineArgumentString(argc,argv,key,out);}

#define ERRORMSG 16
#define shrLoadPPM4ub sdkLoadPPM4ub
#define shrFree free

#include <chrono>
inline double shrDeltaT(int i){static std::chrono::steady_clock::time_point t[16];if(i<0||i>=16)return 0.0;auto n=std::chrono::steady_clock::now();double x=std::chrono::duration<double>(n-t[i]).count();t[i]=n;return x;}

#include "ep_cuda_helpers.h"

#define shrCheckErrorEX(actual,expected,callback) do{if((actual)!=(expected)){fprintf(stderr,"SHR_CHECK_ERROR_FAILED %s\n",#actual);exit(1);}}while(0)

#define CLOSELOG 0
#define shrEXIT(argc,argv) exit(EXIT_SUCCESS)
