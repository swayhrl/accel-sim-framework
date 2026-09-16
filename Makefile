SHELL := /bin/bash
.DEFAULT_GOAL := help
REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BUNDLE_ROOT ?= $(abspath $(REPO_ROOT)/..)
CUDA_INSTALL_PATH ?= $(BUNDLE_ROOT)/toolchain/cuda-12.4
PYTHON ?= $(BUNDLE_ROOT)/toolchain/venv/bin/python
JOBS ?= 4
BENCH ?= offline-v1-bfs-smoke
CONFIG ?= QV100-PTX
NAME ?= manual-ptx
TRACE ?=
GPU_CONFIG ?= $(REPO_ROOT)/gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config
TRACE_CONFIG ?= $(REPO_ROOT)/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
export OFFLINE_BUNDLE_ROOT := $(BUNDLE_ROOT)
export CUDA_INSTALL_PATH := $(CUDA_INSTALL_PATH)
.PHONY: help info doctor setup build clean-build rebuild smoke-sass quick receipts ptx sass stats package verify-package
help:
	@printf '%s\n' 'Offline-Sim V1 commands' '' 'Environment: doctor setup' 'Build: build [JOBS=4] clean-build rebuild' 'Validation: smoke-sass quick receipts' 'Manual: ptx [BENCH=... CONFIG=... NAME=...] | sass TRACE=...' 'Results: stats NAME=...' 'Release: package verify-package' '' 'Variables: JOBS CUDA_INSTALL_PATH PYTHON BENCH CONFIG NAME TRACE GPU_CONFIG TRACE_CONFIG'
info:
	@echo "repo root: $(REPO_ROOT)"; echo "bundle root: $(BUNDLE_ROOT)"; printf 'Framework branch: '; git -C '$(REPO_ROOT)' branch --show-current; printf 'Framework HEAD: '; git -C '$(REPO_ROOT)' rev-parse HEAD; printf 'GPGPU-Sim branch: '; git -C '$(REPO_ROOT)/gpu-simulator/gpgpu-sim' branch --show-current; printf 'GPGPU-Sim HEAD: '; git -C '$(REPO_ROOT)/gpu-simulator/gpgpu-sim' rev-parse HEAD; echo "CUDA path: $(CUDA_INSTALL_PATH)"; for tool in nvcc ptxas cuobjdump; do path="$(CUDA_INSTALL_PATH)/bin/$$tool"; if test -x "$$path"; then echo "$$tool: $$path"; "$$path" --version | sed -n '4p'; else echo "$$tool: NOT FOUND"; fi; done; if test -x '$(PYTHON)'; then echo "Python: $(PYTHON)"; '$(PYTHON)' --version; else echo 'Python: NOT FOUND'; fi
doctor:
	@'$(REPO_ROOT)/offline/doctor.sh'
setup:
	@'$(REPO_ROOT)/offline/setup.sh'
build:
	@JOBS='$(JOBS)' '$(REPO_ROOT)/offline/build.sh'
clean-build:
	@target='$(REPO_ROOT)/gpu-simulator/build/release'; printf 'Removing CMake build directory: %s\n' "$$target"; test ! -e "$$target" || rm -rf "$$target"
rebuild: clean-build build
smoke-sass:
	@'$(REPO_ROOT)/offline/smoke.sh'
quick:
	@'$(REPO_ROOT)/offline/regression.sh' --quick
receipts:
	@'$(REPO_ROOT)/offline/show-receipts.sh'
ptx:
	@set -euo pipefail; test -x '$(PYTHON)' || { echo 'ERROR: bundle venv Python is required.'; exit 2; }; test -f '$(BUNDLE_ROOT)/cache/apps/gpu-app-collection/src/setup_environment' || { echo 'ERROR: GPU App Collection setup_environment is missing.'; exit 2; }; source '$(REPO_ROOT)/offline/env.sh'; source '$(BUNDLE_ROOT)/cache/apps/gpu-app-collection/src/setup_environment'; source '$(REPO_ROOT)/gpu-simulator/setup_environment.sh'; export ACCELSIM_ROOT='$(REPO_ROOT)'; '$(PYTHON)' '$(REPO_ROOT)/util/job_launching/run_simulations.py' -l local -B '$(BENCH)' -C '$(CONFIG)' -N '$(NAME)'
sass:
	@if [ -z '$(strip $(TRACE))' ]; then echo 'ERROR: TRACE is required. Example: make sass TRACE=/path/to/kernelslist.g'; exit 2; fi; test -f '$(TRACE)' || { echo 'ERROR: TRACE does not exist.'; exit 2; }; test -x '$(REPO_ROOT)/gpu-simulator/bin/release/accel-sim.out' || { echo 'ERROR: accel-sim.out is missing.'; exit 2; }; test -f '$(GPU_CONFIG)' || { echo 'ERROR: GPU_CONFIG does not exist.'; exit 2; }; test -f '$(TRACE_CONFIG)' || { echo 'ERROR: TRACE_CONFIG does not exist.'; exit 2; }
	@'$(REPO_ROOT)/offline/run-logged.sh' manual-sass '$(REPO_ROOT)/gpu-simulator/bin/release/accel-sim.out' -trace '$(TRACE)' -config '$(GPU_CONFIG)' -config '$(TRACE_CONFIG)'
stats: NAME =
stats:
	@if [ -z '$(strip $(NAME))' ]; then echo 'ERROR: NAME is required. Example: make stats NAME=my-ptx'; exit 2; fi
	@test -x '$(PYTHON)' || { echo 'ERROR: bundle venv Python is required.'; exit 2; }; mkdir -p '$(BUNDLE_ROOT)/logs'; '$(PYTHON)' '$(REPO_ROOT)/util/job_launching/get_stats.py' -N '$(NAME)' > '$(BUNDLE_ROOT)/logs/get_stats-$(NAME).csv'
package:
	@'$(REPO_ROOT)/offline/package.sh'
verify-package:
	@archive='$(BUNDLE_ROOT)/dist/accel-sim-offline-v1.0.tar.gz'; test -f "$$archive" || { echo 'ERROR: package archive is missing.'; exit 2; }; test -f "$$archive.sha256" || { echo 'ERROR: package SHA256 sidecar is missing.'; exit 2; }; sha256sum -c "$$archive.sha256"; tar -tzf "$$archive" >/dev/null; n=$$(tar -tzf "$$archive" | grep -Ec '(^|/)\.git(/|$$)' || true); test "$$n" = 0; printf '.git directories: %s\n' "$$n"; cat "$$archive.size"; sha256sum "$$archive"
