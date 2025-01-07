
from django.utils.translation import gettext as _
from common_gis.utils.raster_util import RasterCalcHelper, reshape_rasters
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

import sys
import os
import json
from common_gis.models import RegionalAdminLevel, AdminLevelZero, AdminLevelOne, AdminLevelTwo
import datetime
from rest_framework.response import Response
from common.utils.common_util import cint, return_with_error
from common.utils.date_util import validate_years
from common.utils.file_util import (get_download_url, 
								get_media_dir, file_exists, get_absolute_media_path)
from common_gis.utils.raster_util import (get_raster_meta, reproject_raster,
								extract_pixels_using_vector, clip_raster_to_vector,
								return_raster_with_stats, get_raster_models, compute_area, generate_tiles)
from common_gis.utils.vector_util import get_vector
import numpy as np
import pandas as pd
import enum
import rasterio
from rasterio.warp import Resampling
from ldms.enums import (LulcCalcEnum, LulcChangeEnum, LCEnum, GenericRasterBandEnum, ForestChangeEnum,
	 RasterSourceEnum, RasterCategoryEnum)
from common_gis.utils.settings_util import get_gis_settings

class LuLcSettings:
	SUB_DIR = "" # "lulc" # Subdirectory to store rasters for lulc

class LULC:
	"""
	Wrapper class for calculating LULC
	"""	

	def __init__(self, **kwargs):
		"""
		Args:
			**admin_level (int)**: 
				The administrative level for the polygon to be used in case a shapefile id has been provided for the parameter **vector**.
			**shapefile_id (int)**: 
				ID of an existing shapefile. 
			**custom_coords (GeoJSON, or GEOSGeometry)**: 
				Coordinates which may be as a result of a custom drawn polygon or a Geometry object in form of GeoJSON.
			**raster_type (int)**:  
				The type of raster files to be used
			**start_year (int)**: 
				Starting year for which raster files should be used. 
			**end_year (int)**: 
				End year for which raster files should be used.  
			**transform (string)**:
				Either of:
					- "area"
					- a string with placeholder e.g x * x to mean square of that value
			**request (Request)**: 
				A Web request object
		""" 
		self.admin_level = kwargs.get('admin_level', None)
		self.shapefile_id = kwargs.get('shapefile_id', None)
		self.custom_vector_coords = kwargs.get('custom_vector_coords', None)
		self.raster_type = kwargs.get('raster_type', None)
		self.start_year = kwargs.get('start_year', None)
		self.end_year = kwargs.get('end_year', None)
		self.transform = kwargs.get('transform', "area")
		self.request = kwargs.get('request', None)
		self.error = None
		self.analysis_type = None #one of LULC or LULC_CHANGE
		self.raster_source = RasterSourceEnum.LULC # kwargs.get('raster_source', RasterSourceEnum.LULC.value)
		#self._set_raster_source(kwargs.get('raster_source'))
		self.enforce_single_year = kwargs.get('enforce_single_year', True)
		self.admin_0 = kwargs.get('admin_0', None)
		self.is_forest_change = kwargs.get('is_forest_change', False)
		self.is_intermediate_variable = kwargs.get('is_intermediate_variable', False) #is to be used as an intermediate variable

		# #matrix to define land change type. The dict key is the base value
		self.transition_matrix = {
			LCEnum.FOREST.key: { "stable": [LCEnum.FOREST.key, LCEnum.WATER.key], 
					"improved": [], 
					"degraded": [LCEnum.GRASSLAND.key, LCEnum.CROPLAND.key, LCEnum.WETLAND.key,
								LCEnum.ARTIFICIAL.key, LCEnum.BARELAND.key]
					},
			LCEnum.GRASSLAND.key: { "stable": [LCEnum.GRASSLAND.key, LCEnum.WATER.key], 
					"improved": [LCEnum.FOREST.key, LCEnum.CROPLAND.key], 
					"degraded": [LCEnum.WETLAND.key, LCEnum.ARTIFICIAL.key, LCEnum.BARELAND.key]
					},
			LCEnum.CROPLAND.key: { "stable": [LCEnum.CROPLAND.key, LCEnum.WATER.key], 
						"improved": [LCEnum.FOREST.key], 
						"degraded": [LCEnum.GRASSLAND.key, LCEnum.WETLAND.key, 
									LCEnum.ARTIFICIAL.key, LCEnum.BARELAND.key]
					},
			LCEnum.WETLAND.key: { "stable": [LCEnum.WETLAND.key, LCEnum.WATER.key], 
					"improved": [], 
					"degraded": [LCEnum.FOREST.key, LCEnum.GRASSLAND.key, 
									LCEnum.CROPLAND.key, LCEnum.ARTIFICIAL.key, LCEnum.BARELAND.key]
					},
			LCEnum.ARTIFICIAL.key: { "stable": [LCEnum.ARTIFICIAL.key, LCEnum.WATER.key], 
					"improved": [LCEnum.FOREST.key, LCEnum.GRASSLAND.key, LCEnum.CROPLAND.key, 
								LCEnum.WETLAND.key, LCEnum.BARELAND.key], 
					"degraded": []
					},
			LCEnum.BARELAND.key: { "stable": [LCEnum.BARELAND.key, LCEnum.WATER.key], 
					"improved": [LCEnum.FOREST.key, LCEnum.GRASSLAND.key, LCEnum.CROPLAND.key, 
								LCEnum.WETLAND.key], 
					"degraded": [LCEnum.ARTIFICIAL.key]
					},
			LCEnum.WATER.key: { "stable": [LCEnum.FOREST.key, LCEnum.GRASSLAND.key, 
									  LCEnum.CROPLAND.key, LCEnum.WETLAND.key, 
									  LCEnum.ARTIFICIAL.key, LCEnum.BARELAND.key, 
									  LCEnum.WATER.key], 
					"improved": [], 
					"degraded": []
					},
		} 

	def _set_raster_source(self, raster_source):
		if isinstance(raster_source, RasterSourceEnum):
			self.raster_source = raster_source
		else:
			vals = [x.value for x in RasterSourceEnum if x.value == raster_source]
			if vals:
				self.raster_source = RasterSourceEnum(vals[0])
			else:
				self.raster_source = RasterSourceEnum.LULC #RasterSourceEnum.LULC # 

	def return_with_error(self, error):		
		self.error = error
		return return_with_error(self.request, error)
	
	def validate_periods(self):
		"""
		Validate the start and end periods

		Returns:
			tuple (Start_Year, End_Year)
		"""		
		start_year = self.start_year
		end_year = self.end_year

		return validate_years(
							start_year=start_year,
							end_year=end_year,
							both_valid=self.analysis_type == LulcCalcEnum.LULC_CHANGE)

	def get_vector(self):
		return get_vector(admin_level=self.admin_level, 
						  shapefile_id=self.shapefile_id, 
						  custom_vector_coords=self.custom_vector_coords, 
						  admin_0=None,
						  request=self.request
						)
	
	def calculate_lulc(self):
		"""
		Compute Land Use Land Cover
		
		Returns:
			[Response]: [A JSON string with statistic values]
		"""    
		
		self.analysis_type = LulcCalcEnum.LULC    
		vector_id = self.shapefile_id
		admin_level = self.admin_level
		raster_type = self.raster_type
		start_year = self.start_year
		end_year = self.end_year
		custom_coords = self.custom_vector_coords
		transform = self.transform
		
		"""
		- If user has drawn custom polygon, ignore the vector id
		since the custom polygon could span several shapefiles.
		- If no custom polygon is selected, demand an admin_level 
		and the vector id
		"""
		vector, error = self.get_vector()
		if error:
			return self.return_with_error(error)

		# Validate that a raster type has been selected
		raster_type = cint(raster_type)
		if not raster_type:
			return self.return_with_error(_("No raster type has been selected"))	

		"""
		Validate analysis periods
		"""
		start_year, end_year, period_error = self.validate_periods()
		if period_error:
			return self.return_with_error(period_error)

		if self.enforce_single_year:
			if start_year != end_year:
				return self.return_with_error(_("LULC can only be analysed for a single period"))

		# Get Raster Models	by period and raster type
		raster_models = get_raster_models(admin_zero_id=self.admin_0,
						raster_category=RasterCategoryEnum.LULC.value,
						raster_source=self.raster_source.value,
						raster_year__gte=start_year, 
						raster_year__lte=end_year)

		if not raster_models:
			return self.return_with_error(_("No matching rasters"))

		if self.enforce_single_year:
			if len(raster_models) > 1:
				return self.return_with_error(_("Multiple LULC rasters exist for the selected period"))
		## looping through models to retrieve the last one??! To do change this	
		raster_model = raster_models[0]
		#raster_path = get_media_dir() + raster_model.rasterfile.name
		raster_path = os.path.join(get_media_dir() + raster_model.rasterfile.name)
			
		# Validate existence of the raster file
		if not file_exists(raster_path):
			return self.return_with_error(_("Raster %s does not exist" % (raster_model.rasterfile.name)))	

		if raster_model.raster_year == start_year:
				clipped_raster, out_meta = clip_raster_to_vector(raster_path, vector)
		
		# this would be the file_path of the clipped raster
		out_file = get_absolute_media_path(file_path=None, 
									is_random_file=True, 
									random_file_prefix = "lulc",
									random_file_ext=".tif",
									sub_dir=LuLcSettings.SUB_DIR,
									use_static_dir=False)

		with rasterio.open(out_file, "w", **out_meta) as dest:
			dest.write(clipped_raster)
		
		change_enum=LCEnum if not self.is_forest_change else ForestChangeEnum,# LulcChangeEnum

		nodata = out_meta["nodata"]

		wms_url, layer = generate_tiles(raster_file=out_file, nodata=nodata, change_enum=change_enum)

		raster_url = "%s" % (get_download_url(self.request, out_file, 
											use_static_dir=False))



		hlper = RasterCalcHelper(vector=vector,
			rasters=raster_models,
			raster_type_id=raster_type,
			stats=[],
			is_categorical=True,
			transform=transform)

		metadata = hlper.get_raster_metadata(raster_model.id)

		#raster_band_stats = rasterstats.zonal_stats_new(vectors=vector, raster=out_file,categorical=True, metadata)

		res = hlper.get_stats_new(vector, out_file,True,metadata)

		stats_obj = {
		# "baseline": "{}-{}".format(baseline_period[0], baseline_period[-1]),
		"base": start_year,
		"target": end_year,
		"rasterfile": raster_url,
		"rasterpath": out_file,
		"precomputed_field_map": {},
		"nodataval": nodata,
		#"nodata": compute_area(nodata_count, resolution),
		"nodata": 0,
		'stats': res,
		'extras': {},
		'change_enum': str(change_enum),
		'tiles': {
			'url': wms_url,
			'layer': layer
		}
		} 
		return stats_obj



		
		

		

	def calculate_lulc_old(self):
		"""
		Compute Land Use Land Cover
		
		Returns:
			[Response]: [A JSON string with statistic values]
		"""    
		
		self.analysis_type = LulcCalcEnum.LULC    
		vector_id = self.shapefile_id
		admin_level = self.admin_level
		raster_type = self.raster_type
		start_year = self.start_year
		end_year = self.end_year
		custom_coords = self.custom_vector_coords
		transform = self.transform
		
		"""
		- If user has drawn custom polygon, ignore the vector id
		since the custom polygon could span several shapefiles.
		- If no custom polygon is selected, demand an admin_level 
		and the vector id
		"""
		vector, error = self.get_vector()
		if error:
			return self.return_with_error(error)

		# Validate that a raster type has been selected
		raster_type = cint(raster_type)
		if not raster_type:
			return self.return_with_error(_("No raster type has been selected"))

		"""
		Validate analysis periods
		"""
		start_year, end_year, period_error = self.validate_periods()
		if period_error:
			return self.return_with_error(period_error)

		if self.enforce_single_year:
			if start_year != end_year:
				return self.return_with_error(_("LULC can only be analysed for a single period"))

		# Get Raster Models	by period and raster type
		raster_models = get_raster_models(admin_zero_id=self.admin_0,
						raster_category=RasterCategoryEnum.LULC.value,
						raster_source=self.raster_source.value,
						raster_year__gte=start_year, 
						raster_year__lte=end_year)

		if not raster_models:
			return self.return_with_error(_("No matching rasters"))

		if self.enforce_single_year:
			if len(raster_models) > 1:
				return self.return_with_error(_("Multiple LULC rasters exist for the selected period"))
		## looping through models to retrieve the last one??! To do change this
	
		for raster_model in raster_models:			
			# for raster_model in raster_models:

			#raster_path = get_media_dir() + raster_model.rasterfile.name
			raster_path = os.path.join(get_media_dir() + raster_model.rasterfile.name)
			
			# Validate existence of the raster file
			if not file_exists(raster_path):
				return self.return_with_error(_("Raster %s does not exist" % (raster_model.rasterfile.name)))

			if raster_model.raster_year == start_year:
				lulc_raster, lulc_raster_path, nodata = clip_raster_to_vector(raster_model.rasterfile.name, vector)
			print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++MMMM+++++++++++++++++++++++++++++++++++++++++++++++",file=sys.stderr)
			print(raster_model,file=sys.stderr)
			print(raster_model.rasterfile.name,file=sys.stderr)
			#print(lulc_raster.rasterfile.name,file=sys.stderr)
			print(lulc_raster_path,'eeeee',nodata,'eeeeeeeeee',file=sys.stderr)
			print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++MMMM+++++++++++++++++++++++++++++++++++++++++++++++",file=sys.stderr)
			
			
		hlper = RasterCalcHelper(vector=vector,
					rasters=raster_models,
					raster_type_id=raster_type,
					stats=[],
					is_categorical=True,
					transform=transform)
		res = hlper.get_stats()

		field_mp = {'custom_string_01': 'raster_id', 'custom_string_02': 'raster_name', 'custom_string_03': 'year'}
		
		#return res
		return return_raster_with_stats(
			request=self.request,
			datasource=lulc_raster[0], # since its a (1, width, height) matrix
			prefix="lulc" if not self.is_forest_change else "forestchange", 
			change_enum=LCEnum if not self.is_forest_change else ForestChangeEnum,# LulcChangeEnum, 
			metadata_raster_path=lulc_raster_path, 
			nodata=nodata, 
			resolution=raster_model.resolution,
			start_year=start_year,
			end_year=end_year,
			subdir=LuLcSettings.SUB_DIR,
			results=res,
			is_intermediate_variable=self.is_intermediate_variable, 
			precomputed_field_map=field_mp
		)

	def calculate_lulc_change(self, return_no_map=False, reference_soc_file=None):
		"""
		Compute Land Use Land Cover Change between two rasters

		Args:
			return_no_map (bool): Determines if mapping will be done or
			only a Pandas dataframe will be returned with column indicies
			`start` and `end`.		
		Returns:
			[Response]: [A JSON string with statistic values]		
		# TODO: Validate the rasters are similar
		"""

		def return_error(error):
			if return_no_map == True:
				self.error = error
				return None, None, None, None, None
			else:
				return self.return_with_error(error) 

		def generate_array(size=(10, 30)):
			return np.random.randint(1, 8, size=size)

		self.analysis_type = LulcCalcEnum.LULC_CHANGE

		# #matrix to define land change type. The dict key is the base value
		transition_matrix = self.transition_matrix 
		
		"""
		Validate analysis periods
		"""
		start_year, end_year, period_error = self.validate_periods()
		if period_error:
			return return_error(period_error)

		# Get rasters
		start_model = get_raster_models(
						admin_zero_id=self.admin_0,
						raster_category=RasterCategoryEnum.LULC.value,	
						raster_source=self.raster_source.value,					
						raster_year=start_year).first()
		if not start_model:
			return return_error(_("No LULC raster is associated with period %s" % (start_year)))
		end_model = get_raster_models(
						admin_zero_id=self.admin_0,
						raster_category=RasterCategoryEnum.LULC.value,
						raster_source=self.raster_source.value,
						raster_year=end_year).first()
		if not end_model:
			return return_error(_("No LULC raster is associated with period %s" % (end_year)))
		
		vector, error = self.get_vector()
		if error:
			return return_error(error)

		# Read the values of the rasters
		meta_raster, meta_raster_path, nodata = clip_raster_to_vector(start_model.rasterfile.name, vector)
		start_arry, nodata, start_rastfile = extract_pixels_using_vector(start_model.rasterfile.name, 
										vector, use_temp_dir=False)

		# Reproject based on the start model
		end_raster_file, nodata = reproject_raster(reference_raster=start_model.rasterfile.name, 
										   raster=end_model.rasterfile.name,
										   vector=vector,
										   resampling=Resampling.average)

		end_arry, nodata, end_rastfile = extract_pixels_using_vector(end_raster_file, 
										vector, use_temp_dir=False)
		
		reference_soc_arry = None
		reference_soc_rastfile = None
		if reference_soc_file:
			# If there is reference_soc_model, Reproject the reference soc with the start period raster
			reference_soc_file, ndata = reproject_raster(reference_raster=start_model.rasterfile.name, 
												raster=reference_soc_file,
												vector=vector,
												resampling=Resampling.average)
			reference_soc_arry, ndata, reference_soc_rastfile = extract_pixels_using_vector(reference_soc_file, vector)
		
		if reference_soc_file:
			start_arry, end_arry, reference_soc_arry = reshape_rasters(rasters=[start_arry, end_arry, reference_soc_arry])
		else:
			start_arry, end_arry = reshape_rasters(rasters=[start_arry, end_arry])
		meta = get_raster_meta(start_model.rasterfile.name)
		df = pd.DataFrame({'base': start_arry.flatten(), 'target': end_arry.flatten()})

		# fill nan with nodata values
		df['change'] = np.full(df['base'].shape, meta['nodata'])

		if return_no_map == True:
			return df, reference_soc_arry, reference_soc_rastfile, nodata, start_model.resolution

		for key in transition_matrix.keys():
			"""
			get where the 'start' is equal to the dict key
			df['base'] contains pixel values for the base period
			df['target'] contains pixel values for the target period
			"""
			stable = transition_matrix[key]['stable']
			improved = transition_matrix[key]['improved']
			degraded = transition_matrix[key]['degraded']
			if stable:
				df.loc[(df['base']==key) & (df['target'].isin(stable)), ['change']] = LulcChangeEnum.STABLE.key # stable
			if improved:
				df.loc[(df['base']==key) & (df['target'].isin(improved)), ['change']] = LulcChangeEnum.IMPROVED.key # improved
			if degraded:
				df.loc[(df['base']==key) & (df['target'].isin(degraded)), ['change']] = LulcChangeEnum.DEGRADED.key # degraded
					
		# convert to old shape
		dataset = df['change'].values.reshape(start_arry.shape)

		return return_raster_with_stats(
			request=self.request,
			datasource=dataset, 
			prefix="lulcchange", 
			change_enum=LulcChangeEnum, 
			metadata_raster_path=meta_raster_path, 
			nodata=nodata, 
			resolution=start_model.resolution,
			start_year=self.start_year,
			end_year=self.end_year,
			subdir=LuLcSettings.SUB_DIR,
			extras={'rasters': {
								start_model.raster_year: get_download_url(request=self.request, file=start_rastfile.split("/")[-1]), 
								end_model.raster_year: get_download_url(request=self.request, file=end_rastfile.split("/")[-1])
							}
						},
			is_intermediate_variable=self.is_intermediate_variable
		)
		
	def get_comparative_rasters(self):
		"""
		Returns a Pandas Dataframe of the values of two comparing 
		periods with indices `start` and `end`
		"""
		pass
