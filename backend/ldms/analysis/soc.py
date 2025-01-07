import rasterio
import numpy as np
import numpy.ma as ma
import pandas as pd
import enum
from django.utils.translation import gettext as _
from rest_framework.response import Response
from ldms.analysis.lulc import LULC, LCEnum
from common_gis.utils.raster_util import (reproject_raster, extract_pixels_using_vector,
			clip_raster_to_vector, return_raster_with_stats, get_raster_models)
from rasterio.warp import Resampling
from common.utils.common_util import cint, return_with_error
from ldms.enums import SOCChangeEnum, LulcChangeEnum, ClimaticRegionEnum, \
		GenericRasterBandEnum, RasterSourceEnum, RasterCategoryEnum
from common_gis.enums import AdminLevelEnum
from common import AnalysisParamError
from django.conf import settings

class SocSettings:
	SUB_DIR = "" # "soc" # Subdirectory to store rasters for soc

class SOC:
	"""
	Wrapper class for Soil Organic Carbon
	"""	
	def __init__(self, **kwargs):
		""" percentage to apply to determine if SOC degraded or not """
		self.cutoff_percentage = kwargs.get('cutoff_percentage', 10) 				
		self.climatic_region = kwargs.get('climatic_region', None)
		self.raster_type = kwargs.get('raster_type', None)
		self.start_year = kwargs.get('start_year', None)
		self.end_year = kwargs.get('end_year', None)
		self.reference_soc = kwargs.get('reference_soc', None)	
		self.raster_source = RasterSourceEnum.LULC #self._set_raster_source(kwargs.get('raster_source')) # kwargs.get('raster_source', RasterSourceEnum.LULC) #
		self.is_intermediate_variable = kwargs.get('is_intermediate_variable', False) #is to be used as an intermediate variable
		
		# self.write_to_disk = kwargs.get('write_to_disk', False)
		self.request = kwargs.get('request', None)
		self.admin_0 = kwargs.get('admin_0', None)
 
		self.initialize_coefficients()
		self.kwargs = kwargs
		self.error = "" 
	
	def _set_raster_source(self, raster_source):
		if isinstance(raster_source, RasterSourceEnum):
			self.raster_source = raster_source
		else:
			vals = [x.value for x in RasterSourceEnum if x.value == raster_source]
			if vals:
				self.raster_source = RasterSourceEnum(vals[0])
			else:
				self.raster_source = RasterSourceEnum.LULC #RasterSourceEnum.LULC # 

	def initialize_coefficients(self):
		# #matrix to define land change type. The dict key is the base value
		self.coefficient_matrix = {}
		for climate in ClimaticRegionEnum:
			if climate != self.climatic_region: #set matrix for the current climatic region
				continue
			self.coefficient_matrix[climate.id] = [
				{
					'base_lc': LCEnum.FOREST.value, 
					'coeffs': {
						LCEnum.FOREST.value: 1, 
						LCEnum.GRASSLAND.value: 1,
						LCEnum.CROPLAND.value: climate.coeff, 
						LCEnum.WETLAND.value: 1,
						LCEnum.ARTIFICIAL.value: 0.1, 
						LCEnum.BARELAND.value: 0.1,
						LCEnum.WATER.value: 1, 
					}
				},
				{
					'base_lc': LCEnum.GRASSLAND.value, 
					'coeffs': {
						LCEnum.FOREST.value: 1, 
						LCEnum.GRASSLAND.value: 1,
						LCEnum.CROPLAND.value: climate.coeff, 
						LCEnum.WETLAND.value: 1,
						LCEnum.ARTIFICIAL.value: 0.1, 
						LCEnum.BARELAND.value: 0.1,
						LCEnum.WATER.value: 1, 
					}
				},
				{
					'base_lc': LCEnum.CROPLAND.value, 
					'coeffs': {
						LCEnum.FOREST.value: 1 / climate.coeff, 
						LCEnum.GRASSLAND.value: 1 / climate.coeff,
						LCEnum.CROPLAND.value: 1, 
						LCEnum.WETLAND.value: 1 / 0.71,
						LCEnum.ARTIFICIAL.value: 0.1, 
						LCEnum.BARELAND.value: 0.1,
						LCEnum.WATER.value: 1, 
					}
				},
				{
					'base_lc': LCEnum.WETLAND.value, 
					'coeffs': {
						LCEnum.FOREST.value: 1, 
						LCEnum.GRASSLAND.value: 1,
						LCEnum.CROPLAND.value: 0.71, 
						LCEnum.WETLAND.value: 1,
						LCEnum.ARTIFICIAL.value: 0.1, 
						LCEnum.BARELAND.value: 0.1,
						LCEnum.WATER.value: 1, 
					}
				},
				{
					'base_lc': LCEnum.ARTIFICIAL.value, 
					'coeffs': {
						LCEnum.FOREST.value: 2, 
						LCEnum.GRASSLAND.value: 2,
						LCEnum.CROPLAND.value: 2, 
						LCEnum.WETLAND.value: 2,
						LCEnum.ARTIFICIAL.value: 1, 
						LCEnum.BARELAND.value: 1,
						LCEnum.WATER.value: 1, 
					}
				},
				{
					'base_lc': LCEnum.BARELAND.value, 
					'coeffs': {
						LCEnum.FOREST.value: 2, 
						LCEnum.GRASSLAND.value: 2,
						LCEnum.CROPLAND.value: 2, 
						LCEnum.WETLAND.value: 2,
						LCEnum.ARTIFICIAL.value: 1, 
						LCEnum.BARELAND.value: 1,
						LCEnum.WATER.value: 1, 
					}
				},
				{              
					'base_lc': LCEnum.WATER.value, 
					'coeffs': {
						LCEnum.FOREST.value: 1, 
						LCEnum.GRASSLAND.value: 1,
						LCEnum.CROPLAND.value: 1, 
						LCEnum.WETLAND.value: 1,
						LCEnum.ARTIFICIAL.value: 1, 
						LCEnum.BARELAND.value: 1,
						LCEnum.WATER.value: 1, 
					}
				},
			]  

	def get_reference_soc_model(self):
		"""
		Determine which ecological unit to use
		"""		
		models = get_raster_models(raster_source=self.raster_source.value,
								   raster_category=RasterCategoryEnum.SOC.value)
		if models:
			# check if there is contintental one
			continental = [x for x in models if x.admin_level == AdminLevelEnum.CONTINENTAL.key]
			if continental:
				return continental[0]
		
		# If no contintental, pull using specified id
		return get_raster_models(id=self.reference_soc).first()

	def calculate_soc_change(self):
		"""
		Calculate SOC
		"""
		if not self.climatic_region:
			return self.return_with_error(_("Specify the climatic region"))

		if type(self.climatic_region) != ClimaticRegionEnum:
			return self.return_with_error(_("Specify a valid value of the climatic region"))
		
		if not self.raster_type:
			return self.return_with_error(_("Specify a valid raster type"))

		if not self.start_year:
			return self.return_with_error(_("Specify a valid start year"))

		if not self.end_year:
			return self.return_with_error(_("Specify a valid end year"))
 
		if not self.reference_soc:
			return self.return_with_error(_("Specify the reference SOC"))

		reference_soc_model = self.get_reference_soc_model() # get_raster_models(id=self.reference_soc).first()
		if not reference_soc_model:
			return self.return_with_error(_("No raster is associated with the reference soc specified [%s]" % (self.reference_soc)))

		
		"""Calculate LULC Change first"""
		lulc = LULC(**self.kwargs)
		df, reference_soc, reference_soc_file, nodata, resolution = lulc.calculate_lulc_change(return_no_map=True, reference_soc_file=reference_soc_model.rasterfile.name)
		if lulc.error:
			return self.return_with_error(lulc.error) 

		vector, error = lulc.get_vector()
		if error:
			return self.return_with_error(error)

		for key in self.coefficient_matrix:
			""" only a single dict expected with key == self.climatic_region"""
			vals = self.coefficient_matrix[key]
			for mapping in vals:
				""" 
				df['base'] contains pixel values for the base period
				df['target'] contains pixel values for the target period
				"""
				for target_lc_key in mapping['coeffs']:
					target_lc_coeff = mapping['coeffs'][target_lc_key]
					initial_val = mapping['base_lc'][0]
					curr_val = target_lc_key[0]
					mask = (df['base']==initial_val) & (df['target']==curr_val)
					df.loc[mask, ['change']] = target_lc_coeff # Assign coefficient value 

					# target_lc_coeff = mapping['coeffs'][target_lc_key]
					# mask = (df['base']==mapping['base_lc']) & (df['target']== target_lc_key)
					# df.loc[mask, ['change']] = target_lc_coeff # Assign coefficient value 

		# base_model = get_raster_models(
		# 				raster_category=RasterCategoryEnum.LULC.value,
		# 				raster_source=self.raster_source.value,
		# 				raster_year=self.start_year).first()
		
		# if not base_model:
		# 	return self.return_with_error(_("No LULC raster is associated with period %s" % (self.start_year)))
		
		# # Reproject the reference soc with the start period raster
		# reference_soc_file, nodata = reproject_raster(reference_raster=base_model.rasterfile.name, 
		# 									  raster=reference_soc_model.rasterfile.name,
		# 									  resampling=Resampling.average)		
		# # reference_soc, nodata = extract_pixels_using_vector(reference_soc_file, 
		# # 								vector)

		# # Clip the raster and save for later referencing
		# meta_raster, meta_raster_path, nodata = clip_raster_to_vector(reference_soc_file, vector)
		
		# reference_soc, nodata, rastfile = extract_pixels_using_vector(meta_raster_path, vector)

		# Reshape the df_change since it had been flattened earlier
		df_change = df['change'].values.reshape(reference_soc.shape) 

		# Multiply the reference_soc with the change as proxied by the df
		# ref_soc_ma = ma.array(reference_soc)
		# change_ma = ma.array(df_change)
		# ref_soc_ma[ref_soc_ma==nodata] = ma.masked
		# change_ma[change_ma==nodata] = ma.masked

		# soc_current = ref_soc_ma * change_ma
		# soc_change = soc_current - ref_soc_ma

		soc_current = reference_soc * df_change

		# Subtract reference_soc from soc_current
		soc_change = soc_current - reference_soc
		
		# Create a new dataframe with new fields
		df_soc_change = pd.DataFrame({'base_soc': reference_soc.flatten(), 'soc_change': soc_change.flatten()})
		
		# change_range = 2 - (-1) # the max range within which the soc can change
		"""
		To get the % change within, we divide the change by the df['base_soc']
		"""
		nodatavalue = nodata
		valid_vals_mask = (df['change'] != nodatavalue) & (~np.isnan(df_soc_change['soc_change']))
		df_soc_change.loc[valid_vals_mask, ['perc_change']] =  np.divide(df_soc_change['soc_change'] * 100,  df_soc_change['base_soc'])
		df_soc_change['mapping'] = np.nan # initialize mapping index

		"""Transpose the change into Stable, Potentially Degraded or Potentially Improved"""
		mask = (df_soc_change['perc_change'] < (-1 * self.cutoff_percentage))
		df_soc_change.loc[mask, ['mapping']] = SOCChangeEnum.DEGRADED.key

		mask = (df_soc_change['perc_change'] > self.cutoff_percentage)
		df_soc_change.loc[mask, ['mapping']] = SOCChangeEnum.IMPROVED.key
		
		"""cutoff<=value<=cutoff"""
		mask = np.logical_and(
						(df_soc_change['perc_change'] >= (-1 * self.cutoff_percentage)),
						(df_soc_change['perc_change'] <= self.cutoff_percentage)
						)
		df_soc_change.loc[mask, ['mapping']] = SOCChangeEnum.STABLE.key
	
		# change the nan into nodatavalue
		df_soc_change.loc[np.isnan(df_soc_change['perc_change']), ['mapping']] = nodatavalue

		# convert to old shape to allow writing a valid raster
		datasource = df_soc_change['mapping'].values.reshape(reference_soc.shape)
		datasource = datasource.astype(np.int32)

		return return_raster_with_stats(
			request=self.request,
			datasource=datasource, 
			prefix="soc", 
			change_enum=SOCChangeEnum, 
			metadata_raster_path=reference_soc_file, #meta_raster_path, 
			nodata=nodata, 
			resolution=resolution, #base_model.resolution,
			start_year=self.start_year,
			end_year=self.end_year,
			subdir=SocSettings.SUB_DIR,
			is_intermediate_variable=self.is_intermediate_variable
		)

	def return_with_error(self, error):		
		self.error = error
		return return_with_error(self.request, error)