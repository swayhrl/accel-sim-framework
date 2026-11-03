set pagination off
set confirm off
set auto-load python-scripts off
set scheduler-locking off
set $buf=(void*)mmap((void*)0,4096,3,34,-1,0)
restore /root/data/dtc_stage_iia_first16_20261104_v1/control/operational_amendments/disk_preclaim_v1/actual_single_callback_v1/PENDING.bin binary $buf
set $queued=(int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)
printf "QUEUED=%d\n",$queued
detach
quit
