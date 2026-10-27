"""Create a candidate only. Never edits the native production entry."""
import argparse,hashlib,json,pathlib
DEFAULT='/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/padding_only_v1/padding_frontend.py'
def quote(s):return "'"+s.replace("'","'\"'\"'")+"'"
def build(original,frontend=DEFAULT):
 if not frontend.startswith('/')or any(c in frontend for c in '\x00\r\n'):raise ValueError('Absolute single-line frontend path required')
 prefix=r'''#!/bin/sh
set -eu
# Explicit padding-only opt-in. Every original route byte follows unchanged.
dtc_padding_route_hold() {
 printf '{"status":"HOLD","reason":"%s","scientific_starts":0}\n' "$1" >&2
 exit 2
}
dtc_padding_route_count=0
dtc_padding_route_bad=0
for dtc_padding_route_arg in "$@"; do
 case "$dtc_padding_route_arg" in
  --padding-only-admission-v1) dtc_padding_route_count=$((dtc_padding_route_count + 1));;
  --padding-only-admission*) dtc_padding_route_bad=1;;
 esac
done
if [ "$dtc_padding_route_bad" -ne 0 ]; then
 dtc_padding_route_hold UNKNOWN_PADDING_FLAG
fi
if [ "$dtc_padding_route_count" -ne 0 ]; then
 [ "$dtc_padding_route_count" -eq 1 ] || dtc_padding_route_hold DUPLICATE_PADDING_FLAG
 [ "$#" -ge 3 ] || dtc_padding_route_hold INCOMPLETE_PADDING_COMMAND
 case "$1:$2:$3" in
  experiment:prepare:E2-DTCL2MLP-*|experiment:inspect:E2-DTCL2MLP-*|experiment:run-native:E2-DTCL2MLP-*) ;;
  *) dtc_padding_route_hold PADDING_SCOPE_OR_OPERATION_MISMATCH;;
 esac
 dtc_padding_route_validate_tail() {
  shift 3
  dtc_padding_route_projects=0
  dtc_padding_route_tailflags=0
  while [ "$#" -gt 0 ]; do
   case "$1" in
    --project)
     [ "$#" -ge 2 ] || dtc_padding_route_hold MISSING_PROJECT_VALUE
     [ "$2" = DTC_L1 ] || dtc_padding_route_hold WRONG_PADDING_PROJECT
     dtc_padding_route_projects=$((dtc_padding_route_projects + 1))
     shift 2;;
    --padding-only-admission-v1)
     dtc_padding_route_tailflags=$((dtc_padding_route_tailflags + 1))
     shift;;
    *) dtc_padding_route_hold UNKNOWN_PADDING_ARGUMENT;;
   esac
  done
  [ "$dtc_padding_route_projects" -eq 1 ] || dtc_padding_route_hold PROJECT_NOT_EXACTLY_ONCE
  [ "$dtc_padding_route_tailflags" -eq 1 ] || dtc_padding_route_hold PADDING_FLAG_NOT_IN_OPTION_TAIL
 }
 dtc_padding_route_validate_tail "$@"
 exec /usr/bin/python3 -B FRONTEND_PATH "$@"
fi
'''.replace('FRONTEND_PATH',quote(frontend)).encode()
 candidate=prefix+original
 return candidate,{'schema':'PADDING_ONLY_CLI_ROUTE_CANDIDATE_V2_REBASE','frontend_path':frontend,'flag':'--padding-only-admission-v1','old_entry_sha256':hashlib.sha256(original).hexdigest(),'old_entry_bytes':len(original),'prefix_bytes':len(prefix),'candidate_sha256':hashlib.sha256(candidate).hexdigest(),'old_body_exact_suffix':candidate[len(prefix):]==original,'production_mutations':0,'model_starts':0,'new_route_handles_ACTIVE_metadata':False,'ACTIVE_check_owner':'B private frontend; route alone grants no authority'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--output-dir',required=True);p.add_argument('--frontend',default=DEFAULT);a=p.parse_args();out=pathlib.Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 b,m=build(pathlib.Path(a.original).read_bytes(),a.frontend);(out/'native.candidate.sh').write_bytes(b);(out/'ROUTE_MANIFEST.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n',encoding='utf-8');print(json.dumps(m))
