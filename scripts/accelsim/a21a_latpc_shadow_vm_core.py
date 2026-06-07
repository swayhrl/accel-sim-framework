#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import NESTED_ROOT, REPORT_DIR, clean, ensure_dirs, latest, read_csv, rel, stage_report, ts, write_csv

HEADER = NESTED_ROOT / "src/gpgpu-sim/latpc_shadow_vm.h"

HEADER_TEXT = r'''#ifndef LATPC_SHADOW_VM_H
#define LATPC_SHADOW_VM_H

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <set>
#include <vector>

class latpc_shadow_vm_t {
 public:
  latpc_shadow_vm_t() : m_initialized(false), m_enabled(false), m_event_cycle(0), m_lru_clock(0) {}

  void init_from_env() {
    if (m_initialized) return;
    m_initialized = true;
    m_enabled = env_flag("ACCELSIM_LATPC_SHADOW_VM", false);
    m_page_shift = env_uint("ACCELSIM_LATPC_SHADOW_PAGE_SHIFT", 12);
    m_l1_entries = env_uint("ACCELSIM_LATPC_SHADOW_L1_ENTRIES", 32);
    m_l2_entries = env_uint("ACCELSIM_LATPC_SHADOW_L2_ENTRIES", 1024);
    m_l1_mshr_entries = env_uint("ACCELSIM_LATPC_SHADOW_L1_MSHR_ENTRIES", 16);
    m_l2_mshr_entries = env_uint("ACCELSIM_LATPC_SHADOW_L2_MSHR_ENTRIES", 128);
    m_ptw_count = env_uint("ACCELSIM_LATPC_SHADOW_PTW_COUNT", 16);
    m_pwq_entries = env_uint("ACCELSIM_LATPC_SHADOW_PWQ_ENTRIES", 128);
    m_ptw_latency = env_uint("ACCELSIM_LATPC_SHADOW_PTW_LATENCY", 300);
    m_pwc_enable = env_flag("ACCELSIM_LATPC_SHADOW_PWC_ENABLE", false);
    if (m_l1_entries == 0) m_l1_entries = 1;
    if (m_l2_entries == 0) m_l2_entries = 1;
    if (m_ptw_count == 0) m_ptw_count = 1;
    if (m_pwq_entries == 0) m_pwq_entries = 1;
    m_l1.resize(m_l1_entries);
    m_l2.resize(m_l2_entries);
    m_walkers.assign(m_ptw_count, 0);
  }

  bool enabled() {
    init_from_env();
    return m_enabled;
  }

  void observe_warp_addresses(unsigned sm_id, unsigned warp_id, unsigned long long pc,
                              unsigned long long cycle, const unsigned long long *addrs,
                              unsigned count) {
    (void)sm_id;
    (void)warp_id;
    (void)pc;
    init_from_env();
    if (!m_enabled) return;
    m_stats.observe_call_total++;
    unsigned long long now = cycle ? cycle : ++m_event_cycle;
    drain_until(now);
    if (count == 0) {
      m_stats.empty_address_observe_total++;
      return;
    }
    std::vector<unsigned long long> vpns;
    std::set<unsigned long long> seen;
    for (unsigned i = 0; i < count; ++i) {
      unsigned long long addr = addrs[i];
      if (addr == 0) continue;
      unsigned long long vpn = addr >> m_page_shift;
      if (seen.insert(vpn).second) vpns.push_back(vpn);
    }
    if (vpns.empty()) {
      m_stats.empty_address_observe_total++;
      return;
    }
    m_stats.warp_mem_inst_observed++;
    m_stats.translation_request_total += vpns.size();
    for (size_t i = 0; i < vpns.size(); ++i) m_unique_vpns.insert(vpns[i]);
    update_divergence(vpns.size());
    update_stride_and_l4(vpns);
    for (size_t i = 0; i < vpns.size(); ++i) process_vpn(vpns[i], now);
  }

  void print_stats(FILE *f) {
    init_from_env();
    if (!m_enabled) return;
    drain_until(~0ULL / 4);
    std::fprintf(f, "latpc_shadow_vm_enabled = 1\n");
    std::fprintf(f, "latpc_shadow_vm_version = 1\n");
    std::fprintf(f, "latpc_shadow_page_shift = %u\n", m_page_shift);
    std::fprintf(f, "latpc_shadow_l1_entries = %u\n", m_l1_entries);
    std::fprintf(f, "latpc_shadow_l2_entries = %u\n", m_l2_entries);
    std::fprintf(f, "latpc_shadow_l1_mshr_entries = %u\n", m_l1_mshr_entries);
    std::fprintf(f, "latpc_shadow_l2_mshr_entries = %u\n", m_l2_mshr_entries);
    std::fprintf(f, "latpc_shadow_ptw_count = %u\n", m_ptw_count);
    std::fprintf(f, "latpc_shadow_pwq_entries = %u\n", m_pwq_entries);
    std::fprintf(f, "latpc_shadow_ptw_latency = %u\n", m_ptw_latency);
    std::fprintf(f, "latpc_shadow_pwc_enabled = %u\n", m_pwc_enable ? 1 : 0);
    std::fprintf(f, "latpc_shadow_observe_call_total = %llu\n", m_stats.observe_call_total);
    std::fprintf(f, "latpc_shadow_empty_address_observe_total = %llu\n", m_stats.empty_address_observe_total);
    std::fprintf(f, "latpc_shadow_duplicate_observation_warning_total = %llu\n", m_stats.duplicate_observation_warning_total);
    std::fprintf(f, "latpc_shadow_dropped_due_to_mshr_full_total = %llu\n", m_stats.dropped_due_to_mshr_full_total);
    std::fprintf(f, "latpc_shadow_dropped_due_to_pwq_full_total = %llu\n", m_stats.dropped_due_to_pwq_full_total);
    std::fprintf(f, "latpc_vm_warp_mem_inst_observed = %llu\n", m_stats.warp_mem_inst_observed);
    std::fprintf(f, "latpc_vm_translation_request_total = %llu\n", m_stats.translation_request_total);
    std::fprintf(f, "latpc_vm_unique_vpn_total = %llu\n", (unsigned long long)m_unique_vpns.size());
    std::fprintf(f, "latpc_vm_page_div_bin_1 = %llu\n", m_stats.page_div_bin_1);
    std::fprintf(f, "latpc_vm_page_div_bin_2_3 = %llu\n", m_stats.page_div_bin_2_3);
    std::fprintf(f, "latpc_vm_page_div_bin_4_7 = %llu\n", m_stats.page_div_bin_4_7);
    std::fprintf(f, "latpc_vm_page_div_bin_8_15 = %llu\n", m_stats.page_div_bin_8_15);
    std::fprintf(f, "latpc_vm_page_div_bin_16_31 = %llu\n", m_stats.page_div_bin_16_31);
    std::fprintf(f, "latpc_vm_page_div_bin_32 = %llu\n", m_stats.page_div_bin_32);
    std::fprintf(f, "latpc_vm_unique_stride_sample_total = %llu\n", m_stats.unique_stride_sample_total);
    std::fprintf(f, "latpc_vm_unique_stride_sum = %llu\n", m_stats.unique_stride_sum);
    std::fprintf(f, "latpc_vm_same_l4pt_translation_total = %llu\n", m_stats.same_l4pt_translation_total);
    std::fprintf(f, "latpc_vm_l4pt_translation_total = %llu\n", m_stats.l4pt_translation_total);
    std::fprintf(f, "latpc_tlb_l1_access_total = %llu\n", m_stats.l1_access);
    std::fprintf(f, "latpc_tlb_l1_hit_total = %llu\n", m_stats.l1_hit);
    std::fprintf(f, "latpc_tlb_l1_miss_total = %llu\n", m_stats.l1_miss);
    std::fprintf(f, "latpc_tlb_l2_access_total = %llu\n", m_stats.l2_access);
    std::fprintf(f, "latpc_tlb_l2_hit_total = %llu\n", m_stats.l2_hit);
    std::fprintf(f, "latpc_tlb_l2_miss_total = %llu\n", m_stats.l2_miss);
    std::fprintf(f, "latpc_tlb_l1_mshr_alloc_attempt = %llu\n", m_stats.l1_mshr_alloc_attempt);
    std::fprintf(f, "latpc_tlb_l1_mshr_alloc_success = %llu\n", m_stats.l1_mshr_alloc_success);
    std::fprintf(f, "latpc_tlb_l1_mshr_reservation_fail = %llu\n", m_stats.l1_mshr_reservation_fail);
    std::fprintf(f, "latpc_tlb_l1_mshr_hit_under_miss = %llu\n", m_stats.l1_mshr_hit_under_miss);
    std::fprintf(f, "latpc_ptw_request_total = %llu\n", m_stats.ptw_request_total);
    std::fprintf(f, "latpc_ptw_queue_enqueue_total = %llu\n", m_stats.ptw_queue_enqueue_total);
    std::fprintf(f, "latpc_ptw_queue_full_event_total = %llu\n", m_stats.ptw_queue_full_event_total);
    std::fprintf(f, "latpc_ptw_queue_shadow_stall_cycle_total = %llu\n", m_stats.ptw_queue_shadow_stall_cycle_total);
    std::fprintf(f, "latpc_ptw_walk_issue_total = %llu\n", m_stats.ptw_walk_issue_total);
    std::fprintf(f, "latpc_ptw_walk_complete_total = %llu\n", m_stats.ptw_walk_complete_total);
    std::fprintf(f, "latpc_pwc_l1_hit_total = 0\n");
    std::fprintf(f, "latpc_pwc_l1_miss_total = 0\n");
    std::fprintf(f, "latpc_pwc_l2_hit_total = 0\n");
    std::fprintf(f, "latpc_pwc_l2_miss_total = 0\n");
    std::fprintf(f, "latpc_pwc_l3_hit_total = 0\n");
    std::fprintf(f, "latpc_pwc_l3_miss_total = 0\n");
  }

 private:
  struct entry_t {
    bool valid;
    unsigned long long vpn;
    unsigned long long last_used;
    entry_t() : valid(false), vpn(0), last_used(0) {}
  };
  struct completion_t {
    unsigned long long vpn;
    unsigned long long cycle;
  };
  struct stats_t {
    unsigned long long observe_call_total = 0, empty_address_observe_total = 0;
    unsigned long long duplicate_observation_warning_total = 0;
    unsigned long long dropped_due_to_mshr_full_total = 0, dropped_due_to_pwq_full_total = 0;
    unsigned long long warp_mem_inst_observed = 0, translation_request_total = 0;
    unsigned long long page_div_bin_1 = 0, page_div_bin_2_3 = 0, page_div_bin_4_7 = 0;
    unsigned long long page_div_bin_8_15 = 0, page_div_bin_16_31 = 0, page_div_bin_32 = 0;
    unsigned long long unique_stride_sample_total = 0, unique_stride_sum = 0;
    unsigned long long same_l4pt_translation_total = 0, l4pt_translation_total = 0;
    unsigned long long l1_access = 0, l1_hit = 0, l1_miss = 0, l2_access = 0, l2_hit = 0, l2_miss = 0;
    unsigned long long l1_mshr_alloc_attempt = 0, l1_mshr_alloc_success = 0, l1_mshr_reservation_fail = 0, l1_mshr_hit_under_miss = 0;
    unsigned long long ptw_request_total = 0, ptw_queue_enqueue_total = 0, ptw_queue_full_event_total = 0;
    unsigned long long ptw_queue_shadow_stall_cycle_total = 0, ptw_walk_issue_total = 0, ptw_walk_complete_total = 0;
  };

  static unsigned env_uint(const char *name, unsigned def) {
    const char *v = std::getenv(name);
    if (!v || !*v) return def;
    char *end = NULL;
    unsigned long parsed = std::strtoul(v, &end, 10);
    return end == v ? def : (unsigned)parsed;
  }
  static bool env_flag(const char *name, bool def) {
    const char *v = std::getenv(name);
    if (!v || !*v) return def;
    return v[0] == '1' || v[0] == 'y' || v[0] == 'Y' || v[0] == 't' || v[0] == 'T';
  }
  bool tlb_hit(std::vector<entry_t> &tlb, unsigned long long vpn) {
    for (size_t i = 0; i < tlb.size(); ++i) {
      if (tlb[i].valid && tlb[i].vpn == vpn) {
        tlb[i].last_used = ++m_lru_clock;
        return true;
      }
    }
    return false;
  }
  void tlb_insert(std::vector<entry_t> &tlb, unsigned long long vpn) {
    if (tlb.empty()) return;
    size_t victim = 0;
    for (size_t i = 0; i < tlb.size(); ++i) {
      if (tlb[i].valid && tlb[i].vpn == vpn) {
        tlb[i].last_used = ++m_lru_clock;
        return;
      }
      if (!tlb[i].valid) {
        victim = i;
        break;
      }
      if (tlb[i].last_used < tlb[victim].last_used) victim = i;
    }
    tlb[victim].valid = true;
    tlb[victim].vpn = vpn;
    tlb[victim].last_used = ++m_lru_clock;
  }
  bool mshr_contains(unsigned long long vpn) const {
    for (size_t i = 0; i < m_outstanding.size(); ++i)
      if (m_outstanding[i] == vpn) return true;
    return false;
  }
  void release_mshr(unsigned long long vpn) {
    for (std::vector<unsigned long long>::iterator it = m_outstanding.begin(); it != m_outstanding.end(); ++it) {
      if (*it == vpn) {
        m_outstanding.erase(it);
        return;
      }
    }
  }
  void drain_until(unsigned long long cycle) {
    std::vector<completion_t> pending;
    for (size_t i = 0; i < m_completions.size(); ++i) {
      if (m_completions[i].cycle <= cycle) {
        tlb_insert(m_l2, m_completions[i].vpn);
        tlb_insert(m_l1, m_completions[i].vpn);
        release_mshr(m_completions[i].vpn);
        m_stats.ptw_walk_complete_total++;
      } else {
        pending.push_back(m_completions[i]);
      }
    }
    m_completions.swap(pending);
  }
  void update_divergence(size_t n) {
    if (n <= 1) m_stats.page_div_bin_1++;
    else if (n <= 3) m_stats.page_div_bin_2_3++;
    else if (n <= 7) m_stats.page_div_bin_4_7++;
    else if (n <= 15) m_stats.page_div_bin_8_15++;
    else if (n <= 31) m_stats.page_div_bin_16_31++;
    else m_stats.page_div_bin_32++;
  }
  void update_stride_and_l4(const std::vector<unsigned long long> &vpns) {
    std::set<long long> strides;
    for (size_t i = 1; i < vpns.size(); ++i) strides.insert((long long)vpns[i] - (long long)vpns[i - 1]);
    if (!strides.empty()) {
      m_stats.unique_stride_sample_total++;
      m_stats.unique_stride_sum += strides.size();
    }
    std::map<unsigned long long, unsigned> groups;
    for (size_t i = 0; i < vpns.size(); ++i) groups[vpns[i] >> 9]++;
    m_stats.l4pt_translation_total += vpns.size();
    for (std::map<unsigned long long, unsigned>::const_iterator it = groups.begin(); it != groups.end(); ++it)
      if (it->second > 1) m_stats.same_l4pt_translation_total += it->second;
  }
  void schedule_ptw(unsigned long long vpn, unsigned long long now) {
    m_stats.ptw_request_total++;
    if (m_completions.size() >= m_pwq_entries) {
      m_stats.ptw_queue_full_event_total++;
      m_stats.dropped_due_to_pwq_full_total++;
    }
    size_t walker = 0;
    for (size_t i = 1; i < m_walkers.size(); ++i)
      if (m_walkers[i] < m_walkers[walker]) walker = i;
    unsigned long long issue = std::max(now, m_walkers[walker]);
    if (issue > now) m_stats.ptw_queue_shadow_stall_cycle_total += issue - now;
    unsigned long long complete = issue + m_ptw_latency;
    m_walkers[walker] = complete;
    completion_t event = {vpn, complete};
    m_completions.push_back(event);
    m_stats.ptw_queue_enqueue_total++;
    m_stats.ptw_walk_issue_total++;
  }
  void process_vpn(unsigned long long vpn, unsigned long long now) {
    m_stats.l1_access++;
    if (tlb_hit(m_l1, vpn)) {
      m_stats.l1_hit++;
      return;
    }
    m_stats.l1_miss++;
    m_stats.l1_mshr_alloc_attempt++;
    if (mshr_contains(vpn)) {
      m_stats.l1_mshr_hit_under_miss++;
      return;
    }
    if (m_outstanding.size() >= m_l1_mshr_entries) {
      m_stats.l1_mshr_reservation_fail++;
      m_stats.dropped_due_to_mshr_full_total++;
      return;
    }
    m_outstanding.push_back(vpn);
    m_stats.l1_mshr_alloc_success++;
    m_stats.l2_access++;
    if (tlb_hit(m_l2, vpn)) {
      m_stats.l2_hit++;
      tlb_insert(m_l1, vpn);
      release_mshr(vpn);
    } else {
      m_stats.l2_miss++;
      schedule_ptw(vpn, now);
    }
  }

  bool m_initialized, m_enabled, m_pwc_enable;
  unsigned m_page_shift, m_l1_entries, m_l2_entries, m_l1_mshr_entries, m_l2_mshr_entries, m_ptw_count, m_pwq_entries, m_ptw_latency;
  unsigned long long m_event_cycle, m_lru_clock;
  stats_t m_stats;
  std::set<unsigned long long> m_unique_vpns;
  std::vector<entry_t> m_l1, m_l2;
  std::vector<unsigned long long> m_outstanding, m_walkers;
  std::vector<completion_t> m_completions;
};

inline latpc_shadow_vm_t &latpc_shadow_vm() {
  static latpc_shadow_vm_t vm;
  return vm;
}

inline bool latpc_shadow_vm_enabled() { return latpc_shadow_vm().enabled(); }

inline void latpc_shadow_vm_observe_warp_addresses(unsigned sm_id, unsigned warp_id,
                                                   unsigned long long pc,
                                                   unsigned long long cycle,
                                                   const unsigned long long *addrs,
                                                   unsigned count) {
  latpc_shadow_vm().observe_warp_addresses(sm_id, warp_id, pc, cycle, addrs, count);
}

inline void latpc_shadow_vm_print_stats(FILE *f) { latpc_shadow_vm().print_stats(f); }

#endif
'''


