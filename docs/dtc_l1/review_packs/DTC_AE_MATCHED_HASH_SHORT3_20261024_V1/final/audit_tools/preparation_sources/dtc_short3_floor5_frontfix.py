import pathlib
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1');p=T/'tools/short3_frontend_floor5_v3.py';front=p.read_text()
original_archived=sorted(p.name.removesuffix('_ARCHIVE_RECEIPT.json') for p in (T/'control').glob('E2-AEF3-*_ARCHIVE_RECEIPT.json'))
front=front.replace('def main(argv):','ORIGINAL_ARCHIVED='+repr(original_archived)+'\ndef main(argv):')
front=front.replace("if (T/'control'/(argv[2]+'_ARCHIVE_RECEIPT.json')).exists():","if argv[2] in ORIGINAL_ARCHIVED:")
p.write_text(front)
print('CLOSED_ORIGINAL_OUTBOX_ROUTES_PRESERVED',len(original_archived))
