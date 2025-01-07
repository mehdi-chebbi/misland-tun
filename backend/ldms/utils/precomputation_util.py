from common_gis.models import ScheduledPreComputation, ComputedResult, ComputedResultItem, AdminLevelOne
import ldms.analysis.analysis_router as router
from django.contrib.auth import get_user_model
from django.utils import timezone
from common_gis.enums import AdminLevelEnum, RasterSourceEnum
from ldms.enums import ComputationEnum
from common.utils.common_util import cint
import copy
import json
#from rest_framework.request import Request
from django.http import HttpRequest
from django.db import DatabaseError, transaction

""""
@TODO

- Ensure HTTP_HOST correct value is picked so that the url for the computed rasters can be properly picked
- 
"""
User = get_user_model()
def run_computations():
	"""
	Run computations that have been scheduled
	"""
	jobs = ScheduledPreComputation.objects.filter(status="Queued")
	res = None
	for job in jobs:
		if job.computation_type == ComputationEnum.LULC.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_lulc, 
					method='lulc', 
					extra_payload={
						"raster_type": 1,
						'show_change': False,
						'raster_source': RasterSourceEnum.LULC.value
					}
				) 
		if job.computation_type == ComputationEnum.LULC_CHANGE.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_lulc, 
					method='lulc_change', 
					extra_payload={
						"raster_type": 1,
						'show_change': True,
						'raster_source': RasterSourceEnum.LULC.value
					}
				) 
		if job.computation_type == ComputationEnum.FOREST_CHANGE.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_forest_change, 
					method='forest_change', 
					extra_payload={ 
						'raster_source': RasterSourceEnum.LULC.value
					}
				) 
		if job.computation_type == ComputationEnum.SOC.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_soc, 
					method='forest_change', 
					extra_payload={ 
						'raster_source': RasterSourceEnum.LULC.value
					}
				) 
		if job.computation_type == ComputationEnum.FOREST_CARBON_EMISSION.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_forest_carbon_emission, 
					method='forest_carbon_emission', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.PRODUCTIVITY_STATE.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_state, 
					method='state', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.PRODUCTIVITY_TRAJECTORY.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_trajectory, 
					method='trajectory', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.PRODUCTIVITY_PERFORMANCE.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_performance, 
					method='performance', 
					extra_payload={ 					
					}
			) 
		if job.computation_type == ComputationEnum.PRODUCTIVITY.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_productivity, 
					method='productivity', 
					extra_payload={ 						
					}
				)
		if job.computation_type == ComputationEnum.LAND_DEGRADATION.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_land_degradation, 
					method='degradation', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.ARIDITY_INDEX.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_aridity, 
					method='aridity_index', 
					extra_payload={ 					
					}
				) 
		if job.computation_type == ComputationEnum.CLIMATE_QUALITY_INDEX.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_climate_quality_index, 
					method='climate_quality_index', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.SOIL_QUALITY_INDEX.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_soil_quality_index, 
					method='soil_quality_index', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.VEGETATION_QUALITY_INDEX.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_vegetation_quality_index, 
					method='vegetation_quality_index', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.MANAGEMENT_QUALITY_INDEX.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_management_quality_index, 
					method='management_quality_index', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.ESAI.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_esai, 
					method='esai', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.ILSWE.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_ilswe, 
					method='ilswe', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.RUSLE.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_rusle, 
					method='rusle', 
					extra_payload={ 						
					}
				) 
		if job.computation_type == ComputationEnum.COASTAL_VULNERABILITY_INDEX.value:
			res = _do_enqueue(job=job, 
					func=router.enqueue_coastal_vulnerability_index, 
					method='coastal_vulnerability_index', 
					extra_payload={ 						
					}
				) 
	return res 
 

