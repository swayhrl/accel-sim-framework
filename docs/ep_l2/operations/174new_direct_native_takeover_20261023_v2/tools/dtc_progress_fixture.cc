// CPU transport engineering only. No simulator, model, trace or scientific work.
#include "ag7_policyb_progress.h"
int main() {
  dtc_ag7::ProgressProducer p;
  if (!p.enabled()) return 20;
  p.observe("INIT", 0, true, true);
  usleep(20000);
  p.observe("SIMULATE", 1, true, true);
  usleep(20000);
  p.observe("BOUNDARY", 1, true, true, "NATURAL");
  usleep(100000);
  return p.enabled() ? 0 : 21;
}
