from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from ldms.analysis.lulc import LULC
from ldms.analysis.soc import SOC
from ldms.analysis.productivity import Productivity
from ldms.analysis.land_degradation import LandDegradation
from ldms.analysis.forest_change import ForestChange
from ldms.analysis.forest_fire import ForestFireGEE
from ldms.analysis.forest_fire_risk import ForestFireRiskGEE
from ldms.analysis.medalus import Medalus
from ldms.analysis.forest_carbon_emission import ForestCarbonEmission
from ldms.analysis.ilswe import ILSWE
from ldms.analysis.rusle import RUSLE
from ldms.analysis.coastal_erosion import CoastalVulnerabilityIndex
from ldms.enums import ClimaticRegionEnum, ProductivityCalcEnum, MedalusCalcEnum
from common_gis.models import AdminLevelZero, ScheduledTask
from rest_framework.permissions import IsAuthenticated
from ldms.enums import (RasterSourceEnum, RasterCategoryEnum, 
		RUSLEComputationTypeEnum, ILSWEComputationTypeEnum, CVIComputationTypeEnum)
import json 
from django.utils import timezone 
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

import django_rq
from django.utils.translation import gettext as _
from django_rq import job
from rq import get_current_job

# from ldms.tasks import add_numbers
from common.queue import RedisQueue
from common.utils.common_util import get_random_int, get_random_string
from common_gis.utils.common_util import can_queue
from rq_scheduler import Scheduler
import datetime 

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from communication.utils import email_helper
from common.utils.settings_util import get_common_settings
from common_gis.utils.settings_util import get_gis_settings
from common_gis.utils.vector_util import get_vector, queue_threshold_exceeded, get_admin_level_ids_from_db, search_vectors
from common.utils.cache_util import set_cache_key, get_cached_results, generate_cache_key, get_cache_key
from common.utils.file_util import (get_download_url)
from common.utils.url_map_util import get_mapped_url
from common_gis.models import ComputedResult
from ldms.enums import LulcChangeEnum, ComputationEnum
from common.models import MonitoringLog
from common.utils import monitoring_util
from common.utils.common_util import cint
from memory_profiler import profile
import copy

import logging

# see https://www.easydevguide.com/posts/decorator_mem for how to write decorators

# create logger
logger = logging.getLogger('memory_profile_log')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(settings.MEMORY_PROFILER_LOG_FILE)
fh.setLevel(logging.DEBUG)

# create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)

from memory_profiler import LogFile
import sys
if settings.USE_MEMORY_PROFILER_LOG_FILE:
 	sys.stdout = LogFile('memory_profile_log', reportIncrementFlag=True)

LULC_ANALYSIS = 1
LULC_CHANGE_ANALYSIS = 2
mem_logs = open(settings.MEMORY_PROFILER_LOG_FILE, 'w+')

def get_enqueue_message(request, **kwargs):
	return _("Your task is being processed. The response will be sent to {0} when the results are ready".format(str(request.user.email)))

@api_view(['POST'])
def test_tiles(request, **kwargs):
	from common_gis.utils.raster_util import test_generate_tiles
	test_notify_user(request)
	return Response(test_generate_tiles(raster_file=None, 
						nodata=255, 
						change_enum=LulcChangeEnum))

@api_view(['POST'])
def test_push_notifications(request, **kwargs):	
	return Response(test_notify_user(request, test_push=True)) 

@api_view(['POST'])
def test_precomputations(request, **kwargs):	
	from ldms.utils.precomputation_util import run_computations
	try:
		from common_gis.models import ScheduledTask
		# task = ScheduledTask.objects.get(pk=2000)
		# post_analysis_save_task(request=request, task=task, res=json.loads(task.result), error=task.error, data=request.data, func=lulc)
		res = run_computations()
		return Response({ "success": 'true', 'message': res.data["message"] })
	except Exception as e:
		error = str(e)		
		return Response({ "success": 'false', "error": error })

@api_view(['POST'])
def enqueue_lulc(request, **kwargs):
	return _enqueue(func=lulc, request=request, computation_type=ComputationEnum.LULC, **kwargs)

@api_view(['POST'])
def enqueue_forest_change(request, **kwargs):
	return _enqueue(func=forest_change, request=request, computation_type=ComputationEnum.FOREST_CHANGE,**kwargs)

@api_view(['POST'])
def enqueue_forest_fire(request, **kwargs):
	return _enqueue(func=forest_fire, request=request, computation_type=ComputationEnum.FOREST_FIRE,**kwargs)

@api_view(['POST'])
def enqueue_forest_fire_risk(request, **kwargs):
	force_queue = '0.0.0.0' not in request.META['HTTP_HOST']#allow direct computing in debug mode
	# return _enqueue(func=forest_fire_risk, request=request, force_queue=True, computation_type=ComputationEnum.FOREST_FIRE_RISK,**kwargs)
	return _enqueue(func=forest_fire_risk, request=request, force_queue=force_queue, computation_type=ComputationEnum.FOREST_FIRE_RISK,**kwargs)

@api_view(['POST'])
def enqueue_soc(request, **kwargs):
	return _enqueue(func=soc, request=request, computation_type=ComputationEnum.SOC, **kwargs)

@api_view(['POST'])
def enqueue_state(request, **kwargs):
	return _enqueue(func=state, request=request, computation_type=ComputationEnum.PRODUCTIVITY_STATE, **kwargs)

@api_view(['POST'])
def enqueue_trajectory(request, **kwargs):
	return _enqueue(func=trajectory, request=request, computation_type=ComputationEnum.PRODUCTIVITY_TRAJECTORY, **kwargs)

@api_view(['POST'])
def enqueue_performance(request, **kwargs):
	return _enqueue(func=performance, request=request, computation_type=ComputationEnum.PRODUCTIVITY_PERFORMANCE, **kwargs)

