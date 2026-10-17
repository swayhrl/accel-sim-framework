#include "dtc-l1-common.h"
#include <cassert>

// Source-model witness, not an architectural data-value test. The production
// sidecar API has no operation/address argument and cannot invalidate a line.
template <class Frontend> void sidecar_preserves_mapping() {
  dtc_l1::config cfg;
  cfg.logical_sets = 1;
  cfg.logical_ways = 1;
  cfg.physical_lines = 4;
  Frontend f(cfg);
  assert(f.admit(1));
  const auto old = f.access(1, 1, 0);
  assert(old.kind == dtc_l1::io_access_kind::NEW_MISS);
  f.complete(old.physical);
  // STORE / ATOMIC / BYPASS_LOAD / PROXY_FENCE share this frontend lifecycle.
  for (unsigned uid = 2; uid <= 5; ++uid) {
    assert(f.admit(uid));
    f.add_external_dependency(uid);
    f.complete_external_dependency(uid);
    assert(!f.will_new_miss(0));
    assert(f.allocated_lines() == 1);
  }
  assert(f.admit(6));
  const auto hit = f.access(2, 6, 0);
  assert(hit.kind == dtc_l1::io_access_kind::VALID_HIT);
  assert(hit.physical.id == old.physical.id);
  assert(hit.physical.generation == old.physical.generation);
  assert(f.new_misses() == 1);
}

int main() {
  sidecar_preserves_mapping<dtc_l1::io_frontend>();
  sidecar_preserves_mapping<dtc_l1::oo_frontend>();
}
