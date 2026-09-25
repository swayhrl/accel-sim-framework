#include <stdint.h>
#include <stdio.h>

#include "gpgpu-sim/prel1_coalescing_observer.h"

int main() {
  awma_prel1::opportunity_observer &observer =
      awma_prel1::opportunity_observer::instance();
  if (!observer.enabled()) return 2;
  const uint64_t page = 65536;

  // One leader, one same-cycle follower and one cross-cycle follower.
  observer.note_physical_launch(
      0, 1, 0, 10, page, 1,
      vm_translation::TRANSLATION_ACCESS_READ, 10);
  observer.note_physical_launch(
      0, 2, 0, 10, page, 1,
      vm_translation::TRANSLATION_ACCESS_READ, 10);
  observer.note_physical_launch(
      0, 3, 0, 10, page, 1,
      vm_translation::TRANSLATION_ACCESS_READ, 11);
  observer.note_l2_probe(0, 2);
  observer.note_existing_mshr_merge(0, 2);
  // The same-cycle follower finishes before the leader (timing risk); the
  // cross-cycle follower finishes after the leader.
  observer.note_physical_completion(0, 2, 20);
  observer.note_physical_completion(0, 1, 30);
  observer.note_physical_completion(0, 3, 35);

  // The next identical request is a post-completion repeat, not coalescing.
  observer.note_physical_launch(
      0, 4, 0, 10, page, 1,
      vm_translation::TRANSLATION_ACCESS_READ, 40);
  observer.note_physical_completion(0, 4, 41);

  // Exact-identity mismatches must not merge.
  observer.note_physical_launch(
      0, 5, 0, 11, page, 1,
      vm_translation::TRANSLATION_ACCESS_READ, 50);
  observer.note_physical_launch(
      0, 6, 1, 11, page, 1,
      vm_translation::TRANSLATION_ACCESS_READ, 50);
  observer.note_physical_launch(
      0, 7, 0, 11, page, 2,
      vm_translation::TRANSLATION_ACCESS_READ, 50);
  observer.note_physical_launch(
      0, 8, 0, 11, page, 1,
      vm_translation::TRANSLATION_ACCESS_WRITE, 50);
  observer.note_physical_completion(0, 5, 60);
  observer.note_physical_completion(0, 6, 60);
  observer.note_physical_completion(0, 7, 60);
  observer.note_physical_completion(0, 8, 60);

  observer.print(stdout);
  return 0;
}
