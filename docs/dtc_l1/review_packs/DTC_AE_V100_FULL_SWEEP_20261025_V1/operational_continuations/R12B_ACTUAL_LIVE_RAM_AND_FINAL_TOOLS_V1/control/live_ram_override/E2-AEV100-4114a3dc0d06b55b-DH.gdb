set pagination off
set confirm off
set auto-load python-scripts off
set scheduler-locking off
set $buf=(void*)mmap((void*)0,4096,3,34,-1,0)
restore /root/data/dtc_main_v100_sweep_20261025_v1/control/live_ram_override/E2-AEV100-4114a3dc0d06b55b-DH.stub.bin binary $buf
set $queued=(int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)
printf "QUEUED=%d\n",$queued
detach
quit
