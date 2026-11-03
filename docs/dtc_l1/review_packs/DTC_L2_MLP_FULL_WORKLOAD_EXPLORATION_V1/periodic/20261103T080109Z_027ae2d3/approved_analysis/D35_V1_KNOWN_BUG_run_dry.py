"""One-shot only. Writes exclusively to this independent E output directory."""
import datetime,json,pathlib,sys,hashlib
sys.dont_write_bytecode=True
import derived35_consumer as d
def audit(event,args):
    if event=='subprocess.Popen' or event.startswith('os.exec') or event in ('os.system','os.kill','os.killpg'):
        raise AssertionError('Readonly consumer: no subprocess/model/signal')
sys.addaudithook(audit)
out=pathlib.Path(__file__).parent/('DRY_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));out.mkdir()
value=d.ReadonlyConsumer().run()
with (out/'EVIDENCE.json').open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
summary=value['summary'];invalid=[dict(cohort=r['original']['cohort'],reasons=r['original']['reasons'])for r in value['rows']if r['original']['apparent_accepted']and not r['original']['valid']]
alts=[dict(original=r['original_cohort'],alternate=r['alternate'])for r in value['rows']if r['alternate']]
report=dict(UTC=value['UTC'],selected=summary['selected_measurement_references'],missing=summary['missing_slots'],original_valid=sum(r['original']['valid']for r in value['rows']),alternate_valid=sum(bool(r['alternate']and r['alternate']['valid'])for r in value['rows']),invalid_apparent_originals=invalid,alternates=alts,formal_GM_generated=False)
with(out/'REPORT.json').open('x')as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(dict(directory=str(out),selected=report['selected'],missing=report['missing'],invalid_apparent_originals=invalid,alternates=[dict(original=a['original'],valid=a['alternate']['valid'],reasons=a['alternate']['reasons'])for a in alts])))
