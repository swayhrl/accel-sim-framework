"""JSON persistence that preserves nonfinite failure evidence without accepting it."""
import json, math
def safe_json(value):
    if isinstance(value,float) and not math.isfinite(value):
        return {"nonfinite_float":repr(value)}
    if isinstance(value,dict):
        return {str(k):safe_json(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [safe_json(v) for v in value]
    return value
def save_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".writing")
    tmp.write_text(json.dumps(safe_json(value),indent=2,allow_nan=False)+"\n")
    tmp.replace(path)
