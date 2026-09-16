# Known issues

Qualification used bundle-local CUDA 12.4.131 on Ubuntu 22.04. Hopper/TMA, GPU Microbenchmark, and broad Rodinia coverage are `V1_EXTENDED_PENDING`. Core V1 uses one fast official QV100 BFS SASS replay and one fast PTX launcher path. Target systems may supply a compatible external `CUDA_INSTALL_PATH`.

`monitor_func_test.py` may report `NOT_RUNNING_NO_OUTPUT` for completed local-procman runs because `job_status.py` may not match the generated output filename. Offline-Sim V1 quick regression therefore validates the actual PTX child output directly.
