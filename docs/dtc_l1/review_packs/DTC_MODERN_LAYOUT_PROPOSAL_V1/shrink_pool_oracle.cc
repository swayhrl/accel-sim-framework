// CPU structural oracle against the unchanged production header.
// It demonstrates a progress counterexample, not application or full timing validity.
#include <cassert>
#include <cstdio>
#include <type_traits>
#include "dtc-l1-common.h"

template <class Frontend>
void check(const char *name, unsigned pool, bool expect_block) {
  dtc_l1::config cfg;
  cfg.physical_lines = pool;
  cfg.finite_service = true;
  Frontend front(cfg);
  // 96 serial one-line instructions occupy three ways of each of 32 sets.
  // Every return arrives and every instruction retires before the next begins.
  for (unsigned i = 0; i < 96; ++i) {
    const uint64_t cycle = 10*i+1;
    front.advance_service(cycle);
    assert(front.admit(i+1));
    assert(front.try_serve_tag(cycle, i*128));
    front.advance_service(cycle+1);
    auto allocation = front.access(cycle+1, i+1, i*128);
    assert(allocation.kind == dtc_l1::io_access_kind::NEW_MISS);
    front.complete(allocation.physical);
    front.advance_service(cycle+2);
    front.advance_service(cycle+3);
    if constexpr (std::is_same_v<Frontend, dtc_l1::io_frontend>) {
      assert(front.retire_head(i+1));
    } else {
      assert(front.retire_ready_uid(cycle+4, i+1));
    }
  }
  assert(front.occupancy() == 0 && front.allocated_lines() == 96);
  // Line96 targets unused way4 of set0. With P96, no free slot exists;
  // OO also cannot reclaim an invalid logical victim. No reply is outstanding.
  assert(front.admit(97));
  for (uint64_t cycle = 1000; cycle < 1064; ++cycle) {
    front.advance_service(cycle);
    assert(front.try_serve_tag(cycle, 96*128));
    front.advance_service(cycle+1);
    auto allocation = front.access(cycle+1, 97, 96*128);
    assert((allocation.kind == dtc_l1::io_access_kind::NO_FREE_LINE) == expect_block);
    if (!expect_block) {
      assert(allocation.kind == dtc_l1::io_access_kind::NEW_MISS);
      break;
    }
    assert(front.new_misses() == 96 && front.retires() == 96);
    assert(front.allocated_lines() == 96 && front.occupancy() == 1);
  }
  std::printf("%s pool=%u lines retired_before_probe=96 probe=%s PASS\n",
              name, pool, expect_block ? "NO_FREE_LINE_64_RETRIES" : "NEW_MISS");
}

int main() {
  check<dtc_l1::io_frontend>("IO", 96, true);
  check<dtc_l1::oo_frontend>("OO", 96, true);
  check<dtc_l1::io_frontend>("IO", 640, false);
  check<dtc_l1::oo_frontend>("OO", 640, false);
}
