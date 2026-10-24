#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <pthread.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

/* Extract-only interposer. Redirect listed, truncating output names to unique files.
 * Never use on a workload, simulator, or a nonempty extraction directory. */
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static unsigned ordinal;
static int redirect_output(const char *path, int dirfd, char out[PATH_MAX]) {
    const char *root = getenv("EP_CUBIN_OUTPUT_ROOT");
    const char *allowed = getenv("EP_CUBIN_ALLOWED_BASENAMES");
    const char *base = strrchr(path, '/'); base = base ? base + 1 : path;
    if (!root || !allowed) { errno = EPERM; return -1; }
    size_t n = strlen(base);
    int listed = 0;
    for (const char *p = allowed; *p;) {
        const char *end = strchr(p, ':'); if (!end) end = p + strlen(p);
        if ((size_t)(end-p) == n && !strncmp(p, base, n)) listed = 1;
        p = *end ? end+1 : end;
    }
    if (!listed) return 0;
    /* Unsupported path forms or cwd changes fail closed for a listed output. */
    const char *simple = path;
    if (!strncmp(simple, "./", 2)) simple += 2;
    if (strchr(simple, '/') || strcmp(simple, base)) { errno=EPERM; return -1; }
    struct stat actual, expected;
    if (stat(root, &expected) || fstatat(dirfd, ".", &actual, 0) ||
        actual.st_dev != expected.st_dev || actual.st_ino != expected.st_ino) {
        errno=EPERM; return -1;
    }
    pthread_mutex_lock(&mu);
    unsigned k = ++ordinal;
    int len = snprintf(out, PATH_MAX, "%s/image_%06u__%s", root, k, base);
    struct stat st;
    int absent = (len > 0 && len < PATH_MAX && lstat(out, &st) && errno == ENOENT);
    pthread_mutex_unlock(&mu);
    if (!absent) { errno=EEXIST; return -1; }
    return 1;
}

FILE *fopen(const char *p, const char *mode) {
    static FILE *(*real)(const char *,const char *);
    if (!real) real=dlsym(RTLD_NEXT,"fopen");
    char out[PATH_MAX]; int r=0;
    if (strchr(mode,'w')) r=redirect_output(p,AT_FDCWD,out);
    if (r<0) return NULL;
    return real(r ? out : p, mode);
}
FILE *fopen64(const char *p, const char *mode) {
    static FILE *(*real)(const char *,const char *);
    if (!real) real=dlsym(RTLD_NEXT,"fopen64");
    char out[PATH_MAX]; int r=0;
    if (strchr(mode,'w')) r=redirect_output(p,AT_FDCWD,out);
    if (r<0) return NULL;
    return real(r ? out : p, mode);
}
#define OPEN_HOOK(NAME) \
int NAME(const char *p, int flags, ...) { \
    static int (*real)(const char *,int,...); \
    if (!real) real=dlsym(RTLD_NEXT,#NAME); \
    mode_t mode=0; if (flags&O_CREAT) { va_list ap;va_start(ap,flags);mode=va_arg(ap,int);va_end(ap); } \
    char out[PATH_MAX];int r=(flags&O_TRUNC)?redirect_output(p,AT_FDCWD,out):0; \
    if(r<0) { return -1; } return real(r?out:p,flags,mode); \
}
OPEN_HOOK(open)
OPEN_HOOK(open64)
#define OPENAT_HOOK(NAME) \
int NAME(int fd,const char *p,int flags,...) { \
    static int (*real)(int,const char *,int,...); \
    if(!real)real=dlsym(RTLD_NEXT,#NAME); \
    mode_t mode=0;if(flags&O_CREAT){va_list ap;va_start(ap,flags);mode=va_arg(ap,int);va_end(ap);} \
    char out[PATH_MAX];int r=(flags&O_TRUNC)?redirect_output(p,fd,out):0; \
    if(r<0) { return -1; } return real(r?AT_FDCWD:fd,r?out:p,flags,mode); \
}
OPENAT_HOOK(openat)
OPENAT_HOOK(openat64)
int creat(const char *p,mode_t mode){return open(p,O_WRONLY|O_CREAT|O_TRUNC,mode);}
int creat64(const char *p,mode_t mode){return open64(p,O_WRONLY|O_CREAT|O_TRUNC,mode);}
