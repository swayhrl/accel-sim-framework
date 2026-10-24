import pathlib
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1')
p=T/'tools/short3_final_review_bundle.py';s=p.read_text().replace("T/'tools/short3_result_base.py'","T/'tools/short3_result_base_floor5_v3.py'").replace("T/'tools/short3_result.py'","T/'tools/short3_result_floor5_v3.py'");p.write_text(s)
print('UNUSED_COPYONLY_FINAL_REVIEW_EXPORTER_USES_USER5GiB_PROFILE')
