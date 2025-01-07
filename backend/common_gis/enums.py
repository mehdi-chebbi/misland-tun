import enum
from django.utils.translation import gettext as _

class KeyValueBaseEnum(enum.Enum):
	"""Enumeration for items with key and label properties
	"""
	@property
	def key(self):
		return self.value[0]

	@property
	def label(self):
		return self.value[1]
		
class RasterSourceEnum(enum.Enum):
	"""
	Enumeration for different raster sources
	"""
	LULC = "LULC"
	MODIS = "Modis"
	LANDSAT7 = "Landsat 7"
	LANDSAT8 = "Landsat 8"
	HANSEN = "Hansen"
	SENTINEL2 = "Sentinel 2"
	# SINGLE_BAND_IMAGE = 1
	# MODIS = 2
	# LANDSAT7 = 3
	# LANDSAT8 = 4

class GenericRasterBandEnum(enum.Enum):
	"""
	Enumeration for raster bands independently of image source.
	Will be used to retrieve the correct band dynamically
	depending on the image source
	"""
	HAS_SINGLE_BAND = 0 # handles reading of images with only a single band
	RED = 1
	GREEN = 2
	BLUE = 3
	NIR = 4
	SWIR1 = 5
	SWIR2 = 6

class MODISBandEnum(enum.Enum):
	"""
	Enumeration for MODIS bands
	"""
	RED = 1
	NIR = 2
	BLUE = 3
	GREEN = 4
	SWIR1 = 5
	SWIR2 = 6

class Landsat7BandEnum(enum.Enum):
	"""
	Enumeration for Landsat 7 bands
	"""
	BLUE = 1
	GREEN = 2
	RED = 3
	NIR = 4
	SWIR1 = 5
	TIR = 6
	SWIR2 = 7
	PANCHROMATIC = 8

class Landsat8BandEnum(enum.Enum):
	"""
	Enumeration for Landsat 8 bands
	"""
	COASTAL = 1
	BLUE = 2
	GREEN = 3
	RED = 4
	NIR = 5
	SWIR1 = 6
	SWIR2 = 7
	PANCHROMATIC = 8
	CIRRUS = 9
	TIR1 = 10
	TIR2 = 11

class RasterOperationEnum(enum.Enum):
	"""Enumeration for different raster operations
	"""
	ADD = 1
	SUBTRACT = 2
	DIVIDE = 3
	MULTIPLY = 4
	
class AdminLevelEnum(KeyValueBaseEnum):
	"""
	Enumeration for top 3 admin levels
	"""
	CONTINENTAL = ('-2', _("Continental"))
	REGIONAL = ('-1', _("Regional"))
	COUNTRY = ('0', _("Country"))