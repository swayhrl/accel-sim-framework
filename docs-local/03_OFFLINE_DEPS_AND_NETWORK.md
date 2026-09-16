# Offline dependencies and network policy

Host-reused ABI: Ubuntu 22.04 glibc/libstdc++, OpenGL, zlib, zstd. Bundle-local: CUDA 12.4 qualification toolchain, Bison/Flex, pybind11, Python wheelhouse, official trace and GPU App Collection cache. Offline entrypoints set `PIP_NO_INDEX=1` and must not clone/download. Upstream online points are trace/app/dependency acquisition; preparation caches them under bundle root with SHA receipts.
