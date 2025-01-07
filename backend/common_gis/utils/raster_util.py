from django.db.models.fields import FilePathField
from rasterio import windows
import rasterstats 
from django.utils.translation import gettext as _
import geopandas as gpd
from common.utils.file_util import (file_exists, get_absolute_media_path, 
			get_media_dir, get_download_url, get_temp_file, delete_temp_files)
from common_gis.models import Raster, RasterType, RegionalAdminLevel, AdminLevelZero, ComputedResult, ComputedResultItem
from django.conf import settings
from django.contrib.gis.gdal import GDALRaster
import rasterio
from rasterio.transform import from_origin
import numpy as np
import numpy.ma as ma
import fiona
import rasterio
import rasterio.mask
from rasterio.enums import Resampling
from rasterio.windows import Window
from rasterio.warp import calculate_default_transform, reproject, Resampling
import tempfile
import json
import sys

from common_gis.enums import RasterSourceEnum, GenericRasterBandEnum, MODISBandEnum, \
	Landsat7BandEnum, Landsat8BandEnum, RasterOperationEnum, AdminLevelEnum
from common.utils.common_util import cint, list_to_queryset
from common_gis.utils.settings_util import get_gis_settings
from common_gis.utils.geoserver_util import GeoServerHelper
from common import AnalysisParamError

class RasterCalcHelper():   
	"""
	Helper Class to compute Raster statistics using vector geometries

	Call `get_stats` method to get computed statistics

	Referenced as `RasterCalcHelper().get_stats()`
	
	# TODO: validate the Geometry passed
	# TODO: Optimize for large images
	# TODO: Test that raster extent falls within the vector. Check https://www.earthdatascience.org/courses/use-data-open-source-python/spatial-data-applications/lidar-remote-sensing-uncertainty/extract-data-from-raster/
	"""

	def __init__(self, 
				vector, 
				rasters, 
				raster_type_id, 
				stats=None, 
				is_categorical=True, 
				transform="x",                
				raster_resolution=None):
		"""
		Initialize instance values
		
		Args:
			shapefile:
				Vector data to use to overlay raster on. Either of: 
					- Shapefile path 
					- Geometry either of ["Point", "LineString", "Polygon",
						"MultiPoint", "MultiLineString", "MultiPolygon"]
			rasters (list<Raster>): 
				List of Raster Models
			
			raster_type_id (int):
				Id of the raster types that are being processed

			is_categorical (bool):
				If True, the output of zonal_stats is dictionary with the unique raster values 
				as keys and pixel counts as values

			transform (string):
				Either of:
					- "area"
					- a string with placeholder e.g x * x to mean square of that value
			
			raster_resolution [Deprecated]:
				Resolution of the raster as explicity value if `raster` is set as a path to
				a raster file. If `raster` is set as a reference to a Raster model, the 
				resolution is retrieved from the raster metadata
		"""
		self.vector = vector
		self.rasters = rasters
		self.stats = ['mean']
		self.categorical = is_categorical
		self.raster_band_stats = [] #computed results per rasterband
		# self.raster_resolution = 30 # Resolution of the raster
		self.raster_type_id = raster_type_id # Raster type id
		self.value_placeholder = "x" #placeholder for value in transform equation
		self.transform = transform or self.value_placeholder # how to transform generated stats
		
		# if its categorical, we will just return the count per each category of values
		if is_categorical == True: 
			self.stats = []
	def get_stats_new(self, vector, raster, categorical, metadata):
		"""[summary]
		Because we are interested with the count of individual
		pixel values, we pass the categorical=True parameter
		to force the function to get us results as a dict 
		of the form {1.0: 1, 2.0: 9, 5.0: 40}

		As per the documentation:
		"You can treat rasters as categorical (i.e. raster values represent 
		discrete classes) if you’re only interested in the counts of unique pixel values."

		As per the documentation:
		"Using categorical, the output 
		is dictionary with the unique raster 
		values as keys and pixel counts as values:"

		Returns:
			List of stats for each rasterband.
			   
		"""


		raster_band_stats = rasterstats.zonal_stats(vectors=vector,
							raster=raster,
							categorical=self.categorical) #[1]
		
		mapping = metadata['mapping']# self.get_raster_value_mapping(raster.id)
		resolution = metadata['resolution']

		stats_obj = {
		"mapping": metadata['mapping'],
		'stats': []         
		}

		print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxraster_band_statsxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",file=sys.stderr)	
		print(raster_band_stats,file=sys.stderr)
		print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",file=sys.stderr)
		results = []
		for layer_stats in raster_band_stats: # Loop through the results of each band
			for key in layer_stats.keys():
				if mapping:
					mp = [x for x in mapping if key==x['id']]
					if mp:
						val = layer_stats[key]
						results.append({ 
							"key": key, 
							"label": str(mp[0]['label']),
							"raw_val": val,
							"value": self.transform_value(val, self.rasters[0].id, resolution), 
						})
				else:								
					val = layer_stats[key]
					results.append({ 
						"key": key, 
						"label": str(key),
						"raw_val": val,
						"value": self.transform_value(val, self.rasters[0].id, resolution),
					})

		stats_obj['stats'].append({
			"raster_id": metadata['raster'],
			"raster_name": self.rasters[0].name,
			"resolution": metadata['resolution'],
			'year': metadata['year'],    
			'stats': results,
		})
		print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxstats_objxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",file=sys.stderr)	
		print(stats_obj,file=sys.stderr)
		print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",file=sys.stderr)
		return stats_obj
		

		
	def get_stats(self):
		"""[summary]
		Because we are interested with the count of individual
		pixel values, we pass the categorical=True parameter
		to force the function to get us results as a dict 
		of the form {1.0: 1, 2.0: 9, 5.0: 40}

		As per the documentation:
		"You can treat rasters as categorical (i.e. raster values represent 
		discrete classes) if you’re only interested in the counts of unique pixel values."

		As per the documentation:
		"Using categorical, the output 
		is dictionary with the unique raster 
		values as keys and pixel counts as values:"

		Returns:
			List of stats for each rasterband.
			   
		"""
		# TODO: Retrieve the value of shapefile depending on what has been passed
		# TODO: Retrieve the value of raster and the mapping if necessary

		vectors = self.vector
		if self.is_vector_a_path():
			gdf = gpd.read_file(self.vector)
			vectors = gdf['geometry']

		stats_obj = {
			"mapping": self.get_raster_value_mapping(self.raster_type_id),
			'stats': []         
		}

		for raster in self.rasters: 
			results = []
			raster_path = get_absolute_media_path(raster.rasterfile.name)

			clipped_raster, ndata, rastfile = extract_pixels_using_vector(raster_path, vectors, categorical=True)

			# self.raster_band_stats = rasterstats.zonal_stats(vectors=vectors,
			# 				raster=raster_path,
			# 				categorical=self.categorical) #[1]
			self.raster_band_stats = rasterstats.zonal_stats(vectors=vectors,
							raster=rastfile,
							categorical=self.categorical) #[1]
			
			meta_data = self.get_raster_metadata(raster.id)

			mapping = meta_data['mapping']# self.get_raster_value_mapping(raster.id)
			resolution = meta_data['resolution']
			
			if self.categorical: 
				# we are only getting counts for each unique pixel value for categorical data            
				for layer_stats in self.raster_band_stats: # Loop through the results of each band
					for key in layer_stats.keys():
						if mapping:
							mp = [x for x in mapping if key==x['id']]
							if mp:
								val = layer_stats[key]
								results.append({ 
									"key": key, 
									"label": str(mp[0]['label']),
									"raw_val": val,
									"value": self.transform_value(val, raster.id, resolution), 
								})
						else:								
							val = layer_stats[key]
							results.append({ 
								"key": key, 
								"label": str(key),
								"raw_val": val,
								"value": self.transform_value(val, raster.id, resolution),
							})
			else:
				results = self.raster_band_stats
			
			stats_obj['stats'].append({
				"raster_id": meta_data['raster'],
				"raster_name": raster.name,
				"resolution": meta_data['resolution'],
				'year': meta_data['year'],    
				'stats': results,
			})
		return stats_obj

	def append_metadata(self, results, raster_id):
		"""
		Append Raster metadata to the results

		Args:
			results:
				Results generated from the computations
		"""
		meta_data = self.get_raster_metadata(raster_id)
		return {
			"meta": {
				"raster": meta_data['raster'],
				"resolution": meta_data['resolution'],
				"mapping": meta_data['mapping'],                
			},
			"stats": [{
					'year': meta_data['year'],
					'values': results
				}] 
		}

	def transform_value(self, val, raster_id, raster_resolution=None):
		"""
		Transforms the raster band stat results.
		E.g you can calculate the area covered given the pixel count
		"""
		if self.transform == "area":
			resolution = raster_resolution or self.retrieve_raster_resolution(raster_id)
			# return resolution * resolution * val # multiply resolution squared by pixel count
			return compute_area(val, resolution)
		else:
			return eval(self.transform.replace(self.value_placeholder, str(val)))
	
	def is_vector_a_path(self):
		"""
		Checks if the supplied `shapefile` parameter is a path to a file
		"""
		if self.vector.endswith(".shp"):
			return file_exists(self.vector, raise_exception=False)
		return False
 
	def get_raster_metadata(self, raster_id):
		"""
		Retrieves Raster metadata as stored in the database.

		Args:
			raster_id:
				ID of raster to retrieve metadata for

		Returns:
			Dictionary with the keys:
				`raster`: Name of the raster
				`resolution`: Resolution of the raster
				`mapping`: A dictionary of pixel value with the corresponding label
						E.g {1: "Forest", 2: "Grassland"}  
		"""
		model = Raster.objects.get(id=raster_id)
		mapping = {}
		if model.raster_type:
			mapping = [{"id": x.id, "val": x.value, "label": x.label, "color": x.color} for x in model.raster_type.rastervaluemapping_set.all()]

		meta = {
				"raster": model.id,
				"resolution": model.resolution or 1,
				"year": model.raster_year,
				"mapping": mapping,               
			}
		return meta

	def retrieve_raster_resolution(self, raster_id):
		"""
		Retrieve the resolution of a raster from its stored metadata in 
		the Raster model        
		"""
		meta = self.get_raster_metadata(raster_id)
		return meta['resolution']

	def get_raster_value_mapping(self, raster_type_id):
		"""
		Get a mapping of raster value with the corresponding label
		E.g {1: "Forest", 2: "Grassland"}

		Args:
			raster_type_id:
				Id of the raster type to retrieve metadata for
		"""
		model = RasterType.objects.get(id=raster_type_id)
		mapping = [{"id": x.id, "val": x.value, "label": x.label, "color": x.color} for x in model.rastervaluemapping_set.all()]
		return mapping

