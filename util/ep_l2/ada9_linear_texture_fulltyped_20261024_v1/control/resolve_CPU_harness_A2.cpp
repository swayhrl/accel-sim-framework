#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/syscall.h>
#include "nvbit.h"
std::string user_folder="/unused_CPU_only";
#include "linear_texture_resource_v1.h"
int main(int argc,char**argv){std::string t=argv[1];ada9_tex.live=true;ada9_tex.creates=1;ada9_tex.generation=1;ada9_tex.base=0x1000;ada9_tex.bytes=512;ada9_tex.handle=1;uint64_t pair=(uint64_t(1)<<32)|3;
 if(t=="valid127")pair=(uint64_t(1)<<32)|127;
 else if(t=="negative")pair=(uint64_t(1)<<32)|0xffffffffULL;
 else if(t=="oob")pair=(uint64_t(1)<<32)|128;
 else if(t=="wrong_handle")pair=(uint64_t(2)<<32)|3;
 else if(t=="handle_high")ada9_tex.handle=0x100000001ULL;
 else if(t=="overflow")ada9_tex.base=UINT64_MAX-511;
 else if(t=="dead")ada9_tex.live=false;
 else if(t=="generation2")ada9_tex.generation=2;
 auto result=ada9_resolve_texture(pair);printf("%llx\n",(unsigned long long)result);return result==(t=="valid127"?0x11fc:0x100c)?0:2;}
