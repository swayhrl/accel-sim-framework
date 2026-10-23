"""Pure management front-door fence. Contains no science launcher or registry."""
ALLOWED={'project.status','project.assets','experiment.inspect','experiment.prepare','result.archive','result.restore'}
def evaluate(request,authority):
 reasons=[]
 if not authority:reasons.append('NO_SOURCE_AUTHORITY')
 if authority.get('commit_verified') is not True:reasons.append('MANAGEMENT_TRANSFER_NOT_COMMITTED')
 if request.get('operation') not in ALLOWED:reasons.append('OPERATION_NOT_ALLOWED_NO_SCIENTIFIC_START')
 if request.get('epoch')!=authority.get('epoch'):reasons.append('STALE_OR_UNKNOWN_AUTHORITY_EPOCH')
 if request.get('holder')!=authority.get('holder') or request.get('holder')!='huangrulin-sshfs-174':reasons.append('RETIRED_OR_FOREIGN_MANAGEMENT_CALLER')
 if authority.get('mode')!='174NEW_MANAGEMENT_ONLY_SCIENTIFIC_START_DISABLED':reasons.append('AUTHORITY_MODE_NOT_ACTIVE')
 if authority.get('scientific_dispatch_enabled') is not False:reasons.append('UNEXPECTED_SCIENTIFIC_AUTHORITY_SCOPE')
 return {'allowed':not reasons,'reasons':reasons,'scientific_start_allowed':False,'scope':'Current canonical management CLI only; official scientific-controller admission/start-consumption fencing is not enabled by this read-only management mode.'}
