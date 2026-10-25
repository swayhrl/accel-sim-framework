set pagination off
set confirm off
set auto-load python-scripts off
set scheduler-locking off
set $buf = (void *)mmap((void*)0,16384,3,34,-1,0)
restore /root/data/dtc_main_v100_sweep_20261025_v1/control/CPU_RAM_PATCH_racwuja6/V1/pending.bin binary $buf
set $queued = (int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)
printf "QUEUED=%d\n",$queued
detach
quit
