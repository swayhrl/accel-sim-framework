import sys,datetime
sys.path.insert(0,'/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/infrastructure/tools/v7_4f70a66da8fd')
import cold_project_restore as restore
original_resources=restore.check_resources
def guarded_resources():
 original_resources()
 restore.require(not (restore.BRIDGE/'R2_FULL_RESTORE_HOLD_R10_V1.json').exists(),'R10_R2_RESTORE_HOLD_NO_NEW_GROUP')
 restore.require(datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-17T03:44:00+00:00'),'R10_DEADLINE_NO_NEW_GROUP')
restore.check_resources=guarded_resources
restore.main()