@api_view(['POST'])
def enqueue_productivity(request, **kwargs):
	return _enqueue(func=productivity, request=request, computation_type=ComputationEnum.PRODUCTIVITY, **kwargs)

@api_view(['POST'])
def enqueue_land_degradation(request, **kwargs):
	return _enqueue(func=land_degradation, request=request, force_queue=False, computation_type=ComputationEnum.LAND_DEGRADATION, **kwargs)

@api_view(['POST'])
def enqueue_aridity(request, **kwargs):
	return _enqueue(func=aridity_index, request=request, computation_type=ComputationEnum.ARIDITY_INDEX, **kwargs)

@api_view(['POST'])
def enqueue_climate_quality_index(request, **kwargs):
	return _enqueue(func=climate_quality_index, request=request, computation_type=ComputationEnum.CLIMATE_QUALITY_INDEX, **kwargs)

@api_view(['POST'])
def enqueue_soil_quality_index(request, **kwargs):
	return _enqueue(func=soil_quality_index, request=request, computation_type=ComputationEnum.SOIL_QUALITY_INDEX, **kwargs)

@api_view(['POST'])
def enqueue_vegetation_quality_index(request, **kwargs):
	return _enqueue(func=vegetation_quality_index, request=request, computation_type=ComputationEnum.VEGETATION_QUALITY_INDEX, **kwargs)

@api_view(['POST'])
def enqueue_management_quality_index(request, **kwargs):
	return _enqueue(func=management_quality_index, request=request, computation_type=ComputationEnum.MANAGEMENT_QUALITY_INDEX, **kwargs)

@api_view(['POST'])
def enqueue_esai(request, **kwargs):
	return _enqueue(func=esai, request=request, force_queue=True, computation_type=ComputationEnum.ESAI, **kwargs) 

@api_view(['POST'])
def enqueue_forest_carbon_emission(request, **kwargs):
	return _enqueue(func=forest_carbon_emission, request=request, computation_type=ComputationEnum.FOREST_CARBON_EMISSION, **kwargs)

@api_view(['POST'])
def enqueue_ilswe(request, **kwargs):
	return _enqueue(func=ilswe, request=request, computation_type=ComputationEnum.ILSWE, **kwargs)

@api_view(['POST'])
def enqueue_rusle(request, **kwargs):
	return _enqueue(func=rusle, request=request, computation_type=ComputationEnum.RUSLE, **kwargs)

@api_view(['POST'])
def enqueue_coastal_vulnerability_index(request, **kwargs):
	return _enqueue(func=coastal_vulnerability_index, request=request, computation_type=ComputationEnum.COASTAL_VULNERABILITY_INDEX, **kwargs)

def in_precomputation_context(request, **kwargs):
	return 'precomputation_context' in request.data

