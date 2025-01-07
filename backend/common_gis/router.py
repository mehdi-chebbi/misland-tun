from rest_framework.response import Response
from rest_framework.decorators import api_view
from common_gis.models import ScheduledTask
from django.utils.translation import gettext as _

@api_view(['GET'])
def task_result(request, task_id):	
	try:
		tsk = ScheduledTask.objects.get(pk=task_id)
	except ScheduledTask.DoesNotExist:
		return Response({'success': 'false', 'message': _('The results no longer exist. Please schedule another task')})
	
	from django.forms.models import model_to_dict
	return Response(model_to_dict(tsk))