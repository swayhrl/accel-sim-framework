// CPU sizeof-only disclosure. No model construction, library API or trace input.
#include "gpgpu-sim/dtc-l1-common.h"
#include <cstdio>
int main() {
  std::printf("physical_line=%zu entry=%zu config=%zu service=%zu frontend=%zu\n",
              sizeof(dtc_l1::oo_frontend::physical_line),
              sizeof(dtc_l1::oo_frontend::entry), sizeof(dtc_l1::config),
              sizeof(dtc_l1::service_entry), sizeof(dtc_l1::oo_frontend));
}
