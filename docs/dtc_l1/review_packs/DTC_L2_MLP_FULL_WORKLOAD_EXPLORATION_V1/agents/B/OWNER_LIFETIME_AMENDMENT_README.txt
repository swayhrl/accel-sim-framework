Owner lifetime amendment V1 (independent operational amendment, not frozen-source edit)

Source: l2_owner_lifetime_amendment_v1.py
SHA256: 9a47a06ff4ff7dd9f677ef08a50099620f756876e024c192a4d958cbd785b7fa
CPU driver: qualify_owner_lifetime_cpu.py
SHA256: 613455318fc84bb92fba2dc65ac25c4726a6365501ee18180de6c11e06136467
Qualification: OWNER_LIFETIME_AMENDMENT_CPU_QUALIFICATION.json
SHA256: d77ddfa11aa236ab75075b875adfb72212ec88204eb2837da7955375834fae3b

Main coordinator only: import module in existing parent main-thread GIL pending callback, call apply_in_owner(), save returned proof independently as an exclusive operational ACK. Agent B did not attach production parent or apply the hook.

The amendment checks actual owner PID/start and captures the already-running non-daemon DTC_L2_MLP_ADDON_THREAD. It appends one threading._register_atexit callback. Existing hook list is byte/object ordered as before; no removal or reordering. During threading shutdown, reverse order makes the newly appended hook execute before ALL currently registered hooks, including ThreadPoolExecutor._python_exit. It repeatedly joins the existing addon (.5s) until it naturally returns. It does not reset the concurrent.futures global shutdown flag. Creating further normal ThreadPoolExecutors does not register another _python_exit, since that handler registers when concurrent.futures.thread is imported.

Current174: CPython3.10.12. Its installed threading.py/_shutdown and concurrent/futures/thread.py were inspected directly. Actual positive isolated subprocess reaches threading._SHUTTING_DOWN=True after old main returns, then successfully expands an existing executor 1->3 and submits9 jobs, creates a new2-worker executor and completes4 more jobs, naturally shuts both pools and addon, then exits0. The futures global shutdown flag remainsFalse until addon completion. A matching negative control without the hook reproduces RuntimeError(cannot schedule new futures after shutdown). Later-registered benign hooks were included: they execute first, then keepalive, then older hooks. All12 CPU assertions passed; no model starts or registry access.

CPython3.8 differs: official3.8.20 sources use daemon TPE workers and ordinary atexit.register; threading._register_atexit is absent. This amendment intentionally refuses the missing private API; its3.8 source check is not a3.8 runtime qualification. Official source locations:
https://raw.githubusercontent.com/python/cpython/v3.8.20/Lib/threading.py
https://raw.githubusercontent.com/python/cpython/v3.8.20/Lib/concurrent/futures/thread.py

Scope: existing owner lifecycle only. Does not intercept old mainloop, restart any task, replace controller/executor, change frozen source/lease/budget, or signal old/new models. Registration proof includes existing hook identities/indices for the coordinator to confirm actual in-process ordering before future lifecycle changes.
