// PREPARED_NOT_TESTED. Equation audit only; actual C+ integration still required.
#include <cassert>
#include <cstdint>
#include <initializer_list>
#include "dtc-l1-tag-index.h"

static unsigned independent(uint64_t address, unsigned sets) {
  const auto line = address / 128;
  const unsigned bank = line % 4;
  const auto lowrow = (line / 4) % (sets / 4);
  const auto upper = (line / sets) % (sets / 4);
  return 4 * (lowrow ^ upper) + bank;
}
int main() {
  for (unsigned sets : {32U, 64U})
    for (uint64_t line = 0; line < 65536; ++line)
      for (unsigned offset : {0U, 31U, 32U, 127U}) {
        const uint64_t address = line * 128 + offset;
        const unsigned on = dtc_l1::logical_tag_set(address, sets, true);
        const unsigned off = dtc_l1::logical_tag_set(address, sets, false);
        assert(on == independent(address, sets));
        assert(on < sets && off < sets);
        assert((on & 3) == (off & 3));
        assert(off == line % sets);
      }
  // A collision must still compare full aligned addresses in C+ and DTC.
  // Their actual tag-array operations are deliberately not simulated here.
}