def get_band_number(band, raster_source):
	"""
	Determine the band number depending on the raster source (Landsat7, Landsat8, MODIS)
	Args:
		band (GenericRasterBandEnum): Band of the raster to be read. Valid RasterBandEnum value.
			  If image has single band, then pass band=GenericRasterBandEnum.LULC.	
		raster_source (RasterSourceEnum): Source of the raster. A valid value of RasterSourceEnum
	"""
	if raster_source == RasterSourceEnum.LULC:
		return 1
	
	band_map = {
		RasterSourceEnum.MODIS.value : { #modis
			GenericRasterBandEnum.RED.value: MODISBandEnum.RED.value,
			GenericRasterBandEnum.GREEN.value: MODISBandEnum.GREEN.value,
			GenericRasterBandEnum.BLUE.value: MODISBandEnum.BLUE.value,
			GenericRasterBandEnum.NIR.value: MODISBandEnum.NIR.value,
			GenericRasterBandEnum.SWIR1.value: MODISBandEnum.SWIR1.value,
		},
		RasterSourceEnum.LANDSAT7.value : { #landsat7
			GenericRasterBandEnum.RED.value: Landsat7BandEnum.RED.value,
			GenericRasterBandEnum.GREEN.value: Landsat7BandEnum.GREEN.value,
			GenericRasterBandEnum.BLUE.value: Landsat7BandEnum.BLUE.value,
			GenericRasterBandEnum.NIR.value: Landsat7BandEnum.NIR.value,
			GenericRasterBandEnum.SWIR1.value: Landsat7BandEnum.SWIR1.value,
		},
		RasterSourceEnum.LANDSAT8.value : { #landsat8
			GenericRasterBandEnum.RED.value: Landsat8BandEnum.RED.value,
			GenericRasterBandEnum.GREEN.value: Landsat8BandEnum.GREEN.value,
			GenericRasterBandEnum.BLUE.value: Landsat8BandEnum.BLUE.value,
			GenericRasterBandEnum.NIR.value: Landsat8BandEnum.NIR.value,
			GenericRasterBandEnum.SWIR1.value: Landsat8BandEnum.SWIR1.value,
		}
	}
	# return the band value depending on the source
	return band_map[raster_source.value][band.value]

def get_raster_values(raster_file, band, raster_source, windowed=False):
	"""Get raster values
	
	Args:
		raster_file (string): path of the raster file
		band (GenericRasterBandEnum): Band of the raster to be read. Valid GenericRasterBandEnum value.
			  If image has single band, then pass band=GenericRasterBandEnum.HAS_SINGLE_BAND.	
		raster_source (RasterSourceEnum): Source of the raster. A valid value of RasterSourceEnum		
		windowed (bool): Specifies if raster file is to be read in blocks. This 
			is needed for large files

	Returns:
		A numpy array	
	"""

	def get_file_path(raster_file):
		if file_exists(raster_file, raise_exception=False):
			return raster_file
		else:
			raster_file = get_media_dir() + raster_file
			if file_exists(raster_file, raise_exception=True):
				return raster_file
		return None

	# if type(band) != GenericRasterBandEnum:
	# 	raise AnalysisParamError(_("The band specified is invalid. Ensure the type is GenericRasterBandEnum"))
	# if type(raster_source) != RasterSourceEnum:
	# 	raise AnalysisParamError(_("The raster source specified is invalid. Ensure the type is RasterSourceEnum"))
	
	band_to_read = 1 # get_band_number(band=band, raster_source=raster_source)
	file = get_file_path(raster_file)
	if file:
		use_rasterio = True
		if not use_rasterio:        
			rst = GDALRaster(file, write=False)
			return rst.bands[band_to_read].data()
		else:
			if not windowed:
				dataset = rasterio.open(file)
				return dataset.read(1)
			else:				
				with rasterio.open(file) as src:
					"""	
					Well-bred files have identically blocked bands, 
					but GDAL allows otherwise and it's a good idea to test this assumption.
					The block_shapes property is a band-ordered list of block shapes and 
					set(src.block_shapes) gives you the set of unique shapes. Asserting that 
					there is only one item in the set is effectively the same as asserting 
					that all bands have the same block structure. If they do, you can use 
					the same windows for each.
					"""
					results_array = None
					assert len(set(src.block_shapes)) == 1
					for ji, window in src.block_windows(1):
						r = src.read(1, window=window)
						if ji == (0, 0): # first loop, initialize the numpy array
							results_array = np.array(r)
						else:
							results_array = np.append(results_array, r)
						# b, g, r = (src.read(k, window=window) for k in (1, 2, 3))
						# print((ji, r.shape, g.shape, b.shape))
						# break

					# for ji, window in src.block_windows(1):
					# 	b, g, r = (src.read(k, window=window) for k in (1, 2, 3))
					# 	print((ji, r.shape, g.shape, b.shape))
					# 	break
				return results_array
	return None

