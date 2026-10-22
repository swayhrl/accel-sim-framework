#pragma once
// Test-only ownership adapter. Uses real GPU-constructed memory objects.
// No Tag/payload/observer mutation, shadow pool, scope rewrite or model API change.
struct tagpressure_owned_fixture_gpu : public exec_gpgpu_sim {
  tagpressure_owned_fixture_gpu(const gpgpu_sim_config&config,gpgpu_context*ctx)
    :exec_gpgpu_sim(config,ctx) {
    assert(!config.is_SST_mode());
    assert(getMemoryConfig()->m_n_mem==1);
    assert(getMemoryConfig()->m_n_sub_partition_per_memory_channel==1);
    assert(m_memory_partition_unit&&m_memory_partition_unit[0]&&m_memory_stats);
  }
  memory_partition_unit*fixture_partition(){return m_memory_partition_unit[0];}
  memory_stats_t*fixture_memory_stats(){return m_memory_stats;}
  ~tagpressure_owned_fixture_gpu(){
    // Production gpgpu_sim/exec_gpgpu_sim have no explicit destructor for these
    // raw arrays. This derived test object owns their actual allocations.
    // fixture holds BORROWED part/stats aliases and never separately deletes them.
    // Delete every partition/subpartition once before its shared stats, then raw
    // pointer arrays. Deleting through the typed derived pointer is mandatory.
    const unsigned count=getMemoryConfig()->m_n_mem;
    for(unsigned i=0;i<count;++i){delete m_memory_partition_unit[i];m_memory_partition_unit[i]=nullptr;}
    delete[] m_memory_partition_unit;m_memory_partition_unit=nullptr;
    delete[] m_memory_sub_partition;m_memory_sub_partition=nullptr;
    delete m_memory_stats;m_memory_stats=nullptr;
  }
};
