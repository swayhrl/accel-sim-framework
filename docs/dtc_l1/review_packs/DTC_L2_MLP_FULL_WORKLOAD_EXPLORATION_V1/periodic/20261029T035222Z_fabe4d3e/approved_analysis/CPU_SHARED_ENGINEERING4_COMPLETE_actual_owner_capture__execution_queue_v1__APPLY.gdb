set pagination off
set confirm off
set auto-load python-scripts off
set scheduler-locking off
set $buf=(void*)mmap((void*)0,4096,3,34,-1,0)
restore /root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/cpu_shared_timeslice_stage2_v1/actual_mixed_four_capture_v1/execution_queue_v1/PENDING.bin binary $buf
set $queued=(int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)
printf "QUEUED=%d\n",$queued
detach
quit