def _do_enqueue(job, func, method, extra_payload):
	"""
	Invoke computation call

	Args:
		job: ScheduledPreComputation object		
		func: function to be invoked
		method: user-friendly name for the computation
		extra_payload: additional key/vals to be added to the payload. They are computation specific
	"""
	vector = job.continent if job.admin_level == AdminLevelEnum.CONTINENTAL.key else (job.region if job.admin_level==AdminLevelEnum.REGIONAL.key else job.admin_zero)
	data = sanitize_payload(payload={
		'vector': vector.id,
		'admin_level': cint(job.admin_level),
		'admin_0' : job.admin_zero.id if job.admin_level == AdminLevelEnum.COUNTRY.key else None, 
		'start_year': job.start_year,
		'end_year': job.end_year,
		'custom_coords': None,
		'transform': "area", 
		'raster_source': job.datasource
	}, job_id=job.id)

	data.update(extra_payload)
	usr = User.objects.filter(email__startswith="admin").first()
	request = clone_request(data, usr)
	drf_request = clone_post_request_rest(data, user=usr, orig_request=request)
	res = func(request=request, extra_request=drf_request)
	success = res.data['success'] == 'true'
	error = res.data['message'] if not success else None
	queue_msg = res.data['message'] if success else None
	start_job(job=job, success=success, method=method, args=data, queue_msg=queue_msg, error=error)
	return res

def start_job(job, success, method, args, queue_msg, error):
	"""
	Start job processing
	"""
	job.status = "Processing" if success else "Failed"    
	job.args = json.dumps(args)
	job.method = method
	job.started_on = timezone.now()
	job.queue_msg = queue_msg
	job.error = error
	job.save()

