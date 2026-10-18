// CPU-only real system-loader/thread/popen fixture, no simulator APIs or trace.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>
static void* thread_fn(void*) { std::puts("AG3_CPU_THREAD"); return nullptr; }
int main(int argc,char**argv) {
  if(argc>1 && !std::strcmp(argv[1],"hang")){for(;;)sleep(1);}
  if(argc>1 && !std::strcmp(argv[1],"unknown")) {
    int fd=open("/workspace/dtc-lane-ag3-aead-screen-174-v1/build/cpu-unregistered-data",O_RDONLY);
    if(fd<0)return 71;void* p=mmap(nullptr,4096,PROT_READ,MAP_PRIVATE,fd,0);
    if(p==MAP_FAILED)return 72;munmap(p,4096);close(fd);return 0;
  }
  if(argc>1 && !std::strcmp(argv[1],"writablecache")) {
    int fd=open("/etc/ld.so.cache",O_RDONLY);if(fd<0)return 73;
    void* p=mmap(nullptr,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE,fd,0);
    if(p==MAP_FAILED)return 74;munmap(p,4096);close(fd);return 0;
  }
  pthread_t t;if(pthread_create(&t,nullptr,thread_fn,nullptr))return 75;
  if(pthread_join(t,nullptr))return 76;
  FILE* p=popen("/usr/bin/cat /workspace/dtc-lane-ag3-aead-screen-174-v1/build/cpu-helper-data","r");
  if(!p)return 77;char buf[128]={};if(!fgets(buf,sizeof(buf),p))return 78;
  int status=pclose(p);if(!WIFEXITED(status)||WEXITSTATUS(status)!=0)return 79;
  if(std::strcmp(buf,"AG3_CPU_HELPER_OK\n"))return 80;
  std::puts("AG3_CPU_PRODUCTION_WRAPPER_OK no_GPU no_trace no_model_cycle");return 0;
}