def get_raster_object(raster_file):
	"""Get Raster object metadata using the file
	"""
	if file_exists(raster_file, raise_exception=False):
		return GDALRaster(raster_file, write=False)
	else:
		raster_file = get_media_dir() + raster_file
		if file_exists(raster_file, raise_exception=True):
			return GDALRaster(raster_file, write=False)
	return None

# def save_raster(dataset, source_path, target_path, cols, rows, projection, geotransform):
# 	# geotransform = B5_2014.GetGeoTransform()
# 	# rasterSet = gdal.GetDriverByName('GisiTiff').Create(target_path, cols, rows, 1, gdal.GDT_Float32)
# 	# rasterSet.SetProjection(projection)
# 	# rasterSet.SetGeoTransform(geotransform)
# 	# rasterSet.GetRasterBand(1).WriteArray(dataset)
# 	# rasterSet.GetRasterBand(1).SetNoDataValue(-999)
# 	# rasterSet = None
# 	new_dataset = rasterio.open(target_path, 'w', driver='GTiff',
# 						height = rows, width = cols,
# 						count=1, dtype=dataset.dtype, #str(arr.dtype),
# 						crs='+proj=utm +zone=10 +ellps=GRS80 +datum=NAD83 +units=m +no_defs') #,
# 						# transform=geotransform)
# 	new_dataset.write(dataset, 1)
# 	new_dataset.close()

# 	raster = rasterio.open(source_path)
# 	profile = raster.meta

# 	array = ""
# 	with rasterio.open(rasterin) as src:
# 		meta = src.meta
# 		array = src.read(1)

# 	with rasterio.open(rasterout, 'w', **profile) as dst:
# 		dst.write(array.astype(rasterio.uint8), 1)

def get_raster_meta(rasterfile, set_default_nodata=True, default_nodata=settings.DEFAULT_NODATA):
	"""
	Get RasterFile metadata
	"""
	rasterin = get_absolute_media_path(rasterfile)
	with rasterio.open(rasterin) as src:
 		meta = src.meta

	if set_default_nodata:
		if 'nodata' not in src.meta or src.meta.get('nodata', None) == None:
			meta.update({'nodata': default_nodata})
		# if nodatavalue not within int range, set to default value
		nodataval = meta['nodata']
		if not (settings.MIN_INT <= nodataval <= settings.MAX_INT):
			meta.update({'nodata': default_nodata})
		elif isinstance(nodataval, float):
			meta.update({'nodata': default_nodata})

	return meta

def harmonize_raster_nodata(arry, file, ref_file):
	"""Read raster values while harmonizing the nodata values to ensure they are consistent

	Args:
		arry (array): Array whose nodata values we want to harmonize
		file (string): File path of the raster we want to read values from
		ref_file (string): File path of the raster whose nodata values we want to use 

	Returns:
		[array]: Array of harmonized values
	"""
	meta = get_raster_meta(get_absolute_media_path(file))
	nodata = meta.get('nodata')

	base_meta = get_raster_meta(get_absolute_media_path(ref_file))
	base_nodata = base_meta.get('nodata')
	values = np.where(arry == nodata, base_nodata, arry)
	return values

def save_raster(dataset, source_path, target_path, dtype=rasterio.int16, no_data=None):	
	"""
	Write raster dataset to disk

	Args:
		source_path (string): Path of raster where we will get the Metadata
		target_path (string): Path to save the raster
	"""
	rasterin = get_absolute_media_path(source_path.replace("//", "/"), use_static_dir=False)
	rasterout = target_path.replace("//", "/")
 
	# open source to extract meta
	meta = get_raster_meta(rasterin) 
	meta.update({
				 'dtype': dtype, # rasterio.uint8,
				 'compress': 'lzw',
				 'height': dataset.shape[0],
				 'width': dataset.shape[1],				 
				})	
	if no_data:
		meta.update({
			"nodata": no_data
		})
	nodata = override_nodata(meta['nodata'])
	meta.update({"nodata": nodata})
	with rasterio.open(rasterout, 'w', **meta) as dst:		
		# dst.write(dataset.astype(rasterio.uint8), 1)
		if len(dataset.shape) == 2:
			dst.write(dataset.astype(dtype), 1)
		else:
			dst.write(dataset.astype(dtype))
		
	"""
	bands = [x + 1 for x in list(range(rast.count))]
	rast.close()
	badbands = [7, 16, 25]

	nodatavalue = 255
	with rasterio.open(rasterout, 'w', **meta) as dst:
		with rasterio.open(rasterin) as src:
			for ID, b in enumerate(bands,1):
				# if b in ndvibands:
				# 	ndvi = src.read(b)
				# 	ndvi[ndvi != 0] = 0
				# 	dst.write(ndvi, ID)
				# else:
				data = src.read(b, masked=True)
				data = np.ma.filled(data, fill_value=nodatavalue)
				#data[data == 2] = 0
				dst.write(data, ID)
	dst.close
	"""
	return target_path.split("/")[-1]

def reproject_raster(reference_raster, raster, vector, resampling=Resampling.average, set_default_nodata=True, default_nodata=settings.DEFAULT_NODATA, force=False):
	"""Checks if the CRS is the same, if not, reprojection is done.
	   Checks if extents are the same, if not clip or otherwise
	   Checks if resolution is the same, if not, resample

	Args:
		reference_raster (string): Reference raster to use as the base
		raster (string): Target raster that may need reprojection
		resampling (enum): One of the enumerated Rasterio Resampling methods

	Returns:
		(path, nodata): Tuple containing the path to the saved file and the value of nodata value
	"""
	ref_path = get_absolute_media_path(reference_raster)
	if reference_raster == raster: # if same file, do not reproject
		with rasterio.open(ref_path) as ref_file:
			ref_nodata = ref_file.meta.get('nodata') or default_nodata
		return raster, ref_nodata

	resampling = resampling or Resampling.nearest # default to Resampling.nearest

	dst_path = get_absolute_media_path(raster)
	if settings.REPROJECTION_METHOD == 2:
		# clip then reproject
		# Clip the reference raster
		clipped_ref_raster, nodata, clipped_ref_raster_path = extract_pixels_using_vector(ref_path, vector, dest_nodata=default_nodata)	
		ref_path = get_absolute_media_path(clipped_ref_raster_path)

		# Clip the dest raster
		clipped_dest_raster, nodata, clipped_dest_raster_path = extract_pixels_using_vector(dst_path, vector, dest_nodata=default_nodata)	
		dst_path = get_absolute_media_path(clipped_dest_raster_path)
	
	trigger_reproject = False
	ref_nodata = None
	with rasterio.open(ref_path) as ref_file:
		ref_nodata = ref_file.meta.get('nodata') or default_nodata
		with rasterio.open(dst_path) as raster_src:
			src_affine, raster_affine = ref_file.meta['transform'], raster_src.meta['transform']
			src_resolution = [src_affine[0], -src_affine[4]]
			dst_resolution = [raster_affine[0], -raster_affine[4]]
		
			if ref_file.crs != raster_src.crs:
				# reproject
				trigger_reproject = True
				
			if ref_file.shape != raster_src.shape:
				# clip or otherwise	
				trigger_reproject = True

			if ref_file.transform != raster_src.transform: #transformation contains resolution
				# resample
				trigger_reproject = True
			
			if trigger_reproject or force:
				dst_crs = ref_file.crs
				transform, width, height = calculate_default_transform(
							ref_file.crs, dst_crs, ref_file.width, ref_file.height, *ref_file.bounds)
				kwargs = ref_file.meta.copy()
				kwargs.update({
					'crs': dst_crs,
					'transform': transform,
					'width': width,
					'height': height,
					'compress': 'lzw',
					'nodata': ref_nodata
				})

				dest_file = tempfile.NamedTemporaryFile(delete=False)
				with rasterio.open(dest_file.name, 'w', **kwargs) as new_raster:
					# for i in range(1, ref_file.count + 1): # Read all bands
					ref_nodata = ref_nodata if not set_default_nodata else default_nodata
					for i in range(1, 2): # read only the first band
						reproject(
							source=rasterio.band(raster_src, i),
							destination=rasterio.band(new_raster, i),
							src_transform=ref_file.transform,
							src_crs=ref_file.crs,
							dst_transform=transform,
							dst_crs=dst_crs,
							dst_nodata=ref_nodata,
							resampling=resampling)
				
				raster = dest_file.name

	return raster, ref_nodata