def complete_job(scheduled_task, cache_key, success=True, error=None, func=None):
	"""
	Complete job processing
	"""
	def _generate_computed_results(results, request, args, admin_one=None, admin_two=None):
		"""
		Generate ComputedResult objects
		"""		
		parent = None
		with transaction.atomic():
			parent = ComputedResult(
				scheduled_precomputation=scheduled_task.scheduled_precomputation,
				cache_key=cache_key, 
				owner=User.objects.get(email=scheduled_task.owner), 
				continent=scheduled_precomputation.continent, 
				region=scheduled_precomputation.region, 
				admin_zero=scheduled_precomputation.admin_zero, 
				admin_one=admin_one, 
				admin_two=admin_two, 
				custom_polygon=None, 
				computation_type=scheduled_precomputation.computation_type, 
				change_enum=scheduled_task.change_enum,
				nodata=results['nodataval'], 
				prefix=None, 
				resolution=None, 
				subdir=None, 
				raster_file=results['rasterpath'], 
				start_year=scheduled_precomputation.start_year, 
				end_year=scheduled_precomputation.end_year, 
				arguments=args, # scheduled_task.args, 
				results=router.parse_result(results), #json.dumps(results), # scheduled_task.result,
				succeeded=scheduled_task.succeeded, 
				completed_on=timezone.now(),# scheduled_task.completed_on, 
				request=request, # scheduled_task.request, 
				queue_msg=scheduled_task.status,  
			)
			parent.save()
			
			children = _extract_stats(results, parent)
			for child in children:
				child.save()

			"""
			# Recursively navigate to the lowest entry for stats. Some results have stats in many levels e.g lulc
			stats = results['stats']
			while 'stats' in stats or isinstance(stats, list):
				if isinstance(stats, list): # especially for LULC and LULC_CHANGE
					if 'label' in stats[0]: # for LULC Change
						break
					stats = stats[0] # for LULC_CHANGE
					if 'stats' in stats:
						stats = stats['stats']
						break
				else:
					stats = stats['stats']

			# Save individual result items
			for entry in stats:
				child = ComputedResultItem(
					result=parent,
					key=entry['key'] if 'key' in entry else entry['change_type'],
					label=entry['label'],
					count=entry['raw_val'] if 'raw_val' in entry else entry['count'],
					value=entry['value'] if 'value' in entry else entry['area']  
				)
				child.save()
			""" 
	
	def _extract_stats(results, parent):

		def _make_child(entry):
			return ComputedResultItem(
					result=parent,
					key=entry['key'] if 'key' in entry else entry['change_type'],
					label=entry['label'],
					count=entry['raw_val'] if 'raw_val' in entry else entry['count'],
					value=entry['value'] if 'value' in entry else entry['area']  
				)

		# Recursively navigate to the lowest entry for stats. Some results have stats in many levels e.g lulc
		children = []
		stats = results['stats']
		
		if 'stats' in stats:
			stats = stats['stats']
		# while 'stats' in stats and not isinstance(stats, list):
		# 	if isinstance(stats, list): # especially for LULC and LULC_CHANGE
		# 		if 'label' in stats[0]: # for LULC Change
		# 			break
		# 		stats = stats[0] # for LULC
		# 		if 'stats' in stats:
		# 			# stats = stats['stats']
		# 			break
		# 	else:
		# 		stats = stats['stats']

		if isinstance(stats, list): #e.g for ForestChange, LULC, LULC_Change
			if 'stats' in stats[0]:
				for entry in stats: # for LULC
					for itm in entry['stats']:
						child = _make_child(itm)					
						if results['precomputed_field_map']:
							mp = results['precomputed_field_map']
							for key, val in mp.items():
								setattr(child, key, entry.get(val))
						children.append(child)
			else:
				for itm in stats: # for LULC_Change
					child = _make_child(itm)					
					children.append(child)
		else:
			if 'stats' in stats:
				stats = stats['stats']
			for entry in stats:
				child = _make_child(entry)
				children.append(child)

		# while 'stats' in stats or isinstance(stats, list):
		# 	if isinstance(stats, list): # especially for LULC and LULC_CHANGE
		# 		if 'label' in stats[0]: # for LULC Change
		# 			break
		# 		stats = stats[0] # for LULC_CHANGE
		# 		if 'stats' in stats:
		# 			stats = stats['stats']
		# 			break
		# 	else:
		# 		stats = stats['stats']
		return children
		
	def _delete_old_computations():
		"""
		Delete older computations
		"""
		computations = ScheduledPreComputation.objects.filter(admin_zero=scheduled_precomputation.admin_zero,
					  region=scheduled_precomputation.region,
					  continent=scheduled_precomputation.continent,
					  computation_type=scheduled_precomputation.computation_type,
					  start_year=scheduled_precomputation.start_year,
					  end_year=scheduled_precomputation.end_year).exclude(pk=scheduled_precomputation.pk)
		computations.delete()

	scheduled_precomputation = ScheduledPreComputation.objects.get(pk=scheduled_task.scheduled_precomputation_id)
	results = json.loads(scheduled_task.result)
	_generate_computed_results(results=results, request=scheduled_task.request, args=scheduled_task.args)
	scheduled_precomputation.change_enum = scheduled_task.change_enum
	scheduled_precomputation.succeeded = success
	scheduled_precomputation.status = "Succeeded" if success else "Failed"
	scheduled_precomputation.error = error
	scheduled_precomputation.completed_on = timezone.now()
	scheduled_precomputation.save()

	if success: #if successful, delete old computations
		_delete_old_computations()

	# If it is at country level, compute stats for admin_level_one
	if scheduled_precomputation.admin_level == AdminLevelEnum.COUNTRY.key:
		level_ones = AdminLevelOne.objects.filter(admin_zero=scheduled_precomputation.admin_zero)
		for admin_one in level_ones:
			print("Precomputing {0}".format(admin_one.name_1))
			data = json.loads(scheduled_task.args)
			data.update({
				'admin_level': 1,
				'vector': admin_one.id
			})
			usr = User.objects.filter(email__startswith="admin").first()
			request = clone_request(data, usr)
			drf_request = clone_post_request_rest(data, user=usr, orig_request=request)
			# res = func(request=request, extra_request=drf_request) 
			res = func(request, data=data, user=usr, orig_request=request, can_queue=False, orig_data=data)
			results = res.data
			_generate_computed_results(results=results, request=request, args=json.dumps(data), admin_one=admin_one)

def sanitize_payload(payload, job_id):
	payload['cached'] = 0
	payload['scheduled_precomputation_id'] = job_id
	payload['precomputation_context'] = 1
	return payload

def clone_request(data, usr):    
	request = router.clone_post_request(data=data, user=usr, orig_request=None)
	return request

def clone_post_request_rest(data, user, orig_request):
	# factory = RequestFactory()
	# request = factory.post('/')	
	from rest_framework.test import APIRequestFactory
	from ldms.views import MockView
	factory = APIRequestFactory()
	request = factory.post("/dummyview", data=data, content_type="application/json")  # WSGIRequest

	# Add the view call to get response object
	view = MockView.as_view()
	response = view(request)
	response.render()
	drf_request = response.renderer_context['request']  # rest_framework.request.Request

	# This is a really bad idea to access private class members directly
	drf_request._data = data
	drf_request._full_data = data
	drf_request._user = user
	drf_request.META['HTTP_HOST'] = 'localhost'

	if orig_request:
		meta_fields, fields = router.get_request_fields()
		for fld in meta_fields:
			drf_request.META[fld] = orig_request.META.get(fld)
		for fld in fields:
			setattr(drf_request, fld, getattr(orig_request, fld))		
	return drf_request
