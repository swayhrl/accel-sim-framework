#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdarg.h>
#include <string.h>
#include <stdatomic.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
static _Atomic unsigned ordinal=0;
static const char *route(const char *path, char *buf, size_t cap) {
 const char *s=path;
 if(!strncmp(s,"./",2))s+=2;
 size_t n=strlen(s);
 if(strchr(s,'/') || n<7 || strcmp(s+n-6,".cubin"))return path;
 unsigned k=atomic_fetch_add(&ordinal,1)+1;
 if(snprintf(buf,cap,"%06u__%s",k,s)>=(int)cap){errno=ENAMETOOLONG;return NULL;}
 return buf;
}
FILE *fopen(const char *path,const char *mode) {
 static FILE *(*real)(const char*,const char*);
 if(!real)real=dlsym(RTLD_NEXT,"fopen");
 char b[4096];const char *p=strpbrk(mode,"wa")?route(path,b,sizeof(b)):path;
 return p?real(p,mode):NULL;
}
FILE *fopen64(const char *path,const char *mode) {
 static FILE *(*real)(const char*,const char*);
 if(!real)real=dlsym(RTLD_NEXT,"fopen64");
 char b[4096];const char *p=strpbrk(mode,"wa")?route(path,b,sizeof(b)):path;
 return p?real(p,mode):NULL;
}
int open(const char *path,int flags,...) {
 static int (*real)(const char*,int,...);
 if(!real)real=dlsym(RTLD_NEXT,"open");
 mode_t mode=0;if(flags&O_CREAT){va_list a;va_start(a,flags);mode=va_arg(a,int);va_end(a);}
 char b[4096];const char *p=(flags&O_CREAT)?route(path,b,sizeof(b)):path;
 return p?real(p,flags,mode):-1;
}
int open64(const char *path,int flags,...) {
 static int (*real)(const char*,int,...);
 if(!real)real=dlsym(RTLD_NEXT,"open64");
 mode_t mode=0;if(flags&O_CREAT){va_list a;va_start(a,flags);mode=va_arg(a,int);va_end(a);}
 char b[4096];const char *p=(flags&O_CREAT)?route(path,b,sizeof(b)):path;
 return p?real(p,flags,mode):-1;
}
