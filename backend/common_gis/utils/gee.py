import ee
from ee.ee_exception import EEException
import os
import logging
from django.conf import settings
from django.utils.translation import gettext_lazy as _
# import geemap

log = logging.getLogger(f'common_gis.apps.{__name__}')

class GEEAccount:
	@property
	def service_account(self):
		return settings.GEE['SERVICE_ACCOUNT']		
	
	@property
	def private_key(self):
		return settings.GEE['PRIVATE_KEY_FILE']

class GEE(object):
	"""Wrapper class for GEE integration
	Implement a singleton GEE class. See https://medium.com/thedevproject/new-vs-init-in-python-a-most-known-resource-7beb538dc3b
	https://github.com/google/earthengine-api/blob/master/python/examples/ipynb/Earth_Engine_REST_API_computation.ipynb
	"""
	instance = None
	#initialized = False
	
	def __new__(cls, *args, **kwargs):
		if cls.instance is not None:
			return cls.instance
		else:
			inst = cls.instance = super(GEE, cls).__new__(cls, *args, **kwargs)
			cls.initialize(cls.instance)
			return inst
		
	def initialize(self):
		"""
		Initialize and authenticate GEE
		"""
		#if not self.initialized:
		self._authenticate()

	def _authenticate(self):
		"""
		Authenticate with service account if exists
		"""
		try:
			accnt = GEEAccount()
			credentials = ee.ServiceAccountCredentials(accnt.service_account, accnt.private_key)
			ee.Initialize(credentials)
			print(credentials)
		except EEException as e:
			print(str(e))
			log.log(logging.ERROR, str(e))

def is_image_valid(image):
	return len(image.getInfo()['bands']) > 0

def download_collection(images, scale, region, crs=None):
	"""
	Download image collection

	Args:
		images (ee.ImageCollection): Images to download
		scale (int): Scale of the image to be downloaded
		region (vector): Area of interest
		crs (string): Which projection to use

	Returns:
		string: URL of the downloaded image
	"""
	data = images.toList(images.size())
	urls = []
	for i in range(images.size().getInfo()): #This is the number of images in the images collection
		image = ee.Image(data.get(i))
		path = download_image(image, scale, region, crs)
		urls.append(path)		
	return urls

# def conver_to_array(img):
# 	"""
# 	@TODO: Convert the image to a raster array
# 	"""	
# 	if is_image_valid(img):
# 		gdf = geemap.ee_to_pandas(img)
# 		# url = img.getDownloadUrl({
# 		# 	'scale': SCALE,
# 		# 	# 'crs': 'EPSG:4326',
# 		# 	'region': get_country()
# 		# })
# 		# # print(url)
# 		# return url
# 		return gdf
# 	return None

def download_image(img, scale, region, crs=None):
	"""Download a GEE image

	Args:
		img (ee.Image): Image to download
		scale (int): Scale of the image to be downloaded
		region (vector): Area of interest
		crs (string): Which projection to use

	Returns:
		string: URL of the downloaded image
	
	NOTE: img.getDownloadUrl Get sa download URL for small chunks of image data in GeoTIFF or NumPy format. Maximum request size is 32 MB, maximum grid dimension is 10000
	@TODO: Convert the image to an array. check geemap lib
	Once the array is returned, generate a raster. 
	"""

	def _download_using_mapid():	
		if is_image_valid(img):
			from django.conf import settings
			url = img.getDownloadUrl({
				'scale': scale, 
				'crs': crs or settings.DEFAULT_CRS or 'EPSG:4326',
				'region': region
			})
			# conver_to_array(img)
			# print(url)
			return url
		return None
	
	def _download_via_array():
		if is_image_valid(img):
			from django.conf import settings
			url = img.getDownloadUrl({
				'scale': scale,
				# 'crs': 'EPSG:4326',
				'crs': crs or settings.DEFAULT_CRS or 'EPSG:4326',
				'region': region,
				'format': 'NPY'
			})
			# conver_to_array(img)
			# print(url)
			return url
		return None

	return _download_using_mapid()
	# arr = _download_via_array()
	# # res = img_to_array(img=img, aoi=region)
	# # tif = img_to_geotiff(img=img, aoi=region, scale=scale, crs="EPSG:4326")
	# tif = img_to_pandas(img)
	# return tif # arr

def img_to_array(img, aoi):
	"""Convert GEE image to numpy array

	See https://github.com/gee-community/geemap/blob/master/examples/notebooks/11_export_image.ipynb
	    https://mygeoblog.com/2017/10/06/from-gee-to-numpy-to-geotiff/

	Args:
		img: GEE image
		aoi: Area of interest
	"""
	if not isinstance(img, ee.Image):
		raise ValueError(_("Expected an ee.Image object"))
	return geemap.ee_to_numpy(img, aoi)

def img_to_geotiff(img, aoi, scale, crs):
	"""Convert GEE image to Tiff

	See https://github.com/gee-community/geemap/blob/master/examples/notebooks/134_ee_to_geotiff.ipynb
	    https://mygeoblog.com/2017/10/06/from-gee-to-numpy-to-geotiff/

	Args:
		img: GEE image
		aoi: Area of interest
	"""
	if not isinstance(img, ee.Image):
		raise ValueError(_("Expected an ee.Image object"))
	return geemap.ee_to_geotiff(img, output='test.tif', #bbox=aoi, 
			     resolution=scale, crs=crs)

def img_to_pandas(img):
	"""Convert GEE image to Tiff

	See https://github.com/gee-community/geemap/blob/master/examples/notebooks/134_ee_to_geotiff.ipynb
	    https://mygeoblog.com/2017/10/06/from-gee-to-numpy-to-geotiff/

	Args:
		img: GEE image
		aoi: Area of interest
	"""
	if not isinstance(img, ee.Image):
		raise ValueError(_("Expected an ee.Image object"))
	return geemap.ee_to_pandas(img)