def _enqueue(func, request, computation_type, force_queue=False, **kwargs):
	"""Enqueue computation

	Args:
		func (function): Function to be queued
		request (HttpRequest): Web requestpass
		force_queue (bool, optional): Determine if it has to be queued by force. Defaults to False.
	"""
	def clone_request():
		meta_fields, fields = get_request_fields()
		req = {'META': {}}
		for fld in meta_fields:
			if hasattr(request, 'META'):
				req['META'][fld] = request.META.get(fld)
			else:
				req['META'][fld] = request._request.META.get(fld)
		for fld in fields:
			if hasattr(request, 'META'):
				req[fld] = getattr(request, fld)
			else:
				req[fld] = getattr(request._request, fld)
		req['is_queued'] = True # set to True to distinguish between direct and cloned requests. 
		return req	

	def validate_vector_threshold():
		"""
		Validates the vector to check if it qualifies for queueing
		"""
		params = request.data
		admin_level = params.get('admin_level', None)
		vector_id = params.get('vector', None)
		custom_coords = params.get('custom_coords', None)
		
		vector, err = get_vector(admin_level=admin_level, 
						  shapefile_id=vector_id, 
						  custom_vector_coords=custom_coords, 
						  admin_0=None,
						  request=request
				)
		return queue_threshold_exceeded(request, vector)

	def append_admin_level_args():
		"""Append level 0, level 1 and level2 ids given the passed admin_level

		Returns:
			tuple(level0_id, level1_id, level2_id): Tuple of level0, level1 and level2 ids
		"""
		params = request.data
		admin_level = params.get('admin_level', None)
		vector_id = params.get('vector', None)
		continent, region, level_0, level_1, level_2 = get_admin_level_ids_from_db(admin_level, vector_id)
		request.data['continent'] = continent
		request.data['region'] = region
		request.data['admin0'] = level_0
		request.data['admin1'] = level_1
		request.data['admin2'] = level_2

	def _get_cached_results(rqst):
		cache_key = generate_cache_key(rqst.data, rqst.path)
		cache = get_cache_key(cache_key) # get_cached_results(request)
		if not cache:
			from common_gis.utils.precompute_util import get_precomputed_result
			obj = get_precomputed_result(cache_key, rqst, computation_type=computation_type, payload=rqst.data)
			#json.dumps(eval(str(results.data)))
			if isinstance(obj, ComputedResult):
				cache = json.loads(obj.results)
			elif isinstance(obj, str):
				cache = json.loads(str)
			elif isinstance(obj, dict):
				cache = obj
		return cache
	
	if not isinstance(computation_type, ComputationEnum):
		return Response({ "success": 'false', 'message': _("Invalid computation type") })
	# which request to use when there is an extra_request object. Extra_request is passed when processing Scheduled PreComputations
	if 'extra_request' in kwargs:
		request = kwargs['extra_request']
	is_precomputation = in_precomputation_context(request=request)
	system_settings = get_gis_settings()
	#If caching enabled, try retrieve cached vals. ForestFire is not cached since GEE urls expire after some time
	if not is_precomputation and system_settings.enable_cache and func != forest_fire: 
		cached = None		
		if "cached" in request.data:
			if request.data.get("cached") == 1 or request.data.get("cached") == "true":
				cached = _get_cached_results(request)
		else:
			cached = _get_cached_results(request)

		if cached: # return cached results
			val = json.loads(cached) if not isinstance(cached, dict) else cached
			return Response(val)

	# do_queue = can_queue(request)
	exceeded, do_queue, msg = validate_vector_threshold()

	if is_precomputation:
		do_queue = True #If in_precomputation, queue the processing
		force_queue = False
		exceeded = False

	if exceeded and not do_queue: # if threshold hit and user not allowed to queue, return error/msg
		return Response({ "success": 'false', 'message': msg })

	if force_queue:
		if not request.user.is_authenticated:
			return Response({ "success": 'false', 'message': "This request must be queued. You need to be logged in for the request to be queued." })

		if not msg: # If there is no error
			do_queue = True #if force_queue, set exceeded and  to True if there is no error message			

	# Validate that task scheduling is enabled
	if do_queue and not system_settings.enable_task_scheduling:
		return Response({ "success": 'false', 'message': _("The selected region is too large and therefore requires to be scheduled but task scheduling has not been enabled.") })

	if do_queue:
		# set is_authenticated to True since its already queued and no restrictions on queued since only logged in users can queue
		user = {'is_authenticated': True }
		for fld in get_user_fields():
			user[fld] = getattr(request.user, fld)

		orig_data = copy.copy(request.data)
		append_admin_level_args()
		q = RedisQueue()
		if is_precomputation:
			q.enqueue_extra_high(func=func, 
						request=None, 
						data=request.data, 
						user=user, 
						orig_request=clone_request(), # if not is_precomputation else request, 
						orig_data=orig_data,
						can_queue=do_queue)
		else: # the other jobs can be set to different queues depending on the vector size
			if orig_data.get('admin_level') == -1:
				q.enqueue_extra_high(func=func, 
							request=None, 
							data=request.data, 
							user=user, 
							orig_request=clone_request(), # if not is_precomputation else request, 
							orig_data=orig_data,
							can_queue=do_queue)
			elif orig_data.get('admin_level') == 0:
				q.enqueue_high(func=func, 
							request=None, 
							data=request.data, 
							user=user, 
							orig_request=clone_request(), # if not is_precomputation else request, 
							orig_data=orig_data,
							can_queue=do_queue)
			elif orig_data.get('admin_level') == 2:
				q.enqueue_low(func=func, 
							request=None, 
							data=request.data, 
							user=user, 
							orig_request=clone_request(), # if not is_precomputation else request, 
							orig_data=orig_data,
							can_queue=do_queue)
			else:
				q.enqueue_medium(func=func, 
							request=None, 
							data=request.data, 
							user=user, 
							orig_request=clone_request(), # if not is_precomputation else request, 
							orig_data=orig_data,
							can_queue=do_queue)
		return Response({ "success": 'true', 'message': get_enqueue_message(request) })
	else:
		monitor = monitoring_util.start_monitoring(execution_name=str(func), 
											 params=request.data, 
											 caller_id='Instant Computation',
											 caller_type='Instant Computation', 
											 caller_details=str(func))
		results = func(request)		
		# we are not caching forest_fire since GEE urls expire after some time
		if system_settings.enable_cache and func != forest_fire:		
			# Only save to cache if there is no error and if caching enabled
			if 'error' not in results.data:				
				set_cache_key(key=generate_cache_key(request.data, request.path), 
						value=json.dumps(eval(str(results.data))),
						timeout=system_settings.cache_limit)
		if monitor:
			monitoring_util.stop_monitoring(monitoring_log_id=monitor.id)
		return results

def get_user_fields():
	return ["email", "first_name", "last_name", "id", "username"]

def get_request_fields():
	meta_fields = ['SERVER_NAME', 'SERVER_PORT', 'REMOTE_ADDR', 'HTTP_HOST']
	fields = ['path', 'path_info', 'scheme', 'user', '_current_scheme_host']
	return meta_fields, fields

def clone_post_request(data, user, orig_request):
	settings = get_common_settings()
	factory = RequestFactory()	
	request = factory.post('/', HTTP_HOST=settings.backend_url.replace("https://", "").replace("http:", "").replace("/", ""))
	request.data = data
	request.user = user

	if orig_request:
		meta_fields, fields = get_request_fields()
		for fld in meta_fields:
			request.META[fld] = orig_request['META'].get(fld)
		for fld in fields:
			request.fld = orig_request.get(fld)		
	return request

# @api_view(['GET'])
# def task_result(request, task_id):	
# 	try:
# 		tsk = ScheduledTask.objects.get(pk=task_id)
# 	except ScheduledTask.DoesNotExist:
# 		return Response({'success': 'false', 'message': 'The results no longer exist. Please schedule another task'})
	
# 	from django.forms.models import model_to_dict
# 	return Response(model_to_dict(tsk))

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile #(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None) 
def lulc(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Land Use Land Cover
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
						task_name="lulc", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data

	# params = request.data	
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	admin_0 = params.get('admin_0', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	raster_source = params.get('raster_source', RasterSourceEnum.LULC.value)

	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = LULC(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		raster_source=raster_source,
		enforce_single_year=True,
		request=request,
	)
	error = ""
	if show_change == False:
		res = obj.calculate_lulc()
		error = obj.error
	elif show_change == True:
		res = obj.calculate_lulc_change()
		error = obj.error
	
	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=lulc)
	
	if error:
		return Response({ "error": error })
	else:
		return Response(res)
		
# @api_view(['POST'])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def forest_change(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Forest Change Cover
	We return the values where the land cover is Forest
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
							task_name="forest_change", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data
	
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	raster_source = params.get('raster_source', RasterSourceEnum.LULC.value)
	admin_0 = params.get('admin_0', None)
	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = ForestChange(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		raster_source=raster_source,
		enforce_single_year=False,
		request=request,
	)
	res = obj.calculate_forest_change()
	error = obj.error	

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=forest_change)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

