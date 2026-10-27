import pathlib,json,hashlib,zipfile
P=pathlib.Path(__file__).resolve().parent
names=['POSITIVE_CASE_MECHANISM_REPORT.md','POSITIVE_CASE_MECHANISM_REPORT.json','SOURCE_SEMANTICS.json','ORIGINAL_SOURCE_FILES.json','RAW_EVIDENCE_EXTRACT.json.gz','QUALIFIED_OPCODE_EVIDENCE.json','VALIDATION.json','build_report.py','extract_remote.py','package_deliverable.py']
files=[{'path':n,'bytes':(P/n).stat().st_size,'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest()}for n in names]
(P/'DELIVERY_MANIFEST.json').write_text(json.dumps({'schema':'AGENT_C_DELIVERY_V1','files':files,'reproduction':'build_report.py reads ../A/SUITE_PERFORMANCE_ANALYSIS.json and own archived evidence; B frozen qualified opcode extract is self-contained. Full original raw logs/source files are never rewritten.','excluded_scratch':['RAW_EVIDENCE_EXTRACT.json','shader.cc','shader.h','gpu-cache.cc','gpu-cache.h','dtc-l1-common.h','dtc-l1-tag-index.h'],'new_simulator_starts':0},indent=2)+'\n')
with zipfile.ZipFile(P/'agent_c_deliverable.zip','w',compression=zipfile.ZIP_DEFLATED)as z:
 for n in names+['DELIVERY_MANIFEST.json']:z.write(P/n,n)
print(json.dumps({'files':len(files)+1,'zip_bytes':(P/'agent_c_deliverable.zip').stat().st_size,'zip_sha256':hashlib.sha256((P/'agent_c_deliverable.zip').read_bytes()).hexdigest()}))
