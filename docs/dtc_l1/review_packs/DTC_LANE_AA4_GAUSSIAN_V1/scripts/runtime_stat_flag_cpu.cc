#include <cstdio>
#include <cassert>
int main(){ const char *gpgpu_runtime_stat="500000"; int gpu_stat_sample_freq; unsigned gpu_runtime_stat_flag;
gpu_stat_sample_freq = 10000;
    gpu_runtime_stat_flag = 0;
    sscanf(gpgpu_runtime_stat, "%d:%x", &gpu_stat_sample_freq,
           &gpu_runtime_stat_flag);
std::printf("freq=%d flag=%u L1MISS_enabled=%u\n",gpu_stat_sample_freq,gpu_runtime_stat_flag,(gpu_runtime_stat_flag&0x10)!=0);assert(gpu_stat_sample_freq==500000 && gpu_runtime_stat_flag==0);return 0;}