# @api_view(['POST'])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def forest_fire(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Forest Fire  
	Args:
		request (Request): A Web request object

	Returns:
		Response: A Url string where the results can be downloaded as zip
	"""
	can_queue = False # Do not queue ForestFire since it is being processed by GEE
	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
						task_name="forest_fire", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data
	
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	raster_type = params.get('raster_type', None)

	prefire_start = params.get('prefire_start', None)
	prefire_end = params.get('prefire_end', None)

	postfire_start = params.get('postfire_start', None)
	postfire_end = params.get('postfire_end', None)

	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	raster_source = params.get('raster_source', RasterSourceEnum.LANDSAT8.value)
	admin_0 = params.get('admin_0', None)

	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = ForestFireGEE(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords,
		prefire_start = prefire_start,
		prefire_end=prefire_end,
		postfire_start=postfire_start,
		postfire_end=postfire_end,
		transform=transform,
		raster_source=raster_source,
		request=request,
	)
	res = obj.calculate_forest_fire()
	error = obj.error	

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=forest_fire)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def forest_fire_risk(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Forest Fire Risk
	Args:
		request (Request): A Web request object

	Returns:
		Response: A Url string where the results can be downloaded as zip
	"""
	# can_queue = False # Do not queue ForestFire since it is being processed by GEE
	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
						task_name="forest_fire_risk", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data
	
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)	

	start = params.get('start_date', None)
	end = params.get('end_date', None)

	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	# raster_source = params.get('raster_source', RasterSourceEnum.LANDSAT8.value)
	admin_0 = params.get('admin_0', None) 
	if not admin_0:
		admin_0 = params.get('admin0', None)

	# raster_source = map_raster_source(raster_source)
	# if raster_source == None:
	# 	return Response({ "error": _("Invalid value for raster source") })

	obj = ForestFireRiskGEE(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords,
		start_date = start,
		end_date=end,
		transform=transform,
		request=request,
	)

	res, error = None, None
	try:
		res = obj.calculate_fire_risk()
		error = obj.error
	except Exception as e:
		error = str(e)
		return Response({ "error": error })

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=forest_fire_risk)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

