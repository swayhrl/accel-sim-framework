import pathlib,json,sys
j=json.loads(pathlib.Path(sys.argv[1]).read_text());pathlib.Path(j['marker']).write_text('ran');print(json.dumps({'status':'GROUPED_ALL_SHARDS_CRC_PASS','fixture_only':True}));raise SystemExit(j['exit'])
