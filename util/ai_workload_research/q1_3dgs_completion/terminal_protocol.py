"""Cooperative end-of-job acknowledgement; stdlib only. No model computation."""
import os,time,json,secrets,hashlib
from pathlib import Path
def atomic(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,indent=2)+"\n");tmp.replace(path)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def worker_terminal(context,owner_pid,lock,success,gpu_quiescent,timeout=30):
    from shared_gate import identity,kernel_holders
    context=Path(context);nonce=secrets.token_hex(16)
    ready=dict(schema="OWN_WORKER_TERMINAL_READY_V1",identity=identity(os.getpid()),
        owner_pid=owner_pid,nonce=nonce,success=success,gpu_quiescent=gpu_quiescent,
        result_sha256=sha(context/"RESULT.json") if (context/"RESULT.json").exists() else None,
        error_sha256=sha(context/"ERROR.json") if (context/"ERROR.json").exists() else None)
    path=context/"TERMINAL_READY.json";atomic(path,ready);digest=sha(path);deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        ack=context/"TERMINAL_ACK.json"
        if ack.exists():
            a=json.loads(ack.read_text())
            if a.get("owner_pid")!=owner_pid or a.get("ready_sha256")!=digest:
                raise RuntimeError("TERMINAL_ACK_IDENTITY_MISMATCH")
            if kernel_holders(lock)!=[owner_pid]:raise RuntimeError("TERMINAL_ACK_OWNER_LOST")
            return
        if kernel_holders(lock)!=[owner_pid]:raise RuntimeError("TERMINAL_OWNER_LOST")
        time.sleep(.05)
    raise TimeoutError("Own terminal acknowledgement timeout")
