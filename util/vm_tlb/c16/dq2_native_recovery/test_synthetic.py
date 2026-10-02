#!/usr/bin/env python3
"""CPU-only directed fixtures for frozen correctness and DQ2 formulas."""
import json
import tempfile
from copy import deepcopy
from pathlib import Path

from analysis import compare_rows,median_and_mad,metrics

def fake_row(source,row):
    return {"batch_row":row,"source_id":source,"prompt_token_count":512,"tokens":list(range(32)),"sampled_logprobs":[-0.1]*32}

def main():
    ids=[f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(4)]
    a=[fake_row(ids[i],i) for i in range(4)]
    ok,details=compare_rows(a,deepcopy(a),"MP03",ids)
    assert ok and len(details)==128
    b=deepcopy(a);b[2]["tokens"][4]=999
    assert not compare_rows(a,b,"MP03",ids)[0]
    b=deepcopy(a);b[1]["sampled_logprobs"][0]=-1.0
    assert not compare_rows(a,b,"MP03",ids)[0]
    b=deepcopy(a);b[0]["source_id"]=ids[1]
    assert not compare_rows(a,b,"MP03",ids)[0]
    x=median_and_mad([9.0,10.0,10.0,11.0,25.0])
    assert x["median_ms"]==10.0 and x["mad_ms"]==1.0 and x["max_ms"]==25.0
    with tempfile.TemporaryDirectory() as d:
        root=Path(d)
        for point,mode,value in (("MP02","A",10.0),("MP02","B",20.0),("MP03","A",20.0),("MP03","B",40.0)):
            (root/f"{point}_{mode}.json").write_text(json.dumps({"formal_samples":[{"request_gpu_elapsed_ms":value} for _ in range(5)]}))
        result=metrics(root,[{"timing_science_valid":True},{"timing_science_valid":True}])
        assert result["status"]=="DQ2_NATIVE_RECOVERY_COMPLETE"
        assert result["throughput_scale"]=={"A":2.0,"B":2.0}
        assert result["mode_response"]["MP02"]["B_over_A_ratio"]==2.0
        assert result["mode_response"]["MP02"]["A_vs_B_time_reduction"]==0.5
        assert result["timing"]["MP03_A"]["ms_per_generated_token"]==20.0/128
        invalid=metrics(root,[{"timing_science_valid":False},{"timing_science_valid":True}])
        assert invalid["status"]=="NOT_SCIENCE_VALID"
    print("11 directed DQ2 CPU fixtures PASS")

if __name__=="__main__":main()