def return_raster_with_stats(request, datasource, prefix, change_enum, 
							   metadata_raster_path, nodata, resolution,
							   start_year, end_year, subdir=None, results=None,
							   extras={}, is_intermediate_variable=False, 
							   precomputed_field_map={}):
	"""Generates a raster and computes the statistics

	Args:
		request (request): Http Request
		datasource (array): Raster array to save
		prefix (string): Name to prefix the generated raster with
		change_enum (enum.Enum): Type of Enumeration for different changes 
								e.g ProductivityChangeTernaryEnum, TrajectoryChangeTernaryEnum
		metadata_raster_path (string): Path of the raster where to get Metadata from
		nodata (int): Value of nodata
		resolution (int): Resolution to use to compute statistics
		subdir (string): Name of sub directory to save the raster
		results (object): An object already containing calculated values
		extras (dict): Extra key value object that you may want to return in addition to std values
		is_intermediate_variable: True if the results are to be used as an intermediate value not the final value
		precomputed_field_map: Dict of how extra values of statistics will be stored. An example is ForestChange and LULC which has additional values for the results

	Returns:
		object : An object with url to download the generated raster and
					statistics categorized by the change_enum 
	"""
	# TODO validate change_enum
	# if type(change_enum) not in [StateChangeTernaryEnum, PerformanceChangeBinaryEnum, ProductivityChangeTernaryEnum]:
	# 	raise AnalysisParamError(_("The change enum source specified is invalid. Ensure it is a valid enumeration"))
	print("(((((((((((((((((((((())))))))))))))))))))))",file=sys.stderr)
	delete_temp_files(extension=".tif", age_in_seconds=settings.DELETE_TEMP_FILES_AFTER or 86400)

	out_file = get_absolute_media_path(file_path=None, 
									is_random_file=True, 
									random_file_prefix=prefix,
									random_file_ext=".tif",
									sub_dir=subdir,
									use_static_dir=False)

	raster_file = save_raster(dataset=datasource, 
				source_path=metadata_raster_path,
				target_path=out_file)
	
	raster_url = "%s" % (get_download_url(request, raster_file, 
											use_static_dir=False))
	results = results or []		
	
	# Get counts of change types		
	# unique, counts = np.unique(datasource[datasource != nodata], return_counts=True)			
	unique, counts = np.unique(datasource, return_counts=True)			
	val_counts = dict(zip(unique, counts)) # convert to {val:count} freq distribution dictionary
	print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", val_counts, file=sys.stderr)
	if not results:
		for mapping in change_enum:
			key = cint(mapping.key)
			if key in val_counts:
				val = val_counts[mapping.key]
				results.append({
					'change_type': key,
					'label': str(mapping.label),
					'count': val,
					'area': compute_area(val, resolution)
				})
			else:
				results.append({
					'change_type': key,
					'label': str(mapping.label),
					'count': 0,
					'area': 0
				})

	nodata_count = 0 
	if nodata in val_counts:
		nodata_count = val_counts[nodata]

	wms_url, layer = None, None
	if not is_intermediate_variable and get_gis_settings().enable_tiles:
		wms_url, layer = generate_tiles(raster_file=out_file, nodata=nodata, change_enum=change_enum)

	stats_obj = {
			# "baseline": "{}-{}".format(baseline_period[0], baseline_period[-1]),
			"base": start_year,
			"target": end_year,
			"rasterfile": raster_url,
			"rasterpath": raster_file,
			"precomputed_field_map": precomputed_field_map,
			"nodataval": nodata,
			"nodata": compute_area(nodata_count, resolution),
			'stats': results,
			'extras': extras,
			'change_enum': str(change_enum),
			'tiles': {
				'url': wms_url,
				'layer': layer
			}
		} 
	print("*************************************************************************", stats_obj, file=sys.stderr)
	return stats_obj      

def generate_tiles_old(raster_file, nodata, change_enum):
	"""Generate Tiles

	Args:
		raster_file (string): Raster file
		nodata (number): Nodata value
		change_enum (enum.Enum): Type of Enumeration for different changes 
								e.g ProductivityChangeTernaryEnum, TrajectoryChangeTernaryEnum
	Returns:
		Returns a WMS url
	""" 	
	geo = GeoServerHelper(analysis_enum=change_enum, nodata=nodata)
	return geo.upload_raster(raster_file) 

def generate_tiles(raster_file, nodata, change_enum):
	"""Generate Tiles

	Args:
		raster_file (string): Raster file
		nodata (number): Nodata value
		change_enum (enum.Enum): Type of Enumeration for different changes 
								e.g ProductivityChangeTernaryEnum, TrajectoryChangeTernaryEnum
	Returns:
		Returns a WMS url
	""" 
	wms_url, layer = None, None
	if get_gis_settings().enable_tiles:	
		geo = GeoServerHelper(analysis_enum=change_enum, nodata=nodata)
		wms_url, layer = geo.upload_raster(raster_file)
	return (wms_url, layer)

def test_generate_tiles(raster_file, 
			nodata, change_enum):
	return generate_tiles(raster_file=raster_file or "/home/sftdev/django-apps/oss-ldms/backend/media/LC_2000.tif", 
							nodata=nodata or 255, 
							change_enum=change_enum)

def test():	
	x = np.array([1, 2, 3])
	y =  np.array([4, 5, 6])
	nodata = 255
	add =  do_raster_operation([x, y], RasterOperationEnum.ADD, nodata)
	sub =  do_raster_operation([x, y], RasterOperationEnum.SUBTRACT, nodata)
	div =  do_raster_operation([x, y], RasterOperationEnum.DIVIDE, nodata)