def map_raster_source(raster_source_val):
	"""
	Get RasterSourceEnum given a value
	"""
	try:
		return RasterSourceEnum(raster_source_val)
	except ValueError:
		return None

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def soc(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Soil Organic Carbon 
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
						task_name="soc", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data
	
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	reference_raster = params.get('reference_raster', 3)
	raster_source = params.get('raster_source', RasterSourceEnum.LULC.value)
	admin_0 = params.get('admin_0', None)

	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = SOC(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords, # custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		write_to_disk=True,
		climatic_region=ClimaticRegionEnum.TemperateDry,
		reference_soc=reference_raster,
		raster_source=raster_source,
		request=request,
	)

	res = ""
	error = ""
	if show_change == False:
		# res = obj.calculate_soc_change()
		# error = obj.error
		pass
	elif show_change == True:
		res = obj.calculate_soc_change()
		error = obj.error 

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=soc)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def trajectory(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Compute productivity trajectory sub-indicator

	Args:
		request (Request): A Web request object
	
	Returns:
		Response: A JSON string with statistic values
	"""
	return dispatch_productivity(request, ProductivityCalcEnum.TRAJECTORY, data=data, 
			user=user, orig_request=orig_request, can_queue=can_queue, 
			orig_data=orig_data)
	
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def state(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Compute productivity trajectory sub-indicator

	Args:
		request (Request): A Web request object
	
	Returns:
		Response: A JSON string with statistic values
	"""
	return dispatch_productivity(request, ProductivityCalcEnum.STATE, data=data, 
			user=user, orig_request=orig_request, can_queue=can_queue, 
			orig_data=orig_data)
	
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def performance(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Compute productivity performance sub-indicator

	Args:
		request (Request): A Web request object
	
	Returns:
		Response: A JSON string with statistic values
	"""
	return dispatch_productivity(request, ProductivityCalcEnum.PERFORMANCE, data=data, 
			user=user, orig_request=orig_request, can_queue=can_queue, 
			orig_data=orig_data)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def productivity(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Compute productivity indicator

	Args:
		request (Request): A Web request object
	
	Returns:
		Response: A JSON string with statistic values
	"""
	return dispatch_productivity(request, ProductivityCalcEnum.PRODUCTIVITY, data=data, 
				user=user, orig_request=orig_request, can_queue=can_queue, 
				orig_data=orig_data)

def dispatch_productivity(request, productivity_calc_enum, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Compute productivity sub-indicators

	Args:
		request: Request object
		productivity_calc_enum (ProductivityCalcEnum)
	"""	
	if productivity_calc_enum == ProductivityCalcEnum.TRAJECTORY:
		task_name = "trajectory"
	if productivity_calc_enum == ProductivityCalcEnum.STATE:
		task_name = "state"
	if productivity_calc_enum == ProductivityCalcEnum.PERFORMANCE:
		task_name = "performance"
	if productivity_calc_enum == ProductivityCalcEnum.PRODUCTIVITY:
		task_name = "productivity"

	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
						task_name=task_name, orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data

	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	reference_eco_units = params.get('reference_eco_units', None)
	raster_source = params.get('raster_source', RasterSourceEnum.MODIS.value)
	admin_0 = params.get('admin_0', None)
	veg_index = params.get('veg_index', RasterCategoryEnum.NDVI.value)
	version = params.get("version", 1)
	class_map = params.get('class_map', 3)

	# reference_raster = params.get('reference_raster', 3)
	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = Productivity(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords, # custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		write_to_disk=True,
		climatic_region=ClimaticRegionEnum.TemperateDry,
		# reference_soc=reference_raster,
		show_change=show_change,
		request=request,
		raster_source=raster_source,
		reference_eco_units=reference_eco_units,
		veg_index=veg_index,
		version=version,
		class_map=class_map
	)
	func = None
	if productivity_calc_enum == ProductivityCalcEnum.TRAJECTORY:
		res = obj.calculate_trajectory()
		func = trajectory
	if productivity_calc_enum == ProductivityCalcEnum.STATE:
		res = obj.calculate_state()
		func = state
	if productivity_calc_enum == ProductivityCalcEnum.PERFORMANCE:
		res = obj.calculate_performance()
		func = performance
	if productivity_calc_enum == ProductivityCalcEnum.PRODUCTIVITY:
		res = obj.calculate_productivity()
		func = productivity

	error = obj.error 

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=func)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def land_degradation(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Land Degradation
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
							task_name="land_degradation", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data
	
	params = request.data
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	reference_eco_units = params.get('reference_eco_units', None)
	reference_soc = params.get('reference_raster', None)
	raster_source = params.get('raster_source', RasterSourceEnum.MODIS.value)
	admin_0 = params.get('admin_0', None)
	veg_index = params.get('veg_index', RasterCategoryEnum.NDVI.value)

	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = LandDegradation(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords, # custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		write_to_disk=True,
		climatic_region=ClimaticRegionEnum.TemperateDry,
		# reference_soc=reference_raster,
		show_change=show_change,
		request=request,
		reference_soc=reference_soc,
		raster_source=raster_source,
		reference_eco_units=reference_eco_units,
		veg_index=veg_index
	)

	res = obj.calculate_land_degradation()
	error = obj.error 

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=land_degradation)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def aridity_index(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Aridity Indx
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	return dispatch_medalus(request, MedalusCalcEnum.ARIDITY_INDEX, data=data, 
					user=user, orig_request=orig_request, can_queue=can_queue, 
					orig_data=orig_data)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def climate_quality_index(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Climate Quality Index
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	return dispatch_medalus(request, MedalusCalcEnum.CLIMATE_QUALITY_INDEX, data=data, 
					user=user, orig_request=orig_request, can_queue=can_queue, 
					orig_data=orig_data)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def soil_quality_index(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Soil Quality Index
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	return dispatch_medalus(request, MedalusCalcEnum.SOIL_QUALITY_INDEX, data=data, 
					user=user, orig_request=orig_request, can_queue=can_queue, 
					orig_data=orig_data)

@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def vegetation_quality_index(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Vegetation Quality Index
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	return dispatch_medalus(request, MedalusCalcEnum.VEGETATION_QUALITY_INDEX, data=data, 
					user=user, orig_request=orig_request, can_queue=can_queue, 
					orig_data=orig_data)

@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def management_quality_index(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Management Quality Index
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	return dispatch_medalus(request, MedalusCalcEnum.MANAGEMENT_QUALITY_INDEX, data=data, 
					user=user, orig_request=orig_request, can_queue=can_queue, 
					orig_data=orig_data)

@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def esai(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate ESAI
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	return dispatch_medalus(request, MedalusCalcEnum.ESAI, data=data, 
					user=user, orig_request=orig_request, can_queue=can_queue, 
					orig_data=orig_data)

def dispatch_medalus(request, medalus_calc_enum, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Compute Medalus indicies

	Args:
		request: Request object
		medalus_calc_enum (MedalusCalcEnum)
	"""	
	if medalus_calc_enum == MedalusCalcEnum.ARIDITY_INDEX:
		task_name = "aridity_index"
	if medalus_calc_enum == MedalusCalcEnum.CLIMATE_QUALITY_INDEX:
		task_name = "climate_quality_index"
	if medalus_calc_enum == MedalusCalcEnum.SOIL_QUALITY_INDEX:
		task_name = "soil_quality_index"
	if medalus_calc_enum == MedalusCalcEnum.VEGETATION_QUALITY_INDEX:
		task_name = "vegetation_quality_index"
	if medalus_calc_enum == MedalusCalcEnum.MANAGEMENT_QUALITY_INDEX:
		task_name = "management_quality_index"
	if medalus_calc_enum == MedalusCalcEnum.ESAI:
		task_name = "esai"

	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
						task_name=task_name, orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data

	params = request.data
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	reference_eco_units = params.get('reference_eco_units', None)
	reference_soc = params.get('reference_raster', None)
	raster_source = params.get('raster_source', RasterSourceEnum.MODIS.value)
	admin_0 = params.get('admin_0', None)
	
	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = Medalus(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords, # custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		write_to_disk=True,
		# climatic_region=ClimaticRegionEnum.TemperateDry,
		# reference_soc=reference_raster,
		show_change=show_change,
		request=request,
		# reference_soc=reference_soc,
		raster_source=raster_source,
		reference_eco_units=reference_eco_units,
		# veg_index=veg_index
	)

	func = None
	if medalus_calc_enum == MedalusCalcEnum.ARIDITY_INDEX:
		res, raster = obj.calculate_aridity_index()
		func = aridity_index
	if medalus_calc_enum == MedalusCalcEnum.CLIMATE_QUALITY_INDEX:
		res, raster = obj.calculate_climate_quality_index()
		func = climate_quality_index
	if medalus_calc_enum == MedalusCalcEnum.SOIL_QUALITY_INDEX:
		res, raster = obj.calculate_soil_quality_index()
		func = soil_quality_index
	if medalus_calc_enum == MedalusCalcEnum.VEGETATION_QUALITY_INDEX:
		res, raster = obj.calculate_vegetation_quality_index()
		func = vegetation_quality_index
	if medalus_calc_enum == MedalusCalcEnum.MANAGEMENT_QUALITY_INDEX:
		res, raster = obj.calculate_management_quality_index()
		func = management_quality_index
	if medalus_calc_enum == MedalusCalcEnum.ESAI:
		res = obj.calculate_esai()
		func = esai

	error = obj.error

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=func)
	# else: # try cache results if no error
	# 	if not error:
	# 		cache_results(params, res, error)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def forest_carbon_emission(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Forest Carbon Emission
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
						task_name="lulc", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data

	# params = request.data	
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	admin_0 = params.get('admin_0', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	raster_source = params.get('raster_source', RasterSourceEnum.HANSEN.value)
	muf = params.get('muf', None)
	mfu_forest_threshold = params.get('mfu_forest_threshold', None)
	carbon_stock = params.get('carbon_stock', None)
	degradation_emission_proportion = params.get('degradation_emission_proportion', None)

	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = ForestCarbonEmission(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		raster_source=raster_source,
		enforce_single_year=True,
		muf=muf,
		mfu_forest_threshold=mfu_forest_threshold,
		carbon_stock=carbon_stock,
		degradation_emission_proportion=degradation_emission_proportion,
		request=request,
	)
	error = ""
	# if show_change == False:
	res = obj.calculate_carbon_emission()
	error = obj.error
	# elif show_change == True:
	# 	res = obj.calculate_lulc_change()
	# 	error = obj.error
	
	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=forest_carbon_emission)
	
	if error:
		return Response({ "error": error })
	else:
		return Response(res)

@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def ilswe(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Land Degradation
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	def get_computation_type():
		comp_type = params.get('computation_type', None)
		comp_type = comp_type.title() if comp_type else None
		if comp_type == ILSWEComputationTypeEnum.VEGETATION_COVER.label.title():
			return ILSWEComputationTypeEnum.VEGETATION_COVER
		if comp_type == ILSWEComputationTypeEnum.SOIL_CRUST.label.title():
			return ILSWEComputationTypeEnum.SOIL_CRUST
		if comp_type == ILSWEComputationTypeEnum.SOIL_ROUGHNESS.label.title():
			return ILSWEComputationTypeEnum.SOIL_ROUGHNESS
		if comp_type == ILSWEComputationTypeEnum.ERODIBLE_FRACTION.label.title():
			return ILSWEComputationTypeEnum.ERODIBLE_FRACTION
		if comp_type == ILSWEComputationTypeEnum.CLIMATE_EROSIVITY.label.title():
			return ILSWEComputationTypeEnum.CLIMATE_EROSIVITY
		if comp_type == ILSWEComputationTypeEnum.ILSWE.label.title():
			return ILSWEComputationTypeEnum.ILSWE
		return ILSWEComputationTypeEnum.ILSWE

	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
							task_name="ilswe", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data
	
	params = request.data
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	reference_eco_units = params.get('reference_eco_units', None)
	reference_soc = params.get('reference_raster', None)
	raster_source = params.get('raster_source', RasterSourceEnum.MODIS.value)
	admin_0 = params.get('admin_0', None)
	veg_index = params.get('veg_index', RasterCategoryEnum.NDVI.value)
	computation_type = get_computation_type()

	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = ILSWE(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords, # custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		write_to_disk=True,
		climatic_region=ClimaticRegionEnum.TemperateDry,
		# reference_soc=reference_raster,
		show_change=show_change,
		request=request,
		reference_soc=reference_soc,
		raster_source=raster_source,
		reference_eco_units=reference_eco_units,
		veg_index=veg_index,
		computation_type=computation_type
	)

	res = obj.calculate_ilswe()
	error = obj.error 

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=ilswe)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def rusle(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Land Degradation
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	def get_computation_type():
		comp_type = params.get('computation_type', None)
		comp_type = comp_type.title() if comp_type else None
		if comp_type == RUSLEComputationTypeEnum.RAINFALL_EROSIVITY.label.title():
			return RUSLEComputationTypeEnum.RAINFALL_EROSIVITY
		if comp_type == RUSLEComputationTypeEnum.SOIL_ERODIBILITY.label.title():
			return RUSLEComputationTypeEnum.SOIL_ERODIBILITY
		if comp_type == RUSLEComputationTypeEnum.SLOPE_STEEPNESS.label.title():
			return RUSLEComputationTypeEnum.SLOPE_STEEPNESS
		if comp_type == RUSLEComputationTypeEnum.COVER_MANAGEMENT.label.title():
			return RUSLEComputationTypeEnum.COVER_MANAGEMENT
		if comp_type == RUSLEComputationTypeEnum.CONSERVATION_PRACTICES.label.title():
			return RUSLEComputationTypeEnum.CONSERVATION_PRACTICES
		if comp_type == RUSLEComputationTypeEnum.RUSLE.label.title():
			return RUSLEComputationTypeEnum.RUSLE

		return RUSLEComputationTypeEnum.RUSLE

	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
							task_name="rusle", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data
	
	params = request.data
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	reference_eco_units = params.get('reference_eco_units', None)
	reference_soc = params.get('reference_raster', None)
	raster_source = params.get('raster_source', RasterSourceEnum.MODIS.value)
	admin_0 = params.get('admin_0', None)
	veg_index = params.get('veg_index', RasterCategoryEnum.NDVI.value)
	computation_type = get_computation_type()

	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = RUSLE(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords, # custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		write_to_disk=True,
		climatic_region=ClimaticRegionEnum.TemperateDry,
		# reference_soc=reference_raster,
		show_change=show_change,
		request=request,
		reference_soc=reference_soc,
		raster_source=raster_source,
		reference_eco_units=reference_eco_units,
		veg_index=veg_index,
		computation_type=computation_type
	)

	res = obj.calculate_rusle()
	error = obj.error 

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=rusle)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

@profile#(stream=mem_logs if not settings.USE_MEMORY_PROFILER_LOG_FILE else None)
def coastal_vulnerability_index(request, data=None, user=None, orig_request=None, can_queue=False, orig_data=None):
	"""Generate Costal Vulnerability Index
	
	Args:
		request (Request): A Web request object

	Returns:
		Response: A JSON string with statistic values
	"""	
	def get_computation_type():
		comp_type = params.get('computation_type', None)
		comp_type = comp_type.title() if comp_type else None
		if comp_type == CVIComputationTypeEnum.GEOMORPHOLOGY.label.title():
			return CVIComputationTypeEnum.GEOMORPHOLOGY
		if comp_type == CVIComputationTypeEnum.COASTAL_SLOPE.label.title():
			return CVIComputationTypeEnum.COASTAL_SLOPE
		if comp_type == CVIComputationTypeEnum.SEALEVEL_CHANGE.label.title():
			return CVIComputationTypeEnum.SEALEVEL_CHANGE
		if comp_type == CVIComputationTypeEnum.SHORELINE_EROSION.label.title():
			return CVIComputationTypeEnum.SHORELINE_EROSION
		if comp_type == CVIComputationTypeEnum.TIDE_RANGE.label.title():
			return CVIComputationTypeEnum.TIDE_RANGE
		if comp_type == CVIComputationTypeEnum.WAVE_HEIGHT.label.title():
			return CVIComputationTypeEnum.WAVE_HEIGHT
		if comp_type == CVIComputationTypeEnum.CVI.label.title():
			return CVIComputationTypeEnum.CVI 
		return CVIComputationTypeEnum.CVI

	if can_queue:
		job, task = pre_analysis_save_task(request=orig_request, data=data, user=user, 
							task_name="cvi", orig_data=orig_data)
		
	params = data
	if not request:
		request = clone_post_request(data, user, orig_request)
	else:
		params = request.data
	
	params = request.data
	vector_id = params.get('vector', None)
	admin_level = params.get('admin_level', None)
	raster_type = params.get('raster_type', None)
	start_year = params.get('start_year', None)
	end_year = params.get('end_year', None)
	custom_coords = params.get('custom_coords', None)
	transform = params.get('transform', "area")
	show_change = params.get('show_change', False)
	reference_eco_units = params.get('reference_eco_units', None)
	reference_soc = params.get('reference_raster', None)
	raster_source = params.get('raster_source', RasterSourceEnum.MODIS.value)
	admin_0 = params.get('admin_0', None)
	veg_index = params.get('veg_index', RasterCategoryEnum.NDVI.value)
	computation_type = get_computation_type()

	raster_source = map_raster_source(raster_source)
	if raster_source == None:
		return Response({ "error": _("Invalid value for raster source") })

	obj = CoastalVulnerabilityIndex(
		admin_0=admin_0,
		admin_level=admin_level,
		shapefile_id = vector_id,
		custom_vector_coords = custom_coords, # custom_coords,
		raster_type = raster_type,
		start_year=start_year,
		end_year=end_year,
		transform=transform,
		write_to_disk=True,
		climatic_region=ClimaticRegionEnum.TemperateDry,
		# reference_soc=reference_raster,
		show_change=show_change,
		request=request,
		reference_soc=reference_soc,
		raster_source=raster_source,
		reference_eco_units=reference_eco_units,
		veg_index=veg_index,
		computation_type=computation_type
	)

	res = obj.calculate_cvi()
	error = obj.error 

	if can_queue:
		post_analysis_save_task(request, task, res, error, data, func=coastal_vulnerability_index)

	if error:
		return Response({ "error": error })
	else:
		return Response(res)

def pre_analysis_save_task(request, data, user, task_name, orig_data):
	"""Save task"""
	job = get_current_job()
	print("User email: ",  user['email'] if user else "" )
	print("data=", data)
	task = ScheduledTask.objects.create(
		owner=user['email'] if user else "",
		job_id=job.get_id() if job else get_random_string(length=10),
		name=task_name,
		method=request['path'],
		#args=json.dumps(json.loads(data)) if data else "{}",
		args=json.dumps(data) if data else "{}",		
		orig_args=json.dumps(orig_data) if orig_data else "{}",
		status=_("Processing"),
		request=request,
		scheduled_precomputation_id=data['scheduled_precomputation_id'] if 'scheduled_precomputation_id' in data else None #associated sch
	)
	monitor = monitoring_util.start_monitoring(execution_name=request['path'], 
											 params=json.dumps(orig_data) if orig_data else "{}", 
											 caller_id=task.id, 
											 caller_type='Scheduled Computation', 
											 caller_details=user['email'] if user else "")
	return job, task

def parse_result(res):
	"""
	Pass JSON results received after computation and returns a string representation of the data
	"""

	if isinstance(res, dict):
		return json.dumps(eval(str(res)))
	return res

def post_analysis_save_task(request, task, res, error, data, func):
	"""Update task with results of analysis

	Args:
		request: Request object
		task: ScheduledTask
		res: Results of computation
		error: Error description if any
		data: payload
		func: Function being executed
	"""
	def cache_results():
		# cache results. Only save to cache if there is no error
		if not error:
			"""To generate key, use data and not request.data since data contains 
			the original user payload while request.data may have been interfered with 
			when adminlevel one and two ids are appended"""
			set_cache_key(key=cache_key, 
					value=parse_result(res),
					timeout=get_gis_settings().cache_limit)

	"""To generate key, use data and not request.data since data contains 
	the original user payload while request.data may have been interfered with 
	when adminlevel one and two ids are appended"""
	cache_key = generate_cache_key(json.loads(task.orig_args), task.method)
	task.result = parse_result(res) if not error else ""
	task.error = error
	task.succeeded = True if not error else False
	task.status = _("Finished") if not error else _("Failed")
	task.completed_on = timezone.now()
	if not error:
		task.change_enum = str(res['change_enum']) if isinstance(res, dict) else str(json.loads(res)["change_enum"])
	task.save()

	# update ScheduledPreComputation completed and ComputedResults
	if task.scheduled_precomputation:
		from ldms.utils.precomputation_util import complete_job
		complete_job(scheduled_task=task,
	       			cache_key=cache_key,
					success=True if not error else False,
					error=error,
					func=func
				)

	if get_gis_settings().enable_cache:
		cache_results()
		# cache_results(task.orig_args, res, error)
	notify_user(request, task, task.owner)

	# finish monitoring
	doc = MonitoringLog.objects.filter(id=cint(task.id)).first()
	if doc:
		monitoring_util.stop_monitoring(monitoring_log_id=doc.id)

def test_notify_user(request, test_push, **kwargs):
	task = ScheduledTask.objects.get(pk=3543) #.filter(owner="stevenyaga@gmail.com").first()#.get(pk=1)
	task.owner = "stevenyaga@gmail.com"
	if test_push:
		args = task.args or task.orig_args
		args = json.loads(args)	
		args['device_key'] = 'fUpPo2fGSH-hCjisgdGmYF:APA91bHDDlH0JJWUZB7nSbfeABxMlz7U9xKEyBgFKxqC2NX0TrzZ4zh0KkjI8P6q_4VG6QSPmwuuh1OHOd8pWG61hBOckst9VtqlnDJTxgftcrHdvcP1A3BWIbWS7YPMxoIRfd5tTYMg'
		task.args = json.dumps(args)
		task.orig_args = json.dumps(args)

	return notify_user(request, task, "stevenyaga@gmail.com")

def notify_user(request, task, email_addr):

	def _update_notified():
		task.notified_owner = True
		task.notified_on = timezone.now()
		task.message = message
		task.save()
		
	"""Send an email"""
	# During pre-computation, value of HTTP_HOST is not set. But in this context we do not care about the host since its the admin being notified anyway
	current_site = get_current_site(request) if 'HTTP_HOST' in request.META and request.META['HTTP_HOST'] else ''
	user = get_user_model().objects.filter(email=email_addr).first()
	#setts = get_common_settings()
	task_results_url = get_mapped_url(
							url_key='task_results_url', 
							origin=None,
							request=request
					 )
	if task.error:
		task_name = " ".join(task.name.split("_")).title()		
		message = render_to_string('ldms/task_failed.html', {
			'user': user,
			'domain': current_site.domain if current_site else '',
			'endpoint': task_results_url.rstrip("/") + "/" + str(task.id),
			'task': task,
			'task_name': task_name,
			'error': task.error
			})
	else:
		message = render_to_string('ldms/task_complete.html', {
			'user': user,
			'domain': current_site.domain if current_site else '',
			'endpoint': task_results_url.rstrip("/") + "/" + str(task.id),
			'task': task,
			})
	to_email = user.email
	subject = _("Task Completed")

	task.notified_owner = True
	task.notified_on = timezone.now()
	task.message = message
	task.save()
	
	from communication.utils.push_util import send_push_notification
	# check if request came from mobile app
	args = task.args or task.orig_args
	args = json.loads(args)	
	is_mobile = 'device_key' in args
	if is_mobile:		
		res = send_push_notification(user=user,	
								subject=subject,
								message=message, 
								message_type="Scheduled Task Completion", 
								reference_doctype="Scheduled Task", 
								reference_docname=str(task.id),
								arguments=task.args or task.orig_args, 
								method=task.method,
								request=task.request,
								task=task,
								device_id=args['device_key'])
		if res:
			_update_notified()
		return res
	
	# if not to be notified by PUSH, then send email
	res = email_helper.send_email(subject, message, [to_email], 
								message_type="Scheduled Task Completion", 
								reference_doctype="Scheduled Task", 
								reference_docname=str(task.id),
								arguments=task.args or task.orig_args,
								method=task.method,
								request=task.request)
	if res:
		_update_notified()
	return res

@api_view(["GET"])
def forest_fire_qml(request, **kwargs):
	"""
	Get the url of the forest fire qml
	"""
	url = get_download_url(request, "Fire_Severity.qml", use_static_dir=False)
	return Response({ "success": 'true', 'url': url })

@api_view(["GET"])
def search_vector(request, **kwargs):
	params = request.query_params
	query = params.get('query', None)
	result = search_vectors(query=query)
	return Response({ "success": 'true', 'data': result })

# @api_view(['POST'])
def test_queue():
	# Schedule the job with the form parameters
	url = "http://gitlab.com"
	# scheduler = Scheduler(name, interval=interval,
	#                      connection=get_connection(name))
	scheduler = django_rq.get_scheduler('default')
	job = scheduler.schedule(
		scheduled_time=datetime.datetime.now(),
		func=scheduled_get_url_words,
		args=[url],
		interval=10,
		repeat=5,
	)
	# scheduler.schedule(
	# 	scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
	# 	func=func,                     # Function to be queued
	# 	args=[arg1, arg2],             # Arguments passed into function when executed
	# 	kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
	# 	interval=60,                   # Time before the function is called again, in seconds
	# 	repeat=10,                     # Repeat this number of times (None means repeat forever)
	# 	meta={'foo': 'bar'}            # Arbitrary pickleable data on the job itself
	# )
	return Response({ "error": _("Invalid value for raster source") })


@api_view(["GET"])
def test_render(request, **kwargs):
	message = render_to_string('ldms/task_complete.html', {
		'user': {"email": "stev"},
		'domain': "current_site.domain",
		'task': {"id": 3},
	})
	email_helper.send_email("subject", message, ["stevenyaga@gmail.com"],
							message_type="Test", 
							reference_doctype=None, 
							reference_docname=None,
							arguments=None, 
							method=None,
							request=str(request))
	return Response({"message": message})

@job
def add_numbers(a, b):
	return a + b

@job
def scheduled_get_url_words(url):
	"""
	This creates a ScheduledTask instance for each group of
	scheduled task - each time this scheduled task is run
	a new instance of ScheduledTaskInstance will be created
	"""
	import requests
	print ("Starting job execution")
	job = get_current_job()

	task, created = ScheduledTask.objects.get_or_create(
		job_id=job.get_id(),
		name=url
	)
	response = requests.get(url)
	response_len = len(response.text)
	# ScheduledTaskInstance.objects.create(
	#     scheduled_task=task,
	#     result = response_len,
	# )
	print ("Completed job execution")
	return Response({ "error": response_len })
	
