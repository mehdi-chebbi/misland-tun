import os
from common_gis.utils.settings_util import get_gis_settings

def can_queue(request):
	"""return True if the Task can be scheduled"""
	setts = get_gis_settings()
	if not setts.enable_task_scheduling or not request.user.is_authenticated:
		return False
	elif setts.enable_task_scheduling:
		return True
	return False