def do_raster_operation(rasters, operation, nodata):
	"""Perform operations on rasters

	Args:
		rasters (list): List of rasters
		operation (RasterOperationEnum): Type of operation

	# TODO validate projection/extent/resolution
	"""
	res = None
	if isinstance(rasters, list):
		if operation == RasterOperationEnum.DIVIDE and len(rasters) != 2:
			raise AnalysisParamError(_("The list must contain only 2 arrays"))
		
		masked_rasters = []
		# Mask nodata values
		for i, itm in enumerate(rasters):
			# loop because np.ma.<arithmetic> replaces the masked values
			itm = ma.array(itm, fill_value=nodata)
			itm[itm==nodata] = ma.masked
			masked_rasters.append(itm)

			if i == 0:
				res = itm
			else:
				if operation == RasterOperationEnum.ADD:
					res = np.ma.add(res, itm)
				elif operation == RasterOperationEnum.SUBTRACT:
					res = np.ma.subtract(res, itm)
				elif operation == RasterOperationEnum.MULTIPLY:
					res = np.ma.multiply(res, itm)
				elif operation == RasterOperationEnum.DIVIDE:
					res = np.ma.divide(res, itm)
		
		# if operation == RasterOperationEnum.ADD:
		# 	res = np.add.reduce(masked_rasters)
		# elif operation == RasterOperationEnum.SUBTRACT:
		# 	res = np.subtract.reduce(masked_rasters)
		# elif operation == RasterOperationEnum.MULTIPLY:
		# 	res = np.multiply.reduce(masked_rasters)
		# elif operation == RasterOperationEnum.DIVIDE:
		# 	res = np.divide(masked_rasters[0], masked_rasters[1])
	
	return res

	# res = None
	# if isinstance(rasters, list):
	# 	if len(rasters) == 2: # operation on only multiple rasters	
	# 		rast1 = ma.array(rasters[0])			
	# 		rast1[rast1==nodata] = ma.masked
	# 		rast2 = ma.array(rasters[1])			
	# 		rast2[rast2==nodata] = ma.masked

	# 		if operation == RasterOperationEnum.ADD:
	# 			res = np.add(rast1, rast2)
	# 		elif operation == RasterOperationEnum.SUBTRACT:
	# 			res = np.subtract(rast1, rast2)
	# 		elif operation == RasterOperationEnum.DIVIDE:
	# 			res = np.divide(rast1, rast2)		
	# 	else:
	# 		raise AnalysisParamError(_("The list must contain only 2 arrays"))
	# return res

def resample_raster(raster_file, scale=2):
	"""
	Resample a raster file.

	Args:
		raster_file (string): Path to the raster file
	See https://gis.stackexchange.com/questions/368069/rasterio-window-on-resampling-open
	"""
	reference_file_path = get_absolute_media_path("LC_2007.tif")
	file_path_to_resample = get_absolute_media_path("LC_2008.tif")
	path_to_output = get_absolute_media_path("LC2007_2008get_raster_object.tif")
	# Open the datasets once
	# Load the reference profile
	with rasterio.open(reference_file_path) as src, rasterio.open(file_path_to_resample) as dst:
		profile = src.profile
		blocks = list(src.block_windows())
		height, width = src.shape
		result = np.full((height, width), dtype=profile['dtype'], fill_value=profile['nodata'])

		# Loop on blocks
		for _, window in blocks:
			row_offset = window.row_off + window.height
			col_offset = window.col_off + window.width

			# open image block
			src_values = src.read(
				1,
				masked=True,
				window=window
			)
			print (src_values)

			# Resample the window
			res_window = Window(window.col_off / scale, window.row_off / scale,
								window.width / scale, window.height / scale)

			try:
				dst_values = dst.read(
					out_shape=(
						src.count,
						int(window.height),
						int(window.width)
					),
					resampling=Resampling.average,
					masked=True,
					window=res_window
				)
			except:
				break

			print(dst_values.shape)

			# Do computations here e.g subtract the values
			result[window.row_off: row_offset, window.col_off: col_offset] = src_values + dst_values

	# Write result on disc
	with rasterio.open(path_to_output, 'w', **profile) as dataset:
		dataset.write_band(1, result)

	# path = get_absolute_media_path(raster_file)
	# with rasterio.open(path) as dataset:
	# 	# resample data to target shape
	# 	data = dataset.read(
	# 		out_shape=(
	# 			dataset.count,
	# 			int(dataset.height * scale),
	# 			int(dataset.width * scale)
	# 		),
	# 		resampling=Resampling.average
	# 	)

	# 	# scale image transform
	# 	transform = dataset.transform * dataset.transform.scale(
	# 		(dataset.width / data.shape[-1]),
	# 		(dataset.height / data.shape[-2])
	# 	)

def clip_raster_to_regional_vector(raster_file):
	"""
	Clip raster to only include values inside the regional vector
	"""
	regional_vector = RegionalAdminLevel.objects.all().first()
	if regional_vector:
		return clip_raster_to_vector(vector=json.loads(regional_vector.geom.geojson),
					raster_file=raster_file)		
	return raster_file

def clip_rasters(vector, models, ref_model=None, raise_file_missing_exception=True):
	"""Clip all rasters using the vector

	Args:
		vector (geojson): Polygon to be used for clipping
		models (List): Models whose raster files should be clipped
	
	Returns:
		tuple (nodata, list[raster, raster_file])
	"""
	res = []
	if not isinstance(models, list):
		models = [models]
	#meta = get_raster_meta(models[0].rasterfile.name)
	meta = get_raster_meta(ref_model.rasterfile.name) if ref_model else get_raster_meta(models[0].rasterfile.name)
	dest_nodata = override_nodata(meta['nodata'])
	for i, model in enumerate(models):
		if model:
			if file_exists(get_absolute_media_path(model.rasterfile.name), raise_exception=raise_file_missing_exception):
				out_image, out_file, out_nodata = clip_raster_to_vector(model.rasterfile.name, 
												vector, use_temp_dir=True, 
												dest_nodata=dest_nodata)
				res.append([out_image, out_file])
			else:
				res.append([None, None])
		else:
			res.append([None, None])
	return (dest_nodata, res)

def mask_rasters(rasters, nodata):
	"""Clip all rasters using the vector

	Args:
		vector (geojson): Polygon to be used for clipping
		models (List): Models whose raster files should be clipped
	
	Returns:
		tuple (nodata, list[raster, raster_file])
	"""
	res = []
	if not isinstance(rasters, list):
		rasters = [rasters]
	for i, raster in enumerate(rasters):
		# is_masked = isinstance(rasters, ma.MaskedArray)
		arry = ma.array(raster)
		arry[arry==nodata] = ma.masked 
		res.append(arry)
	return res

def clip_raster_to_vector(raster_file, vector, dest_nodata=None):
	"""
	Mask out regions of a raster that are outside the polygons defined in the shapefile.

	Args:
		raster_file: absolute raster_path
		vector (geojson): Polygon to be used for clipping
		dest_nodata (number): Value to set as nodata when returning the clipped raster
	
	Returns (array): Tuple of the clipped raster array (image?) and metatdata
	"""
	
	
		
	all_touched = get_gis_settings().raster_clipping_algorithm == "All Touched"
	# read the file and crop areas outside the polygon
	with rasterio.open(raster_file) as src:
		nodata = dest_nodata if dest_nodata != None else src.meta['nodata'] or settings.DEFAULT_NODATA
		out_image, out_transform = rasterio.mask.mask(src, 
					[json.loads(vector)], # accepts array of shapes
					all_touched=all_touched,
					nodata=nodata,
					crop=True)
		out_meta = src.meta
	
	# update meta
	out_meta.update({"driver": "GTiff",
				"height": out_image.shape[1],
				"width": out_image.shape[2],
				"transform": out_transform
	})

	# enable compress
	out_meta.update({'compress': 'lzw'})

	# update nodata
	out_meta.update({'nodata': nodata})

	return (out_image, out_meta)

