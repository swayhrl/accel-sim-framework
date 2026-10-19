// No GPU/model APIs; real glibc, clone, fork, system dash and cat.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>
static void* threadfn(void*) {return nullptr;}
int main(int argc,char**argv){
 const char* mode=argc>1?argv[1]:"normal";
 if(!strcmp(mode,"root_exit_child")){
  pid_t child=fork();if(child<0)return 11;
  if(child==0){usleep(500000);return 0;}
  return 0;
 }
 if(!strcmp(mode,"hang")){for(;;)sleep(1);}
 if(!strcmp(mode,"nonzero"))return 3;
 if(!strcmp(mode,"unknownexec")){execl("/usr/bin/true","true",nullptr);return 4;}
 if(!strcmp(mode,"unknownmap")||!strcmp(mode,"writablecache")){
  const char* path=!strcmp(mode,"unknownmap")?"/workspace/dtc-lane-ag6-aead-sixpoint-174-v1/build/unknown-data":"/etc/ld.so.cache";
  int fd=open(path,O_RDONLY);if(fd<0)return 5;
  void* p=mmap(nullptr,4096,PROT_READ|(!strcmp(mode,"writablecache")?PROT_WRITE:0),MAP_PRIVATE,fd,0);
  if(p==MAP_FAILED)return 6;munmap(p,4096);close(fd);return 0;
 }
 pthread_t t;if(pthread_create(&t,nullptr,threadfn,nullptr)||pthread_join(t,nullptr))return 7;
 int rounds=!strcmp(mode,"long")?28:2;
 for(int i=0;i<rounds;i++){
  FILE* f=popen("/usr/bin/cat /workspace/dtc-lane-ag6-aead-sixpoint-174-v1/build/helper-data","r");
  if(!f)return 8;char b[80]={};if(!fgets(b,sizeof(b),f))return 9;
  int s=pclose(f);if(!WIFEXITED(s)||WEXITSTATUS(s)||strcmp(b,"AG6_HELPER_OK\n"))return 10;
  if(!strcmp(mode,"long"))usleep(850000);
 }
 puts("AG6_CPU_ONLY_OK");return 0;
}
