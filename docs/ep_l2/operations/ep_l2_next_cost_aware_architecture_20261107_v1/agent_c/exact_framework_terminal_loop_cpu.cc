#include <vector>
#include <string>
#include <iostream>
#include <cstdio>
#include <cassert>
struct Kernel {bool started=false;unsigned get_cuda_stream_id(){return 0;}bool was_launched(){return started;}void set_launched(){started=true;}const char*get_name(){return"fake";}unsigned get_uid(){return 1;}};
struct GPU {
 bool timed=true,work=false,cleanup=false,done=false;unsigned ticks=0,left=0,requests=0,final_prints=0;
 bool active(){return work||cleanup;}bool can_start_kernel(){return true;}
 void launch(Kernel*){work=true;}
 bool cycle_insn_cta_max_hit(){return false;}
 void update_stats(){}void ro_end_epoch(){}
 void quota_request_terminal_cleanup(){if(timed&&!done&&!cleanup){cleanup=true;left=3;++requests;}}
 void quota_print_terminal_contract(){if(timed&&(!done||cleanup||ticks!=4))throw 1;}
 void print_stats(unsigned long long){if(timed&&(!done||ticks!=4))throw 2;++final_prints;}
};
struct Context{void print_simulation_time(){}};
class accel_sim_framework {
 public:
 GPU* m_gpgpu_sim;Context* m_gpgpu_context;unsigned commandlist_index=0;
 std::vector<int>commandlist{1};std::vector<Kernel*>kernels_info;std::vector<unsigned>busy_streams;
 bool sim_cycles=false,ro_epoch_started=false;Kernel kernel;
 void parse_commandlist(){if(commandlist_index==0){commandlist_index=1;kernels_info.push_back(&kernel);}}
 unsigned simulate(){
  if(m_gpgpu_sim->work){m_gpgpu_sim->work=false;++m_gpgpu_sim->ticks;sim_cycles=true;return 1;}
  while(m_gpgpu_sim->cleanup){++m_gpgpu_sim->ticks;sim_cycles=true;if(!--m_gpgpu_sim->left){m_gpgpu_sim->cleanup=false;m_gpgpu_sim->done=true;}}
  return 0;
 }
 void cleanup(unsigned){kernels_info.clear();}
 void simulation_loop();
};
void accel_sim_framework::simulation_loop() {
  // for each kernel
  // load file
  // parse and create kernel info
  // launch
  // while loop till the end of the end kernel execution
  // prints stats

  // A finished CTA/kernel can leave no source-side work while lower-memory
  // traffic (notably no-return L2 writebacks) is still draining.  Keep the
  // framework clocking that production backend until active() reports that
  // all credits and queues are clear.
  while (commandlist_index < commandlist.size() || !kernels_info.empty() ||
         m_gpgpu_sim->active()) {
    parse_commandlist();

    // Launch all kernels within window that are on a stream that isn't already
    // running
    for (auto k : kernels_info) {
      bool stream_busy = false;
      for (auto s : busy_streams) {
        if (s == k->get_cuda_stream_id()) stream_busy = true;
      }
      if (!stream_busy && m_gpgpu_sim->can_start_kernel() &&
          !k->was_launched()) {
        std::cout << "launching kernel name: " << k->get_name()
                  << " uid: " << k->get_uid()
                  << " cuda_stream_id: " << k->get_cuda_stream_id()
                  << std::endl;
        m_gpgpu_sim->launch(k);
        k->set_launched();
        busy_streams.push_back(k->get_cuda_stream_id());
      }
    }

    unsigned finished_kernel_uid = simulate();
    // cleanup finished kernel
    if (!kernels_info.empty() &&
        (finished_kernel_uid || m_gpgpu_sim->cycle_insn_cta_max_hit() ||
         !m_gpgpu_sim->active())) {
      cleanup(finished_kernel_uid);
    }

    if (sim_cycles) {
      m_gpgpu_sim->update_stats();
      m_gpgpu_context->print_simulation_time();
    }

    if (m_gpgpu_sim->cycle_insn_cta_max_hit()) {
      printf(
          "GPGPU-Sim: ** break due to reaching the maximum cycles (or "
          "instructions) **\n");
      fflush(stdout);
      break;
    }
    if(commandlist_index==commandlist.size()&&kernels_info.empty())
      m_gpgpu_sim->quota_request_terminal_cleanup();
  }

  // cleanup() reports a completed kernel as soon as its CTA work retires.
  // Emit one final snapshot after the backend drain so closeout checks see
  // the actual terminal resource and credit state.
  // A capped/aborted run never receives a completed-epoch marker.
  if (ro_epoch_started && !m_gpgpu_sim->cycle_insn_cta_max_hit()) {
    m_gpgpu_sim->ro_end_epoch();
    printf("EPL2ROV1|COMMANDLIST_END|complete=1|commands=%zu\n", commandlist.size());
  }
  if(!m_gpgpu_sim->cycle_insn_cta_max_hit())m_gpgpu_sim->quota_print_terminal_contract();
  if (sim_cycles && !m_gpgpu_sim->cycle_insn_cta_max_hit())
    m_gpgpu_sim->print_stats(~0ULL);
}

int main() {
 GPU gpu;Context context;accel_sim_framework f;f.m_gpgpu_sim=&gpu;f.m_gpgpu_context=&context;
 f.simulation_loop();
 if(gpu.ticks!=4||gpu.requests!=1||gpu.final_prints!=1||!gpu.done)return 9;
 puts("PASS EXACT_FRAMEWORK_LOOP_CLOCKS_TERMINAL_BEFORE_FINAL_SNAPSHOT");
 GPU legacy;legacy.timed=false;accel_sim_framework g;g.m_gpgpu_sim=&legacy;g.m_gpgpu_context=&context;g.simulation_loop();
 if(legacy.ticks!=1||legacy.requests||legacy.final_prints!=1)return 10;
 puts("PASS LEGACY_MODE_NO_ADDED_TERMINAL_WORK");
}
