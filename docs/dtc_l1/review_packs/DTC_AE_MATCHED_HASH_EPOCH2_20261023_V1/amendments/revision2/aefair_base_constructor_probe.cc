// Directed CPU construction only. No kernel, trace replay, model cycle or thread.
#include "gpgpu-sim/gpu-sim.h"
#include "gpgpu-sim/shader.h"
#include "gpgpu-sim/icnt_wrapper.h"
#include "gpgpu_context.h"
#include "gpgpusim_entrypoint.h"
#include "option_parser.h"
#include <cassert>
#include <cstdio>
#include <ctime>
#include <csignal>
#include <sys/resource.h>
int main(int argc,const char**argv) {
 assert(argc==3);rlimit lim{0,0};setrlimit(RLIMIT_CORE,&lim);
 gpgpu_context ctx;gpgpu_sim_config cfg(&ctx);auto parser=option_parser_create();
 cfg.reg_options(parser);icnt_reg_options(parser);ctx.ptx_reg_options(parser);ctx.func_sim->ptx_opcocde_latency_options(parser);
 char path[1024];
 for(unsigned i: {0U,1U,3U}) {std::snprintf(path,sizeof(path),"%s/config-%u.config",argv[1],i);option_parser_cfgfile(parser,path);}
 const char*opts[]={"AEFAIR_BASE_CTOR_CPU","-gpgpu_n_clusters","1","-gpgpu_n_cores_per_cluster","1","-gpgpu_n_mem","1","-gpgpu_n_sub_partition_per_mchannel","1","-gpgpu_shader_core_pipeline","64:32","-gpgpu_shader_cta","2","-gpgpu_smem_latency","2","-network_mode","2","-gpgpu_memory_partition_indexing","0","-power_simulation_enabled","0","-visualizer_enabled","0","-gpgpu_dtc_l1_finite_service",argv[2]};
 option_parser_cmdline(parser,sizeof(opts)/sizeof(opts[0]),opts);cfg.init();ctx.the_gpgpusim->g_simulation_starttime=std::time(nullptr);
 std::printf("CPU_CONFIG mode=%u finite=%u pib=%u mshr=%u sets=%u lines=%u dataKiB=%u\n",cfg.m_shader_config.dtc_l1_mode,cfg.m_shader_config.dtc_l1_finite_service,cfg.m_shader_config.dtc_l1_pib_entries,cfg.m_shader_config.dtc_l1_mshr_entries,cfg.m_shader_config.m_L1D_config.get_nset(),cfg.m_shader_config.m_L1D_config.get_num_lines(),cfg.m_shader_config.m_L1D_config.get_total_size_inKB());std::fflush(stdout);
 std::signal(SIGABRT,SIG_DFL);
 auto*gpu=new exec_gpgpu_sim(cfg,&ctx);gpu->init();
 auto*core=gpu->get_simt_core_clusters()[0]->get_shader_cores()[0];auto*ld=core->m_ldst_unit;
 assert(cfg.m_shader_config.dtc_l1_mode==1 && !cfg.m_shader_config.dtc_l1_finite_service);
 assert(ld->dtc_l1_paper_base_active() && !ld->dtc_l1_finite_service_active());
 assert(ld->m_L1D && !ld->m_dtc_l1_io_frontend && !ld->m_dtc_l1_oo_frontend);
 assert(ld->m_dtc_l1_frontend->m_cfg.pib_entries==256);
 assert(cfg.m_shader_config.m_L1D_config.get_nset()==32 && cfg.m_shader_config.m_L1D_config.get_num_lines()==768);
 assert(cfg.m_shader_config.m_L1D_config.get_mshr_entries()==512 && cfg.m_shader_config.m_L1D_config.get_total_size_inKB()==96);
 assert(cfg.m_shader_config.m_L1D_config.l1_banks==4 && cfg.m_shader_config.m_L1D_config.l1_latency==20);
 assert(gpu->gpu_sim_cycle==0 && gpu->gpu_tot_sim_cycle==0);
 std::puts("PASS_REAL_PAPER_BASE_CONSTRUCTOR standard_finite_cache_resources=preserved DTC_only_finite_flag=0 kernels=0 trace_members_read=0 model_cycle_calls=0 simulation_threads_started=0");
}
