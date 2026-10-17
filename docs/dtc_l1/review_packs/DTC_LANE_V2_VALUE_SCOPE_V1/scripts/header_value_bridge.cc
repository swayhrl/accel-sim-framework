#include "dtc-l1-common.h"
#include <array>
#include <cassert>
#include <cstdio>

// Values below are EXTERNAL synthetic overlays. The production header has no
// payload read/write API. This program proves metadata compatibility only.
template <class Frontend> void no_selected_E(const char *mode) {
  dtc_l1::config cfg;
  cfg.logical_sets = cfg.logical_ways = 1;
  cfg.physical_lines = 4;
  Frontend f(cfg);
  assert(f.admit(1));
  const auto old = f.access(1, 1, 0);
  f.complete(old.physical);
  std::array<unsigned char, 4> allocation_bytes{7, 7, 7, 7};
  auto externally_published_memory = allocation_bytes;
  // Synthetic single-byte publication. Not a production store instruction.
  externally_published_memory[1] = 9;
  assert(f.admit(2));
  f.add_external_dependency(2);
  f.complete_external_dependency(2);
  assert(f.admit(3));
  const auto again = f.access(2, 3, 0);
  assert(again.kind == dtc_l1::io_access_kind::VALID_HIT);
  assert(again.physical.id == old.physical.id &&
         again.physical.generation == old.physical.generation);
  assert(allocation_bytes[1] != externally_published_memory[1]);
  std::printf("{\"case\":\"NO_E_PARTIAL_BYTE_OVERLAY\",\"mode\":\"%s\","
              "\"production_metadata_hit\":true,\"external_old_byte\":7,"
              "\"external_published_byte\":9,\"production_value_proof\":false}\n", mode);
}

#ifdef HAS_PUBLISHED_K1
void selected_E_pending_return() {
  dtc_l1::config cfg;
  cfg.selected_mode = dtc_l1::mode::PAPER_OO;
  cfg.logical_sets = cfg.logical_ways = 1;
  cfg.physical_lines = 4;
  cfg.finite_service = true;
  dtc_l1::oo_frontend f(cfg);
  f.advance_service(1);
  assert(f.admit(1));
  const auto old = f.access(1, 1, 0).physical;
  f.complete(old);  // inflight may be closed; metadata return is still pending.
  assert(f.admit(2));
  assert(f.access(1, 2, 0).kind == dtc_l1::io_access_kind::PENDING_HIT);
  const auto delta = f.invalidate_lookup(1); // exact published X API, no patch
  assert(delta.changed == 1 && delta.retained == 1 && !delta.reclaimed);
  assert(f.ref_count(old) == 2 && !f.tag_visible(old));
  assert(f.fill_identity_matches(old) && f.will_new_miss(0));
  assert(f.admit(3));
  const auto fresh = f.access(2, 3, 0);
  assert(fresh.kind == dtc_l1::io_access_kind::NEW_MISS);
  assert(fresh.physical.id != old.id);
  f.complete(fresh.physical);
  f.advance_service(2);
  assert(f.entry_ready_for(1) && f.entry_ready_for(2) && f.entry_ready_for(3));
  assert(f.retire_ready_uid(2, 1) && f.is_allocated(old));
  assert(f.retire_ready_uid(3, 2) && !f.is_allocated(old));
  assert(f.retire_ready_uid(4, 3));
  // The values 7 and 9 are attached by this witness, not returned by the API.
  std::printf("{\"case\":\"E_OLD_PENDING_NEW_ALLOCATION\","
              "\"old_external_version\":7,\"new_external_version\":9,"
              "\"old_identity_retained_to_final_ref\":true,"
              "\"production_value_proof\":false}\n");
}
#endif

int main() {
  no_selected_E<dtc_l1::io_frontend>("IO");
  no_selected_E<dtc_l1::oo_frontend>("OO");
#ifdef HAS_PUBLISHED_K1
  selected_E_pending_return();
#else
  std::puts("{\"case\":\"K1_FROZEN_CORE\",\"status\":\"NO_API_NOT_TESTED\"}");
#endif
}