def clip_raster_to_vector_old(raster_file, vector, use_temp_dir=True, dest_nodata=None):
	"""
	Mask out regions of a raster that are outside the polygons defined in the shapefile.

	Args:
		vector (geojson): Polygon to be used for clipping
		dest_nodata (number): Value to set as nodata when returning the clipped raster
	
	Returns (string, array): Tuple of Url of the clipped raster and the raster array
	"""
	
	file = get_absolute_media_path(raster_file)
	if not file_exists(file):
		return (None, None)
		
	all_touched = get_gis_settings().raster_clipping_algorithm == "All Touched"
	# read the file and crop areas outside the polygon
	with rasterio.open(file) as src:
		nodata = dest_nodata if dest_nodata != None else src.meta['nodata'] or settings.DEFAULT_NODATA
		out_image, out_transform = rasterio.mask.mask(src, 
					[json.loads(vector)], # accepts array of shapes
					all_touched=all_touched,
					nodata=nodata,
					crop=True)
		out_meta = src.meta
	print("-----------------OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO------------",file=sys.stderr)	
	print(src.meta ,file=sys.stderr)
	print("-----------------OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO------------",file=sys.stderr)
	
	# update meta
	out_meta.update({"driver": "GTiff",
				"height": out_image.shape[1],
				"width": out_image.shape[2],
				"transform": out_transform
	})

	# enable compress
	out_meta.update({'compress': 'lzw'})

	# update nodata
	out_meta.update({'nodata': nodata})

	# print("-----------------OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO------------",file=sys.stderr)	
	# print(out_image.meta ,file=sys.stderr)
	# print("-----------------OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO------------",file=sys.stderr)
	# get output file
	if use_temp_dir:
		out_file = get_temp_file(suffix=".tif")
	else:
		out_file = get_absolute_media_path(file_path=None, 
									is_random_file=True, 
									random_file_prefix="",
									random_file_ext=".tif")

	print("----------------------------------------------------------------------------",file=sys.stderr)	
	print(out_file ,file=sys.stderr)
	print("----------------------------------------------------------------------------",file=sys.stderr)
									
	with rasterio.open(out_file, "w", **out_meta) as dest:
		dest.write(out_image)
	return (out_image, out_file, out_meta['nodata'])

def extract_pixels_using_vector(raster_file, vector, categorical=False, use_temp_dir=True, dest_nodata=None):
	"""
	Extracts pixels covered by a vector
	Args:
		raster (string or array): Raster file or raster array
		vector (GeoJSON): GeoJSON string
		nodata: Value to use for nodata
		use_temp_dir: If True, the resulting raster will be stored in /tmp directory, else in the media directory
	Returns:
		tuple(array, nodata, file): Raster, value of nodata, filepath of the generated raster
	"""
	array, file, nodata = clip_raster_to_vector(raster_file, vector, use_temp_dir=use_temp_dir, dest_nodata=dest_nodata)
	return (array[0], nodata, file)
	"""
	if type(raster_file) == str:	
		file = get_absolute_media_path(raster_file)	
		if not file_exists(file):
			return (None, None)
	else:
		file = raster_file
	raster_stats = rasterstats.zonal_stats(vectors=vector,
						raster=file,
						categorical=categorical,
						all_touched=True,
						nodata=nodata,
						raster_out=True)
	return (raster_stats[0]['mini_raster_array'], raster_stats[0]['mini_raster_nodata']) 
	"""

	# bounds = json.loads(vector)['geometry']["bbox"]
	# if file_exists(file):
	# 	with rasterstats.io.Raster(raster=file, nodata=nodata) as raster_obj:
	# 		raster_subset = raster_obj.read(bounds=vector)
	# 		nodata = raster_obj.nodata
	# 	return (raster_subset, nodata)

def segment_and_concatenate(matrix, func=None, block_size=(16,16), overlap=(0,0), nodata=settings.DEFAULT_NODATA):
	"""Truncate matrix to a multiple of block_size. 
	Truncates the matrix to size that will be equally divisible by the block size
	
	See https://stackoverflow.com/questions/5073767/how-can-i-efficiently-process-a-numpy-array-in-blocks-similar-to-matlabs-blkpro
	
	Args:
		matrix (ndarray): Matrix that needs to be reduced
		func (function, optional): Function to be applied to the blocks (chunks). The function must return an ndarray. Defaults to None.
		block_size (tuple, optional): Size of chunks (blocks). Defaults to (16,16).
		overlap (tuple, optional): Are the chunks overlapping. Defaults to (0,0).

	Returns:
		ndarray: The reduced matrix
	"""
	if len(matrix.shape) > 2:
		matrix = matrix.reshape(-1, matrix.shape[2]) #reshape to remove first dimension

	matrix = matrix[:matrix.shape[0]-matrix.shape[0]%block_size[0], 
		  			:matrix.shape[1]-matrix.shape[1]%block_size[1]]
	rows = []
	res_array = np.full(shape=matrix.shape, fill_value=nodata)
	frame_length = 1
	block_no = 0
	for i in range(0, matrix.shape[0], block_size[0]):
		cols = []
		for j in range(0, matrix.shape[1], block_size[1]):
			max_ndx = (min(i+block_size[0], matrix.shape[0]),
					   min(j+block_size[1], matrix.shape[1]))
			block_data = matrix[i:max_ndx[0], j:max_ndx[1]]
			res = func(block_data)

			res_array[i, j] = res[0][0]
			block_no += 1		
	return res_array
	 
def segment_and_concatenate_old(matrix, func=None, block_size=(16,16), overlap=(0,0)):
	"""Truncate matrix to a multiple of block_size. 
	Truncates the matrix to size that will be equally divisible by the block size
	
	See https://stackoverflow.com/questions/5073767/how-can-i-efficiently-process-a-numpy-array-in-blocks-similar-to-matlabs-blkpro
	
	Args:
		matrix (ndarray): Matrix that needs to be reduced
		func (function, optional): Function to be applied to the blocks (chunks). The function must return an ndarray. Defaults to None.
		block_size (tuple, optional): Size of chunks (blocks). Defaults to (16,16).
		overlap (tuple, optional): Are the chunks overlapping. Defaults to (0,0).

	Returns:
		ndarray: The reduced matrix
	"""
	if len(matrix.shape) > 2:
		matrix = matrix.reshape(-1, matrix.shape[2]) #reshape to remove first dimension

	matrix = matrix[:matrix.shape[0]-matrix.shape[0]%block_size[0], 
		  			:matrix.shape[1]-matrix.shape[1]%block_size[1]]
	rows = []
	for i in range(0, matrix.shape[0], block_size[0]):
		cols = []
		for j in range(0, matrix.shape[1], block_size[1]):
			max_ndx = (min(i+block_size[0], matrix.shape[0]),
					   min(j+block_size[1], matrix.shape[1]))
			res = func(matrix[i:max_ndx[0], j:max_ndx[1]])
			cols.append(res)
		rows.append(np.concatenate(cols, axis=1))
	return np.concatenate(rows, axis=0) # np.array([np.concatenate(rows, axis=0)]) # force return of a 3D matrix

from numpy.lib.stride_tricks import as_strided
def block_view(A, block= (3, 3)):
	"""Provide a 2D block view to 2D array. No error checking made.
	Therefore meaningful (as implemented) only for blocks strictly
	compatible with the shape of A."""
	# simple shape and strides computations may seem at first strange
	# unless one is able to recognize the 'tuple additions' involved ;-)
	shape= (A.shape[0]/ block[0], A.shape[1]/ block[1])+ block
	strides= (block[0]* A.strides[0], block[1]* A.strides[1])+ A.strides
	return as_strided(A, shape= shape, strides= strides)
	
