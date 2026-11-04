"""Private fresh V4 sole entry. Requires Main native route/auth installation before use."""
import argparse,os
from ep_perf_native_wv_modes_draft import prepare,run_native
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','run']);ap.add_argument('cohort');a=ap.parse_args()
 if os.environ.get('EP_FULL_PERF_NATIVE_ENTRY')!='1':raise RuntimeError('native sole entry required')
 print((prepare if a.action=='prepare'else run_native)(a.cohort))
