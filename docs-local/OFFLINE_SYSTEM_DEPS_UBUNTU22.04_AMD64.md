# Ubuntu 22.04 amd64 offline system dependencies

Present on the build host: GCC/G++ 11.4, CMake 3.22, Make 4.3, Python 3.10, Git 2.34.

Must carry/install on a clean target: `build-essential`, `cmake`, `make`, `python3`, `python3-venv`, `git`, `bison`, `flex`, `libboost-all-dev`, `zlib1g-dev`, `libssl-dev`, `libxml2-dev`, `libncurses5-dev`, `libffi-dev`, compatible NVIDIA driver and chosen CUDA toolkit. Optional: `ninja-build`, `ccache`, `gdb`, `tmux`.

Do not replace a target CUDA installation; select it through `CUDA_INSTALL_PATH`.