def gate_allows() -> bool:
    gate = latest("A20C_latpc_implementation_gate_*.csv")
    if not gate:
        return False
    rows = read_csv(gate)
    return any(r["gate_item"] == "source_implementation_allowed" and r["status"].lower() == "true" for r in rows)


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    files_csv = REPORT_DIR / f"A21A_latpc_shadow_vm_core_files_{stamp}.csv"
    report = REPORT_DIR / f"A21A_latpc_shadow_vm_core_impl_{stamp}.md"
    if not gate_allows():
        status = "PASS_DESIGN_ONLY"
        blocker = "A20C gate did not allow implementation"
        rows = []
    else:
        existed = HEADER.exists()
        HEADER.write_text(HEADER_TEXT)
        status = "PASS_WITH_WARNINGS"
        blocker = "none"
        rows = [{"path": "gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h", "repo": "nested", "action": "modify" if existed else "add", "summary": "header-only LATPC shadow VM stats substrate", "behavior_affecting": "no", "notes": "default disabled; PWC deferred"}]
    write_csv(files_csv, rows, ["path", "repo", "action", "summary", "behavior_affecting", "notes"])
    stage_report(report, "A21A LATPC Shadow VM Core", status, start_iso, start, ["python3 scripts/accelsim/a21a_latpc_shadow_vm_core.py"], [".local_reports/A20C_latpc_implementation_gate_*.csv"], [rel(files_csv), rel(report), rel(HEADER) if HEADER.exists() else ""], blocker, ["Core only; A21B adds hooks.", "No real simulator timing/control behavior is changed."])
    print(f"A21A status: {status}")
    print(f"A21A report: {rel(report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
