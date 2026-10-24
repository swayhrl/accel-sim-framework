import pathlib,os,time,subprocess,json,hashlib
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/stencil768_private_qualification_A3/startup_journal_failure/control');B=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/stencil768_private_qualification_A3/startup_journal_failure/fake_library');I='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';W=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/stencil768_private_qualification_A3/startup_journal_failure/ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2_post_epoch4_single768');W.mkdir()
(C/'CONTROLLER_EXECUTED').write_text('x')
time.sleep(30)
