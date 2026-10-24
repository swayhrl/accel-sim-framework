#include <signal.h>
#include <stdio.h>
#include <dlfcn.h>
int main(){ puts("FIRST_ISSUE");fflush(stdout);raise(SIGSTOP);void *h=dlopen("libm.so.6",RTLD_NOW);if(!h)return 5;puts("TERMINAL");fflush(stdout);raise(SIGSTOP);dlclose(h);return 0;}
