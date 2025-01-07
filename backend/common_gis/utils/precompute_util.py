import copy
from common_gis.models import ComputedResult, ComputedResultItem
from common.utils.cache_util import generate_cache_key, get_cache_key
from common_gis.utils.raster_util import return_raster_with_stats
from common_gis.utils.raster_util import extract_pixels_using_vector
from common_gis.utils.vector_util import get_vector_from_db, get_admin_level_ids_from_db
from common.utils.file_util import get_absolute_media_path, get_physical_file_path_from_url, file_exists
from common.utils.common_util import str_to_class
import json


def get_precomputed_result(cache_key, request, computation_type, payload=None):
	"""Get precomputed values from the database
	1. Will start by retrieving computed values using cache key, if it finds a match, return that record
	2. If no match is found, check if have precomputed results for a higher admin level, if it exists, clip that raster and 
	   do the stats
	"""
	def _clear_admin_level_filters(filters):
		if 'continent' in filters: del filters['continent']
		if 'region' in filters: del filters['region']
		if 'admin_zero' in filters: del filters['admin_zero']
		if 'admin_one' in filters: del filters['admin_one']
		if 'admin_two' in filters: del filters['admin_two']
		 
	obj = ComputedResult.objects.filter(cache_key=cache_key).first()
	if obj:
		return json.loads(obj.results)
	else:
		if "admin_level" in payload:            
			admin_level = payload["admin_level"]
			lvl = admin_level # admin_level - 1 #Go one level higher
			continent, region, level_0, level_1, level_2 = get_admin_level_ids_from_db(payload["admin_level"], payload["vector"])
			filters = { key: value
					   for key, value in payload.items()
					   if key in ['start_year', "end_year"] and value
					}
			filters['succeeded'] = 1
			filters['computation_type'] = computation_type.value
			while lvl >= -2: # continental level is -2
				pyload = copy.copy(payload)

				# clear admin level filters
				_clear_admin_level_filters(filters)

				if lvl == -2: # continental
					pyload["vector"] = continent
					pyload["admin_level"] = -2
					filters['continent'] = continent
					
				if lvl == -1: # regional
					pyload["vector"] = region
					pyload["admin_level"] = -1
					filters['region'] = continent

				if lvl == 0: # country
					pyload["vector"] = level_0
					pyload["admin_level"] = 0
					#pyload["admin2"] = None  
					filters['admin_zero'] = level_0

				if lvl == 1: # admin level 1                    
					pyload["vector"] = level_1 # None
					pyload["admin_level"] = 1
					filters['admin_one'] = level_1
				
				if lvl == 2: # admin level 2
					# nothing to change
					pyload["vector"] = level_2
					pyload["admin_level"] = 2
					filters['admin_two'] = level_2

				# Do not filter by cache_key as it might be different from the one used in precomputation. Instead filter by admin levels, year and computation_type
				# key = generate_cache_key(pyload, request.path)
				# obj = ComputedResult.objects.filter(cache_key=key).first()
				obj = ComputedResult.objects.filter(**filters).first()

				if obj:
					vector, error = get_vector_from_db(payload["admin_level"], payload["vector"]) #get vector of the area of interest
					raster_file = get_physical_file_path_from_url(request=request, url=obj.raster_file.name)
					if not file_exists(file_path=raster_file, raise_exception=False):
						return None 
					datasource, nodata, raster_file = extract_pixels_using_vector(raster_file=raster_file, vector=vector, dest_nodata=obj.nodata)
					change_enum = str_to_class(class_name=obj.change_enum, module_name="ldms.enums")
					obj = return_raster_with_stats(request, 
							   datasource=datasource, 
							   prefix=obj.prefix, 
							   change_enum=change_enum, 
							   metadata_raster_path=raster_file, 
							   nodata=nodata, 
							   resolution=obj.resolution,
							   start_year=obj.start_year, 
							   end_year=obj.end_year, 
							   subdir=None, 
							   results=None,
							   extras={}, 
							   is_intermediate_variable=False,
							#    save_precomputed_result=payload["admin_level"]<=0 #save for country level and above
							)
					break
				lvl -= 1 #reduce
		return obj

def get_precomputed_result_OLD(cache_key, request, payload=None):
	"""Get precomputed values from the database
	1. Will start by retrieving computed values using cache key, if it finds a match, return that record
	2. If no match is found, check if have precomputed results for a higher admin level, if it exists, clip that raster and 
	   do the stats
	"""
	obj = ComputedResult.objects.filter(cache_key=cache_key).first()
	if obj:
		return json.loads(obj.results)
	else:
		if "admin_level" in payload:            
			admin_level = payload["admin_level"]
			lvl = admin_level - 1 #Go one level higher
			continent, region, level_0, level_1, level_2 = get_admin_level_ids_from_db(payload["admin_level"], payload["vector"])
			filters = { key: value
					   for key, value in payload.items()
					   if key not in ['admin_level', "continent", "region", "admin0", "admin1", "admin2"]
					}
			while lvl >= -2: # continental level is -2
				pyload = copy.copy(payload)
				if lvl == -2: # continental
					pyload["vector"] = continent
					pyload["admin_level"] = -2
					
				if lvl == -1: # regional
					pyload["vector"] = region
					pyload["admin_level"] = -1

				if lvl == 0: # country
					pyload["vector"] = level_0
					pyload["admin_level"] = 0
					#pyload["admin2"] = None  

				if lvl == 1: # admin level 1                    
					pyload["vector"] = level_1 # None
					pyload["admin_level"] = 1
				
				if lvl == 2: # admin level 2
					# nothing to change
					pyload["vector"] = level_2
					pyload["admin_level"] = 2

				key = generate_cache_key(pyload, request.path)
				obj = ComputedResult.objects.filter(cache_key=key).first()                
				if obj:
					vector, error = get_vector_from_db(payload["admin_level"], payload["vector"]) #get vector of the area of interest
					raster_file = get_absolute_media_path(file_path=obj.raster_file.name)
					datasource, nodata, raster_file = extract_pixels_using_vector(raster_file=raster_file, vector=vector, dest_nodata=obj.nodata)
					change_enum = str_to_class(class_name=obj.computation_type, module_name="ldms.enums")
					obj = return_raster_with_stats(request, 
							   datasource=datasource, 
							   prefix=obj.prefix, 
							   change_enum=change_enum, 
							   metadata_raster_path=raster_file, 
							   nodata=nodata, 
							   resolution=obj.resolution,
							   start_year=obj.start_year, 
							   end_year=obj.end_year, 
							   subdir=None, results=None,
							   extras={}, 
							   is_intermediate_variable=False,
							#    save_precomputed_result=payload["admin_level"]<=0 #save for country level and above
							)
					break
				lvl -= 1 #reduce
		return obj