def segmented_stride(M, fun, blk_size=(3,3), overlap=(0,0)):
	# This is some complex function of blk_size and M.shape
	stride = blk_size
	output = np.zeros(M.shape)

	B = block_view(M, block=blk_size)
	O = block_view(output, block=blk_size)

	for b,o in zip(B, O):
		o[:,:] = fun(b)

	return output

def view_process(M, fun=None, blk_size=(16,16), overlap=None):
	# truncate M to a multiple of blk_size
	from itertools import product
	output = np.zeros(M.shape)

	dz = np.asarray(blk_size)
	shape = M.shape - (np.mod(np.asarray(M.shape), 
						  blk_size))
	for indices in product(*[range(0, stop, step) 
						for stop,step in zip(shape, blk_size)]):
		# Don't overrun the end of the array.
		#max_ndx = np.min((np.asarray(indices) + dz, M.shape), axis=0)
		#slices = [slice(s, s + f, None) for s,f in zip(indices, dz)]
		output[indices[0]:indices[0]+dz[0], 
			   indices[1]:indices[1]+dz[1]][:,:] = fun(M[indices[0]:indices[0]+dz[0], 
			   indices[1]:indices[1]+dz[1]])

	return output
	
def clip_raster_to_vector_windowed(raster_file, vector, window_size, use_temp_dir=True, 
		apply_func=None, dest_nodata=None): 
	"""
	Mask out regions of a raster that are outside the polygons defined in the shapefile.

	Args:
		raster_file (string or array): Raster file or raster array
		vector (geojson): Polygon to be used for clipping
		window_size (tuple): How big are the blocks. A tuple of (width, height)
		use_temp_dir: If True, the resulting raster will be stored in /tmp directory, else in the media directory
		apply_func (function, optional): Function to applied to the windowed blocks. Defaults to None. 
										 This function must return an ndarray
		dest_nodata (number): Value to set as nodata when returning the clipped raster

	Returns:
		tuple(array, nodata, file): Raster, value of nodata, filepath of the generated raster
	"""
	def get_dest_file():
		# get output file
		if use_temp_dir:
			out_file = get_temp_file(suffix=".tif")
		else:
			out_file = get_absolute_media_path(file_path=None, 
										is_random_file=True, 
										random_file_prefix="",
										random_file_ext=".tif")
		return out_file
		
	# Clip the raster first
	array, file, nodata = clip_raster_to_vector(raster_file, vector, use_temp_dir=use_temp_dir, dest_nodata=dest_nodata)
	out_file = get_dest_file()# get output file
	out_raster = segment_and_concatenate(matrix=array, func=apply_func, block_size=window_size, nodata=nodata)
	res = save_raster(dataset=out_raster, source_path=file, target_path=out_file)
	return (out_raster, out_file, nodata)
	
def reshape_rasters(rasters):
	"""Returns an array whose size is smallest amongst the rasters
	Only reshapes rasters of shape (x, y) or (x, y, z)

	Args:
		rasters (list of nd-arrays): List of rasters to reshape
	"""
	is_masked = isinstance(rasters[0], ma.MaskedArray) if rasters else False
	# check if sizes are same
	if len(set([x.shape for x in rasters])) > 1:
		# check if shapes are similar in dimensions e.g (x, y, z) or (x,y)
		dimensions = set([len(x.shape) for x in rasters])
		if len(dimensions) > 1:
			raise AnalysisParamError("The specified inputs have different dimensions of %s", list(dimensions))
		
		if list(dimensions)[0] == 2: # If shape is (x, y)
			min_row_size = min([x.shape[0] for x in rasters])
			min_col_size = min([x.shape[1] for x in rasters])
			dest_rasters = []
			for rast in rasters:
				if not is_masked:
					dest_rasters.append(np.array(rast[:min_row_size, :min_col_size])) #extract min rows and cols
				else:
					dest_rasters.append(ma.array(rast[:min_row_size, :min_col_size])) #extract min rows and cols
		elif list(dimensions)[0] == 3: # If shape is (x, y, z)
			min_row_size = min([x.shape[1] for x in rasters])
			min_col_size = min([x.shape[2] for x in rasters])
			dest_rasters = []
			for rast in rasters:
				if not is_masked:
					dest_rasters.append(np.array(rast[:, :min_row_size, :min_col_size])) #extract min rows and cols
				else:
					dest_rasters.append(ma.array(rast[:, :min_row_size, :min_col_size])) #extract min rows and cols
		return dest_rasters
	return rasters

def reshape_raster(raster, shape):
	"""Returns an array whose size is of the shape speficied

	Args:
		raster (An nd-arrays): Raster to reshape
		shape (tuple(row, col)): Size of new raster
	"""
	# check if sizes are same
	if raster.shape != shape:
		dest_rast = raster[:shape[0] + 1, :shape[1] + 1]
		return dest_rast
	return raster

def reshape_and_reproject_rasters(raster_objects, vector):
	"""Reshape and reproject rasters
	Pass a list of objects of type {'raster': array, 'rasterfile': string}
	Args:		
		raster_objects (list): List of objects of type {'raster': array, 'rasterfile': string}
		vector: Vector to clip using
	"""

	"""
	1. Loop through all the rasters and reproject. Get the raster with the largest dimension and use that as the ref raster

	"""
	is_masked = isinstance(raster_objects[0]['raster'], ma.MaskedArray) if raster_objects else False
	# get raster with max size
	max_size = max([x['raster'].size for x in raster_objects])
	largest_raster = [x for x in raster_objects if x['raster'].size == max_size][0] #get the first
	results = []
	for obj in raster_objects:
		if obj['rasterfile'] != largest_raster['rasterfile']:
			raster, ref_nodata = reproject_raster(reference_raster=largest_raster['rasterfile'],
				raster=obj['rasterfile'],
				vector=vector
			)
			raster_vals = get_raster_values(raster, 
								band=GenericRasterBandEnum.HAS_SINGLE_BAND, 
								raster_source=RasterSourceEnum.MODIS, 
								windowed=False)	
			if is_masked:
				raster_vals = ma.array(raster_vals)
				raster_vals[raster_vals==ref_nodata] = ma.masked #mask nodata values
			results.append(raster_vals)
		else:
			results.append(largest_raster['raster'])
	return results

