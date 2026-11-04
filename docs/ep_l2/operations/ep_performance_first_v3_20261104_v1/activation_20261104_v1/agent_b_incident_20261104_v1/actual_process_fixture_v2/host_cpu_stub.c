#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
int main(int argc,char **argv) {
 const char *list=0;
 for(int i=1;i+1<argc;i++)if(!strcmp(argv[i],"-trace"))list=argv[i+1];
 if(!list)return 31;
 FILE *f=fopen(list,"rb");if(!f)return 32;
 char marker[1024],member[4096];
 if(!fgets(marker,sizeof(marker),f)||!fgets(member,sizeof(member),f))return 33;
 fclose(f);member[strcspn(member,"\r\n")]=0;
 if(strncmp(marker,"HOST_CPU_FIXTURE_DUMMY",21))return 34;
 f=fopen(member,"rb");if(!f)return 35;
 if(!fgets(marker,sizeof(marker),f))return 36;fclose(f);
 volatile unsigned char *mem=(volatile unsigned char *)malloc(16u<<20);if(!mem)return 37;for(unsigned n=0;n<(16u<<20);n+=4096)mem[n]=(unsigned char)n;
 printf("HOST_CPU_STUB_BEGIN|NOT_GPU_SIMULATOR=1|touched_bytes=16777216|pid=%ld\n",(long)getpid());fflush(stdout);
 for(int i=0;i<12;i++){
  printf("HOST_CPU_STUB_HEARTBEAT|ordinal=%d\n",i);fflush(stdout);
  struct timespec t={0,250000000};nanosleep(&t,0);
 }
 puts("HOST_CPU_STUB_EXIT|CPU_FIXTURE_COMPLETE=1|GPU_DRAIN_NOT_APPLICABLE=1");
 return 0;
}
