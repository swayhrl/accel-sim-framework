#!/usr/bin/env bash
# Run only under the site's/central EDA resource admission. No library guesses.
set -euo pipefail
: "${RTL_REPO:?absolute Framework worktree}"
: "${DC_OUT:?new unique output directory}"
: "${TARGET_LIBS:?Tcl list of actual .db files}"
: "${LINK_LIBS:?Tcl list of actual .db files, including required SRAM macros when bound}"
: "${OPERATING_CONDITIONS:?actual operating-condition name in selected DB}"
: "${PVT_LABEL:?corner label}"
: "${LIB_TIME_UNIT_NS:?ns per actual library unit, e.g. 1.0 or 0.001}"
: "${IO_DRIVE_CELL:?real selected library cell}"
: "${OUTPUT_LOAD_LIB_UNITS:?load in actual library capacitance units}"
: "${MODE:?0=B16,1=Unified,2=S64}"
export CLOCK_PERIOD_NS="${CLOCK_PERIOD_NS:-0.883392226}"
case "$MODE" in 0|1|2) ;; *) exit 2;; esac
command -v dc_shell >/dev/null
if test -e "$DC_OUT"; then echo 'DC_OUT must not already exist' >&2; exit 2; fi
mkdir -p "$DC_OUT"
python3 - <<'PY'
from pathlib import Path
import hashlib,json,os,subprocess
r=Path(os.environ['RTL_REPO']).resolve(strict=True);f=r/'rtl/ep_l2/flow/filelist.f'
files=[r/x for x in f.read_text().splitlines() if x and not x.startswith('#')]+[f,r/'rtl/ep_l2/flow/run_dc.tcl',r/'rtl/ep_l2/flow/run_dc_r2.sh',r/'rtl/ep_l2/flow/common.sdc']
d={'git_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'git_status':subprocess.check_output(['git','status','--porcelain'],cwd=r,text=True),'files':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'environment':{k:os.environ[k] for k in ('MODE','PVT_LABEL','OPERATING_CONDITIONS','LIB_TIME_UNIT_NS','CLOCK_PERIOD_NS','IO_DRIVE_CELL','OUTPUT_LOAD_LIB_UNITS','TARGET_LIBS','LINK_LIBS')},'scope':'controller/access timing cut; external SRAM macros and traditionalTag/MSHR excluded; no whole-slice PPA'}
(Path(os.environ['DC_OUT'])/'DC_SOURCE_IDENTITY.json').write_text(json.dumps(d,indent=2)+'\n')
PY
dc_shell -f "$RTL_REPO/rtl/ep_l2/flow/run_dc.tcl" -output_log_file "$DC_OUT/dc.log"