def get_raster_models(admin_zero_id=None, **args):
	"""Get Raster models from the database

	Returns:
		Enumerable: Return filtered Raster Models
	"""
	raster_models = Raster.objects.filter(**args)
	results = []
	if raster_models:
		# check if there are some associated with admin_0 id
		unique_years = list(set([x.raster_year for x in raster_models if x.raster_year]))
		for yr in list(set(unique_years)):
			year_models = [x for x in raster_models if x.raster_year==yr]
			if not admin_zero_id:
				"""
				If admin_zero_id (country) is not specified, return continental level
				"""
				# if regional_admin_id: # only proceed if regional_admin_id is specified
				# 	region = RegionalAdminLevel.objects.get(pk=regional_admin_id)
				# 	regional_rasters = [x for x in year_models if x.admin_level == AdminLevelEnum.REGIONAL.key and x.regional_admin == region]	
				# 	if regional_rasters: # add the first regional raster
				# 		results.append(regional_rasters[0])
				# 	else: # if there are no regional datasets, return continental						
				continental_rasters = [x for x in year_models if x.admin_level == AdminLevelEnum.CONTINENTAL.key]
				if continental_rasters: # add the first continental raster
					results.append(continental_rasters[0])
			else:
				"""
				If country specified, check if country has datasets, 
				If it has, return those. If no datasets tagged to the country, get the region_id of the country
				and check if there are datasets tagged with the region
				"""
				country_rasters = [x for x in year_models if x.admin_level == AdminLevelEnum.COUNTRY.key and x.admin_zero_id == admin_zero_id]
				if country_rasters:# add the first country level dataset
					results.append(country_rasters[0])
				else:
					region = AdminLevelZero.objects.get(pk=admin_zero_id).regional_admin
					if region:
						"""
						Check if there are datasets tagged by the regional_admin
						"""
						regional_rasters = [x for x in year_models if x.admin_level == AdminLevelEnum.REGIONAL.key and x.regional_admin == region]	
						if regional_rasters: # add the first regional raster
							results.append(regional_rasters[0])
						else:
							"""
							If there are no rasters tagged by region, return continental level datasets
							"""
							continental_rasters = [x for x in year_models if x.admin_level == AdminLevelEnum.CONTINENTAL.key]
							if continental_rasters: # add the first continental raster
								results.append(continental_rasters[0])
					else: # if no region specified, return continental level models
						continental_rasters = [x for x in year_models if x.admin_level == AdminLevelEnum.CONTINENTAL.key]
						if continental_rasters: # add the first continental raster
							results.append(continental_rasters[0])

			# country_rasters = [] if not admin_zero_id else [x for x in year_models if x.admin_zero_id == admin_zero_id]
			# if not admin_zero_id:
			# 	regional_rasters = [x for x in year_models if x.admin_level == -1 and x.regional_admin]	
			# regional_rasters = [x for x in year_models if x.admin_level == -1 and x.regional_admin]
			# continental_rasters = [x for x in year_models if x.admin_level == -2]

			# if admin_zero_id:
			# 	# check if there is a country level one
			# 	cntry_rasters = [x for x in year_models if x.admin_zero_id == admin_zero_id]
			# 	if cntry_rasters:
			# 		results.append(cntry_rasters[0])
			# 	elif regional_rasters: #else add the first regional level raster
			# 		results.append(regional_rasters[0])
			# else:
			# 	if regional_rasters:
			# 		results.append(regional_rasters[0])
	
		# convert list to queryset
		return list_to_queryset(Raster, results)
	return raster_models #if no admin_zero_id

def get_raster_models_old(admin_zero_id=None, regional_admin_id=None, **args):
	"""Get Raster models from the database

	Returns:
		Enumerable: Return filtered Raster Models
	"""
	raster_models = Raster.objects.filter(**args)
	results = []
	if raster_models:
		# check if there are some associated with admin_0 id
		unique_years = list(set([x.raster_year for x in raster_models if x.raster_year]))
		for yr in list(set(unique_years)):
			year_models = [x for x in raster_models if x.raster_year==yr]
			regional_rasters = [x for x in year_models if not x.admin_zero]
			if admin_zero_id:
				# check if there is a country level one
				cntry_rasters = [x for x in year_models if x.admin_zero_id == admin_zero_id]
				if cntry_rasters:
					results.append(cntry_rasters[0])
				elif regional_rasters: #else add the first regional level raster
					results.append(regional_rasters[0])
			else:
				if regional_rasters:
					results.append(regional_rasters[0])
	
		# convert list to queryset
		return list_to_queryset(Raster, results)
	return raster_models #if no admin_zero_id 

def compute_area(pixel_count, resolution):
	"""
	Get the area given pixel count and resolution

	Args:
		pixel_count (int): _description_
		resolution (int): _description_

	Returns:
		Area
	"""
	# The area is arrived at getting the area per pixel multiplied by number of pixels
	return (resolution or 1) * (resolution or 1) * pixel_count # multiply resolution squared by pixel count

def duplicate_raster_exists(raster):
	"""
	Check if a model exists so that we do not replace it
	"""
	exists = None
	if str(raster.admin_level) == str(AdminLevelEnum.CONTINENTAL.key):
		exists = Raster.objects.filter(
					raster_category=raster.raster_category,
					raster_year=raster.raster_year,
					raster_source=raster.raster_source,
					admin_level=raster.admin_level,
					continent_admin_id=raster.continent_admin_id			
			).first()
	if str(raster.admin_level) == str(AdminLevelEnum.REGIONAL.key):
		exists = Raster.objects.filter(
					raster_category=raster.raster_category,
					raster_year=raster.raster_year,
					raster_source=raster.raster_source,
					admin_level=raster.admin_level,
					regional_admin_id=raster.regional_admin_id		
			).first()
	if str(raster.admin_level) == str(AdminLevelEnum.COUNTRY.key):
		exists = Raster.objects.filter(
					raster_category=raster.raster_category,
					raster_year=raster.raster_year,
					raster_source=raster.raster_source,
					admin_level=raster.admin_level,
					admin_zero_id=raster.admin_zero_id		
			).first()
	return exists


def nanunique(arry):
	"""
	Get unique values ignoring nan

	"""
	a = np.unique(arry)
	r = []
	for i in a:
		if i in r or (np.isnan(i) and np.any(np.isnan(r))):
			continue
		else:
			r.append(i)
	return np.array(r)

def override_nodata(nodata):
	"""Harmonize nodata value
	If nodata value not between np.int8 range, return the default value
	"""
	#if not (settings.MIN_INT <= nodataval <= settings.MAX_INT):
	info = np.iinfo(np.int16)
	if info.min <= nodata <= info.max:
		return nodata
	return settings.DEFAULT_NODATA

def reclassify_by_quantiles(src_raster, classes_count, nodata):
	"""Reclassify raster into `quantiles_count` number of classes 

	Args:
		src_raster (array): Raster to reclassify
		classes_count (int): Number of classes to reclassify into
		nodata (number): Nodata value
	"""
	raster = np.array(src_raster)
	# Get the quantile break points
	percentiles = list()
	for i in range(1, classes_count):
		percentiles.append(i * (100.0/classes_count))

	# mask the nodata value
	# raster[raster==nodata] = ma.masked
			
	# Get the max and min values
	max_val = np.max(raster)
	min_val = np.min(raster)

	# Convert the raster into float
	raster = raster.astype('float')

	# Get a value that is not in the raster
	# placeholder_val = settings.MIN_INT # nodata # min_val - 1
	
	# Replace the placeholder value with NaNs
	#raster[raster==placeholder_val] = np.NaN
	raster[raster==nodata] = np.NaN

	# Compile the quantile breaks
	breakpoints = list(np.nanpercentile(raster, percentiles))	
	breakpoints.insert(0, min_val)
	breakpoints.append(max_val)

	# Map the ranges to class numbers
	replace_tbl = list()
	for i, breakpoint in enumerate(breakpoints[:-1]):
		replace_tbl.append([breakpoint, breakpoints[i+1], i+1])
	
	validdata_mask = raster!=nodata
	# Do actual replacement of cols and rows at once
	for i, k in enumerate(replace_tbl):
		lower = raster>k[0]
		# for the last index, increase max_val by 1 so as to ensure complete coverage
		upper = raster<=k[1] # raster<k[1] if i < len(replace_tbl) - 1 else raster<max_val + 1 
		raster[lower & upper & validdata_mask] = k[2]

	# restore the nodata values
	raster[np.isnan(raster)] = nodata
	return raster.astype(src_raster.dtype)
