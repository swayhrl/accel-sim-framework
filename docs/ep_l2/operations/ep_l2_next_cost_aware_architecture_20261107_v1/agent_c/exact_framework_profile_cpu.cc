#include <vector>
#include <stdexcept>
#include <cstdio>
enum class command_type{cpu_gpu_mem_copy,kernel_launch,unknown};
struct Command{command_type m_type;};
struct GPU{bool quota_timing_enabled(){return true;}};
void validate(const std::vector<Command>&commandlist){GPU gpu;auto*m_gpgpu_sim=&gpu;
    if(m_gpgpu_sim->quota_timing_enabled()) {
      bool seen_kernel=false;
      for(const auto&command:commandlist) {
        if(command.m_type==command_type::kernel_launch)seen_kernel=true;
        else if(command.m_type==command_type::cpu_gpu_mem_copy) {
          if(seen_kernel)throw std::invalid_argument("timed CLEAN profile forbids memcpy after first kernel");
        } else throw std::invalid_argument("unknown command in timed CLEAN profile");
      }
      if(!seen_kernel)throw std::invalid_argument("timed CLEAN profile requires a kernel command");
    }
}
int main(){
 validate({{command_type::cpu_gpu_mem_copy},{command_type::kernel_launch},{command_type::kernel_launch}});
 unsigned refused=0;
 for(const auto&x:std::vector<std::vector<Command>>{{{command_type::kernel_launch},{command_type::cpu_gpu_mem_copy}},{{command_type::cpu_gpu_mem_copy}},{{command_type::unknown}}}){
  try{validate(x);}catch(const std::invalid_argument&){++refused;}
 }
 if(refused!=3)return 1;puts("PASS EXACT_INPUT_PROFILE_INIT_COPIES_ONLY_AND_THREE_EARLY_REJECTIONS");
}
