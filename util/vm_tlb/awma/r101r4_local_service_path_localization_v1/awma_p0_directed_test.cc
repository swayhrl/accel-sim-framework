#include <assert.h>

#include <iostream>

#include "awma_r101r4_local_service.h"

int main() {
  using namespace awma_r101r4;

  assert(kScheduledCapacity == 1);
  assert(kReadyCapacity == 16);
  assert(!scheduled_full(0));
  assert(scheduled_full(1));
  assert(!ready_full(0));
  assert(!ready_full(15));
  assert(ready_full(16));

  finite_accounting counters;
  counters.observe_depth(0, 0);
  assert(counters.max_scheduled == 0);
  assert(counters.max_ready == 0);

  counters.admissions = 1;
  counters.observe_depth(1, 0);
  assert(counters.max_scheduled == 1);
  assert(scheduled_full(counters.max_scheduled));

  counters.scheduled_full_cycles = 3;
  counters.scheduled_full_events = 1;
  assert(counters.scheduled_full_cycles >= counters.scheduled_full_events);

  counters.ready_eligible = 1;
  counters.ready_full_cycles = 2;
  counters.ready_full_events = 1;
  counters.observe_depth(1, 16);
  assert(counters.max_ready == 16);
  assert(counters.ready_full_cycles >= counters.ready_full_events);

  counters.ready = 1;
  counters.retired = 1;
  assert(counters.quiescent());

  counters.duplicate = 1;
  assert(!counters.quiescent());
  counters.duplicate = 0;

  assert(ADMISSION_NOT_HANDLED != ADMISSION_ACCEPTED);
  assert(ADMISSION_ACCEPTED != ADMISSION_BACKPRESSURED);
  assert(counters.quiescent());

  std::cout << "AWMA_R101R4_P0_DIRECTED PASS checks=22\n";
  return 0;
}
