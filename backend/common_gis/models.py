# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.db.models.manager import Manager as GeoManager
from django.conf import settings
from django.utils.translation import gettext as _
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import os
from common.models import SearchableQuerySet, SearchableModelManager, BaseModel
from common_gis.enums import AdminLevelEnum

class AdminLevelModelManager(GeoManager):
	"""
	Extend GeoManager to maintain the ability for spatial querying as we allow for more definition of methods
	"""
	def get_queryset(self):
		return SearchableQuerySet(self.model, using=self._db)
	
	def search(self, query=None):
		return self.get_queryset().search(query=query)

class ContinentalAdminLevel(BaseModel):
	"""
	Model for continental shapefile
	"""
	class Meta:
		ordering = ('name',)

	object_id = models.IntegerField(default=0)
	name = models.CharField(max_length=100, null=True, blank=True)
	shape_length = models.FloatField(blank=True, null=True, default=0)
	shape_area = models.FloatField(blank=True, null=True, default=0)
	geom = models.MultiPolygonField()
	objects = AdminLevelModelManager() #to allow for spatial queries and operations
	
	# objects = GeoManager() #to allow for spatial queries and operations

	@property
	def search_columns(self):
		return ["name"]

	@property
	def search_display_text(self):
		return f'{self.name}'
		
	def __str__(self):
		return self.name or self.object_id

	def is_duplicate(self):
		"""
		Check if a model exists so that we do not replace it
		"""	
		exists = ContinentalAdminLevel.objects.filter(name=self.name).first()
		return exists

	def save(self, *args, **kwargs):
		"""Ensure we do not replace existing record
		"""
		if self.pk: # is an update, go ahead and update
			super(ContinentalAdminLevel, self).save(*args, **kwargs)
		else:# If it is a new record
			if not self.is_duplicate(): # Only save when it is not a duplicate
				super(ContinentalAdminLevel, self).save(*args, **kwargs)
			else:
				print("ContinentalAdminLevel {0} exists".format(self.name))
				return# cancel the save
	


class ShapeFile(BaseModel):
	"""
	Model to handle shapefiles
	"""
	filename = models.CharField(max_length=255)
	srs = models.CharField(max_length=254, blank=True)
	geom_type = models.CharField(max_length=50)
	encoding = models.CharField(max_length=20, blank=True)

	def __str__(self):
		return self.filename

class Attribute(BaseModel):
	"""
	Model to handle shapefile attributes
	"""
	shapefile = models.ForeignKey(ShapeFile, on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	type = models.IntegerField()
	width = models.IntegerField()
	precision = models.IntegerField()

	def __str__(self):
		return 'Name: %s' % self.name

class Feature(BaseModel):
	"""
	Model to handle features of a shapefile
	"""
	feature_name = models.CharField(max_length=255, default="")
	shapefile = models.ForeignKey(ShapeFile, on_delete=models.CASCADE)
	# geom_point = models.PointField(srid=4326, blank=True, null=True)
	# geom_multipoint = models.MultiPointField(srid=4326, blank=True, null=True)	
	# geom_linestring = models.LineStringField(srid=4326, blank=True, null=True)
	# geom_multilinestring = models.MultiLineStringField(srid=4326, blank=True, null=True)
	# geom_polygon = models.PolygonField(srid=4326, blank=True, null=True)
	# geom_multipolygon = models.MultiPolygonField(srid=4326, blank=True, null=True)
	geom_geometrycollection = models.GeometryCollectionField(srid=4326, blank=True, null=True)
	objects = GeoManager() #to allow for spatial queries and operations

class AttributeValue(BaseModel):
	"""
	Model to handle attribute features of a shapefile
	"""
	feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
	attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
	value = models.CharField(max_length=255, blank=True, null=True)
	
class RegionalAdminLevel(BaseModel):
	"""
	Model for regional shapefile
	"""
	class Meta:
		ordering = ('name',)

	continent_admin = models.ForeignKey(ContinentalAdminLevel, on_delete=models.CASCADE, blank=True, null=True, default=None)
	object_id = models.IntegerField(default=0)
	name = models.CharField(max_length=100, null=True, blank=True)
	shape_length = models.FloatField(blank=True, null=True, default=0)
	shape_area = models.FloatField(blank=True, null=True, default=0)
	geom = models.MultiPolygonField()
	objects = AdminLevelModelManager() #to allow for spatial queries and operations

	# objects = GeoManager() #to allow for spatial queries and operations

	@property
	def search_columns(self):
		return ["name"]

	@property
	def search_display_text(self):
		return f'{self.name}'

	def __str__(self):
		return self.name or self.object_id

	def is_duplicate(self):
		"""
		Check if a model exists so that we do not replace it
		"""	
		exists = RegionalAdminLevel.objects.filter(name=self.name).first()
		return exists

	def save(self, *args, **kwargs):
		"""Ensure we do not replace existing record
		"""
		if self.pk: # is an update, go ahead and update
			super(RegionalAdminLevel, self).save(*args, **kwargs)
		else:# If it is a new record
			if not self.is_duplicate(): # Only save when it is not a duplicate
				super(RegionalAdminLevel, self).save(*args, **kwargs)
			else:
				print("RegionalAdminLevel {0} exists".format(self.name))
				return# cancel the save

class AdminLevelZero(BaseModel):
	"""
	Model to handle Admin Level Zero boundaries
	"""
	class Meta:
		ordering = ('name_0',)

	regional_admin = models.ForeignKey(RegionalAdminLevel, on_delete=models.CASCADE, blank=True, null=True, default=None)
	gid_0 = models.CharField(max_length=50)
	name_0 = models.CharField(max_length=250)
	region_name = models.CharField(max_length=250, blank=True, null=True, default=None)
	cpu = models.CharField(max_length=250, blank=True, null=True)
	geom = models.MultiPolygonField()

	objects = AdminLevelModelManager() #to allow for spatial queries and operations

	def __str__(self):
		return self.name_0

	def is_duplicate(self):
		"""
		Check if a model exists so that we do not replace it
		"""	
		exists = AdminLevelZero.objects.filter(name_0=self.name_0).first()
		return exists

	def save(self, *args, **kwargs):
		"""Ensure we do not replace existing record
		"""
		if self.pk: # is an update, go ahead and update
			super(AdminLevelZero, self).save(*args, **kwargs)
		else:# If it is a new record
			if not self.is_duplicate(): # Only save when it is not a duplicate
				super(AdminLevelZero, self).save(*args, **kwargs)
			else:
				print("AdminLevelZero {0} exists".format(self.name_0))
				return# cancel the save

	@property
	def search_columns(self):
		return ["name_0"]

	@property
	def search_display_text(self):
		return self.name_0


class AdminLevelOne(BaseModel):
	"""
	Model to handle Admin Level One boundaries
	"""
	class Meta:
		ordering = ('name_0', 'name_1',)

	admin_zero = models.ForeignKey(AdminLevelZero, on_delete=models.CASCADE)
	gid_0 = models.CharField(max_length=50)
	name_0 = models.CharField(max_length=250)	
	gid_1 = models.CharField(max_length=50)	
	name_1 = models.CharField(max_length=250)	
	varname_1 = models.CharField(max_length=250, blank=True, null=True)	
	nl_name_1 = models.CharField(max_length=250, blank=True, null=True)	
	type_1 = models.CharField(max_length=250, blank=True, null=True)	
	engtype_1 = models.CharField(max_length=250, blank=True, null=True)	
	cc_1 = models.CharField(max_length=50, default='', blank=True, null=True)	
	hasc_1 = models.CharField(max_length=250, blank=True, null=True)	 
	cpu = models.CharField(max_length=250, blank=True, null=True)
	geom = models.MultiPolygonField()

	objects = AdminLevelModelManager() #to allow for spatial queries and operations

	def __str__(self):
		return self.name_1

	def admin_zero_exists(self):
		"""
		Check if admin_zero exists
		"""
		exists = AdminLevelZero.objects.filter(gid_0=self.gid_0).first()
		return exists

	def is_duplicate(self):
		"""
		Check if a model exists so that we do not replace it
		We check for existence of the admin_level_zero too
		"""	
		exists = AdminLevelOne.objects.filter(name_1=self.name_1, gid_0=self.gid_0).first()
		return exists

	def save(self, *args, **kwargs):
		"""Ensure we do not replace existing record
		"""
		if not self.admin_zero_exists():
			print("AdminLevelOne {0}. AdminLevelZero {1} does not exist".format(self.name_1, self.name_0))
			return
		else:
			if self.pk: # is an update, go ahead and update
				super(AdminLevelOne, self).save(*args, **kwargs)
			else:# If it is a new record
				if not self.is_duplicate(): # Only save when it is not a duplicate
					super(AdminLevelOne, self).save(*args, **kwargs)
				else:
					print("AdminLevelOne {0} exists".format(self.name_1))
					return# cancel the save

	@property
	def search_columns(self):
		return ["name_1"]

	@property
	def search_display_text(self):
		return f'{self.admin_zero.name_0}, {self.name_1} '

class AdminLevelTwo(BaseModel):
	"""
	Model to handle Admin Level Two boundaries
	"""
	class Meta:
		ordering = ('name_0', 'name_1', 'name_2',)

	admin_one = models.ForeignKey(AdminLevelOne, on_delete=models.CASCADE)
	gid_0 = models.CharField(max_length=50)
	name_0 = models.CharField(max_length=250)
	gid_1 = models.CharField(max_length=250)
	name_1 = models.CharField(max_length=250)
	nl_name_1 = models.CharField(max_length=250, blank=True, null=True)
	gid_2 = models.CharField(max_length=250)
	name_2 = models.CharField(max_length=250)
	varname_2 = models.CharField(max_length=250, blank=True, null=True)
	nl_name_2 = models.CharField(max_length=250, blank=True, null=True)
	type_2 = models.CharField(max_length=250, blank=True, null=True)
	engtype_2 = models.CharField(max_length=250, blank=True, null=True)
	cc_2 = models.CharField(max_length=250, default='', blank=True, null=True)
	hasc_2 = models.CharField(max_length=250, blank=True, null=True)
	cpu = models.CharField(max_length=250, blank=True, null=True)
	geom = models.MultiPolygonField()

	objects = AdminLevelModelManager() #to allow for spatial queries and operations

	def is_duplicate(self):
		"""
		Check if a model exists so that we do not replace it
		We check for existence of the admin_level_zero too
		"""	
		exists = AdminLevelTwo.objects.filter(name_2=self.name_2, gid_1=self.gid_1).first()
		return exists

	def save(self, *args, **kwargs):
		"""Ensure we do not replace existing record
		"""
		if self.pk: # is an update, go ahead and update
			super(AdminLevelTwo, self).save(*args, **kwargs)
		else:# If it is a new record
			if not self.is_duplicate(): # Only save when it is not a duplicate
				super(AdminLevelTwo, self).save(*args, **kwargs)
			else:
				print("AdminLevelTwo {0} exists".format(self.name_2))
				return# cancel the save

	@property
	def search_columns(self):
		return ["name_2"]

	@property
	def search_display_text(self):
		return f'{self.admin_one.admin_zero.name_0}, {self.admin_one.name_1}, {self.name_2}' # f"{{}}"


class RasterType(BaseModel):
	"""
	Model for Raster Types
	"""
	name = models.CharField(max_length=250, blank=False)
	description = models.TextField(blank=True, null=True)

	class Meta:
		ordering = ['name']
		
	def __str__(self):
		return "%s: %s" % (self.name, self.description)

class RasterValueMapping(BaseModel):
	"""
	Model for Mapping Raster pixel values with a label
	"""
	raster_type = models.ForeignKey(RasterType, on_delete=models.CASCADE)
	value = models.FloatField(blank=True, null=True)
	label = models.CharField(max_length=250, blank=True, null=True)
	color = models.CharField(max_length=50, default="#FF0000", blank=True, null=True)

	def __str__(self):
		return "%s mapping" % (self.raster_type.name)
		
def current_year():
	return datetime.date.today().year
	
def max_year_validator(value):
	return MaxValueValidator(current_year())(value)

class Raster(BaseModel):
	"""
	Model to store Raster MetaData
	"""
	raster_types = (
		# ("LULC", 'Land Use/Land Cover'),
		# ("Productivity", 'Productivity'),
		# ("Carbon Stocks", 'Carbon Stocks'),
		# ("Land Degradation", 'Land Degradation'),
		# ('Ecological Units', 'Ecological Units'),
		# ("Forest Loss", 'Forest Loss'),
	)	
	# RASTER_CATEGORIES = []	
	# for itm in RasterCategoryEnum:
	# 	RASTER_CATEGORIES.append((itm.value, itm.value))
	
	# RASTER_SOURCES = []
	# for itm in RasterSourceEnum:
	# 	RASTER_SOURCES.append((itm.value, itm.value))

	ADMIN_LEVELS = [("", "")]	
	for itm in AdminLevelEnum:
		ADMIN_LEVELS.append((itm.key, itm.label))

	name = models.CharField(max_length=100, blank=False, null=True, 
			help_text=_("Raster layer name"))
	description = models.TextField(blank=True, null=True, 
			help_text=_("Description"))
	raster_year = models.PositiveIntegerField(
			blank=False,
			default=current_year(),
			validators=[MinValueValidator, max_year_validator],
			help_text=_("Year")
	)
	# raster_type = models.CharField(max_length=100, choices=raster_types, blank=True)
	raster_type = models.ForeignKey(RasterType, blank=True, null=True, on_delete=models.PROTECT)
	raster_category = models.CharField(max_length=100, choices=settings.RASTER_CATEGORIES, 
			 blank=False, default="", 
			 help_text=_("Raster Category"))
	# datatype = models.CharField(max_length=2, choices=DATATYPES, default='co')
	rasterfile = models.FileField(null=True, blank=False, 
			 help_text=_("Raster source file"))
	raster_source = models.CharField(max_length=50, choices=settings.RASTER_SOURCES, 
			 blank=False, default="", 
			 help_text=_("Datasource"))
	values_type=models.CharField(null=True, blank=False, max_length=50, default="Discrete", 
				choices=[("Discrete", 'Discrete'), ("Continuous", 'Continuous')], 
				help_text=_("Does the raster contain continuous or discrete values?"))
	admin_level = models.CharField(max_length=50, choices=ADMIN_LEVELS, blank=False, default=None, null=True)
	continent_admin = models.ForeignKey(ContinentalAdminLevel, on_delete=models.CASCADE, default="", blank=True, null=True)
	regional_admin = models.ForeignKey(RegionalAdminLevel, on_delete=models.CASCADE, default="", blank=True, null=True)
	admin_zero = models.ForeignKey(AdminLevelZero, on_delete=models.CASCADE, 
			 default="", blank=True, null=True,
			 help_text=_("Country"))
	resolution = models.FloatField(null=True, blank=True, 
			help_text=_("Resolution"))
	# rasterlayer = models.OneToOneField(RasterLayer, related_name='metadata', on_delete=models.CASCADE)
	uperleftx = models.FloatField(null=True, blank=True, 
			help_text=_("Upper Left X"))
	uperlefty = models.FloatField(null=True, blank=True, 
			help_text=_("Upper left Y"))
	width = models.IntegerField(null=True, blank=True, 
			help_text=_("Width"))
	height = models.IntegerField(null=True, blank=True, 
			help_text=_("Height"))
	scalex = models.FloatField(null=True, blank=True, 
			help_text=_("Scale X"))
	scaley = models.FloatField(null=True, blank=True, 
			help_text=_("Scale Y"))
	skewx = models.FloatField(null=True, blank=True, 
			help_text=_("Skew X"))
	skewy = models.FloatField(null=True, blank=True, 
			help_text=_("Skew Y"))
	numbands = models.IntegerField(null=True, blank=True, 
			help_text=_("Number of bands"))
	srs_wkt = models.TextField(null=True, blank=True, 
			help_text=_("SRS WKT"))
	srid = models.PositiveSmallIntegerField(null=True, blank=True, 
			help_text=_("SRS ID"))
	max_zoom = models.PositiveSmallIntegerField(null=True, blank=True, 
			help_text=_("Maximum Zoom"))
	
	class Meta:
		ordering = ['-raster_year', 'name','raster_category', 'raster_source']

	def __str__(self):
		return self.name

	def sanitize_admin_levels(self):
		"""
		Set / unset different values for admin level
		"""
		if self.admin_level == AdminLevelEnum.CONTINENTAL.key:
			self.regional_admin = None
			self.admin_zero = None
		if self.admin_level == AdminLevelEnum.REGIONAL.key:
			self.continent_admin = None
			self.admin_zero = None
		if self.admin_level == AdminLevelEnum.COUNTRY.key:
			self.continent_admin = None
			self.regional_admin = None

	def is_duplicate(self):
		"""
		Check if a model exists so that we do not replace it
		"""
		from common_gis.utils.raster_util import duplicate_raster_exists
		exists = duplicate_raster_exists(self)	
		return exists

	def save(self, *args, **kwargs):
		"""Ensure we do not replace existing record
		"""
		self.sanitize_admin_levels()
		if self.pk: # is an update, go ahead and update
			super(Raster, self).save(*args, **kwargs)
		else:# If it is a new record
			exists = self.is_duplicate()
			if not exists: # Only save when it is not a duplicate
				super(Raster, self).save(*args, **kwargs)
			else:
				msg = "A duplicate Raster already exists. ID {0}".format(exists.id)
				print(msg)
				raise Exception(msg) #cancel the save

# class RasterType(BaseModel):
# 	"""
# 	Model for Raster Types
# 	"""
# 	# RASTER_CATEGORIES = []
# 	# for itm in RasterCategoryEnum:
# 	# 	RASTER_CATEGORIES.append((itm.value, itm.value))

# 	name = models.CharField(max_length=250, blank=False,
# 		help_text=_("Raster type name"))
# 	raster_category = models.CharField(max_length=100, choices=settings.RASTER_CATEGORIES, 
# 			 blank=False, default="", 
# 			 help_text=_("Raster Category"))
# 	description = models.TextField(blank=True, null=True,
# 		help_text=_("Description"))
	
#     # class Meta:
#     #     db_table = 'gis_rastertype'

# 	def __str__(self):
# 		return "%s: %s" % (self.name, self.description)

class GISSettings(BaseModel):
	"""Singleton Django Model
	Ensures there's always only one entry in the database, and can fix the
	table (by deleting extra entries) even if added via another mechanism.
	
	Also has a static load() method which always returns the object - from
	the database if possible, or a new empty (default) instance if the
	database is still empty. If your instance has sane defaults (recommended),
	you can use it immediately without worrying if it was saved to the
	database or not.
	
	Useful for things like system-wide user-editable settings.
	"""
	enable_guest_user_limit = models.BooleanField(default=False, 
			help_text=_("If checked, guest users will process polygons upto a specific polygon size"))
	guest_user_polygon_size_limit = models.FloatField(blank=False, 
			help_text=_("Maximum size of polygon in hectares that anonymous users can process using the system"))
	enable_signedup_user_limit = models.BooleanField(default=False, 
			help_text=_("If checked, Logged in users will process polygons upto a specific polygon size"))
	signedup_user_polygon_size_limit = models.FloatField(blank=False, default=1, 
			help_text=_("Maximum size of polygon in hectares that Logged in users can process using the system"))
	enable_task_scheduling = models.BooleanField(
			help_text=_("If checked, user GIS tasks will be scheduled"))
	task_results_url = models.CharField(max_length=255, blank=False, 
			default="http://0.0.0.0:8080/#/dashboard/results/", null=False, 
			help_text=_("Url to redirect user when results of scheduled task are available. Task id will be appended at the end after /"))
	raster_clipping_algorithm = models.CharField(max_length=20, 
			choices=[("All Touched", "All Touched"), ("Pixel Center", "Pixel Center")], 
			blank=True, default="All Touched:", 
			help_text=_("""All Touched=Include a pixel in the mask if it touches any of the shapes.
				Pixel Center= Include a pixel only if its center is within one of the shapes"""))
	enable_cache = models.BooleanField(default=True, blank=True, 
			help_text=_("If enabled, results of GIS computation will be cached for a period as specified by the cache limit field"))
	cache_limit = models.IntegerField(default=86400, 
			help_text=_("Number of seconds that results will be cached."))
	# override_backend_port = models.BooleanField(default=True, 
	# 		help_text=_("If checked, the system will override the default port and use the value of Backend port. Important when constructing URL of computed Raster"))
	# backend_url = models.CharField(_("Backend url"), max_length=200, 
	# 		default="http://0.0.0.0/", 
	# 		blank=False, 
	# 		null=False,
	# 		help_text=_("URL of server (without port) hosting the backend."))
	# backend_port = models.IntegerField(_("Backend port"), default=80, 
	# 		help_text=_("Port from which the system is served"))
	enable_tiles = models.BooleanField(default=False, blank=True, help_text=_("If enabled, a WMS link will be returned for all analysis to allow rendering of tiles"))
	 
	
	class Meta:
		abstract = False # True
		verbose_name_plural = "GIS Settings"

	def __str__(self):
		return "GIS Settings"

	def save(self, *args, **kwargs):
		"""
		Save object to the database. Removes all other entries if there
		are any.
		"""
		self.__class__.objects.exclude(id=self.id).delete()
		super(GISSettings, self).save(*args, **kwargs)

	@classmethod
	def load(cls):
		"""
		Load object from the database. Failing that, create a new empty
		(default) instance of the object and return it (without saving it
		to the database).
		"""
		try:
			return cls.objects.get()
		except cls.DoesNotExist:
			return cls()

class ComputationThreshold(BaseModel):
	"""
	Class to store Thresholds for analysis
	"""
	# RASTER_SOURCES = []
	# for itm in RasterSourceEnum:
	# 	RASTER_SOURCES.append((itm.value, itm.value))

	datasource = models.CharField(max_length=255, blank=False, null=False, 
				choices=settings.RASTER_SOURCES, unique=True, 
				help_text=_("Datasource"))
	enable_guest_user_limit = models.BooleanField(default=True, 
				help_text=_("If checked, guest users will process polygons upto a specific polygon size"))
	guest_user_threshold = models.FloatField(blank=False, 
				help_text=_("Maximum size of polygon in hectares that anonymous users can process using the system for the selected datasource"))
	enable_signedup_user_limit = models.BooleanField(default=True, 
				help_text=_("If checked, Logged in users will process polygons upto a specific polygon size"))
	authenticated_user_threshold = models.FloatField(blank=False, 
				help_text=_("Maximum size of polygon in hectares that anonymous users can process using the system for the selected datasource"))
	
class CustomShapeFile(BaseModel):
	"""
	Model for custom shape files
	"""
	owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
	shapefile_name = models.CharField(_("Description of the vector"), max_length=100, null=True, blank=True)
	# description = models.TextField(_("Description of the vector"), blank=False)
	shapefile = models.FileField(_("Upload Shapefile"))
	shape_length = models.FloatField(blank=True, null=True, default=0)
	shape_area = models.FloatField(blank=True, null=True, default=0)	
	# geom = models.MultiPolygonField()
	geom = models.GeometryCollectionField(srid=4326, blank=True, null=True)
	objects = GeoManager() #to allow for spatial queries and operations

class PublishedComputation(BaseModel):
	class Meta:
		abstract = False # True
		verbose_name_plural = "Published Computations"

	def __str__(self):
		return self.computation_type

	# COMPUTATIONS = []	
	# for itm in ComputationEnum:
	# 	COMPUTATIONS.append((itm.value, itm.value))
	 	
	computation_type = models.CharField(max_length=100, choices=settings.COMPUTATIONS, blank=False, default="")
	style = models.TextField(help_text=_("Styled Layer Descriptor (SLD)"), null=True, blank=True)
	admin_zero = models.ForeignKey(AdminLevelZero, on_delete=models.CASCADE, 
					default="", blank=True, null=True, help_text=_("Associated country. Leave blank to associate with all countries"))
	published = models.BooleanField(default=True, null=True, help_text=_("If checked, only the specified years will be enabled for computation"))
	
class PublishedComputationYear(BaseModel):	
	published_computation = models.ForeignKey(PublishedComputation, verbose_name=_("published_computation"), related_name="published_computations", on_delete=models.CASCADE)
	published_year = models.PositiveIntegerField(
			blank=False,
			default=current_year(),
			validators=[MinValueValidator, max_year_validator]
	)
class DataImportSettings(BaseModel):
	"""Singleton Django Model
	Ensures there's always only one entry in the database, and can fix the
	table (by deleting extra entries) even if added via another mechanism.
	
	Also has a static load() method which always returns the object - from
	the database if possible, or a new empty (default) instance if the
	database is still empty. If your instance has sane defaults (recommended),
	you can use it immediately without worrying if it was saved to the
	database or not.
	
	Useful for things like system-wide user-editable settings.
	"""	
	raster_data_file = models.FileField(help_text=_("JSON file that contains definition of rasters to be imported into the system from disk"))

	class Meta:
		abstract = False # True
		verbose_name_plural = "Data Import Settings"

	def __str__(self):
		return "Data Import Settings"

	def save(self, *args, **kwargs):
		"""
		Save object to the database. Removes all other entries if there
		are any.
		"""
		self.__class__.objects.exclude(id=self.id).delete()
		super(DataImportSettings, self).save(*args, **kwargs)

	@classmethod
	def load(cls):
		"""
		Load object from the database. Failing that, create a new empty
		(default) instance of the object and return it (without saving it
		to the database).
		"""
		try:
			return cls.objects.get()
		except cls.DoesNotExist:
			return cls()

class ScheduledPreComputation(BaseModel):
	"""Model to handle precomputations. Stores computations that need to be precomputed
	"""
	class Meta:
		abstract = False # True
		verbose_name_plural = "Scheduled PreComputations"

	def __str__(self):
		return self.computation_type

	# COMPUTATIONS = []	
	# for itm in ComputationEnum:
	# 	COMPUTATIONS.append((itm.value, itm.value))
	ADMIN_LEVELS = [("", "")]	
	for itm in AdminLevelEnum:
		ADMIN_LEVELS.append((itm.key, itm.label))

	STATUS = [("", "")]	
	for itm in ["Queued", "Processing", "Failed", "Succeeded"]:
		STATUS.append((itm, itm))
	computation_type = models.CharField(max_length=100, choices=settings.COMPUTATIONS, blank=False, default="")
	change_enum = models.CharField(max_length=255, blank=True, null=True, help_text=_("Change Enum applied"))
	admin_level = models.CharField(max_length=50, choices=ADMIN_LEVELS, blank=False, default=None, null=True)
	continent = models.ForeignKey(ContinentalAdminLevel, on_delete=models.CASCADE, default="", blank=True, null=True)
	region = models.ForeignKey(RegionalAdminLevel, on_delete=models.CASCADE, 
						default="", blank=True, null=True,
						help_text=_("Region"))
	admin_zero = models.ForeignKey(AdminLevelZero, on_delete=models.CASCADE, 
			 default="", blank=True, null=True,
			 help_text=_("Country"))
	datasource = models.CharField(max_length=255, blank=False, null=True, 
				choices=settings.RASTER_SOURCES, default='', 
				help_text=_("Datasource"))
	start_year = models.PositiveIntegerField(
			blank=False,
			#default=current_year(),
			validators=[MinValueValidator, max_year_validator]
	)
	end_year = models.PositiveIntegerField(
			blank=False,
			#default=current_year(),
			validators=[MinValueValidator, max_year_validator]
	)
	started_on = models.DateTimeField(blank=True, null=True)
	status = models.CharField(max_length=100, choices=STATUS, blank=False, default="")
	args = models.TextField(blank=True, null=True)
	method = models.CharField(max_length=128)
	error = models.TextField(blank=True, null=True)
	succeeded = models.BooleanField(default=False)
	completed_on = models.DateTimeField(blank=True, null=True)
	#published = models.BooleanField(default=True, null=True, help_text=_("If checked, only the specified years will be enabled for computation"))	

	def sanitize_admin_levels(self):
		"""
		Set / unset different values for admin level
		"""
		if self.admin_level == AdminLevelEnum.CONTINENTAL.key:
			self.region = None
			self.admin_zero = None
		if self.admin_level == AdminLevelEnum.REGIONAL.key:
			self.continent = None
			self.admin_zero = None
		if self.admin_level == AdminLevelEnum.COUNTRY.key:
			self.continent = None
			self.regionn = None

	def is_duplicate(self):
		"""
		Check if a model exists so that we do not replace it
		"""
		from common_gis.utils.raster_util import duplicate_raster_exists
		exists = duplicate_raster_exists(self)	
		return exists

	def save(self, *args, **kwargs):
		"""Ensure we do not replace existing record
		"""
		self.sanitize_admin_levels()
		#super(ScheduledPreComputation, self).save(*args, **kwargs)
		if self.pk: # is an update, go ahead and update 
			super(ScheduledPreComputation, self).save(*args, **kwargs)
		else:# If it is a new record
			self.status = "Queued"
			super(ScheduledPreComputation, self).save(*args, **kwargs)

		# if self.pk: # is an update, go ahead and update
		# 	super(ScheduledPreComputation, self).save(*args, **kwargs)
		# else:# If it is a new record
		# 	exists = self.is_duplicate()
		# 	if not exists: # Only save when it is not a duplicate
		# 		super(ScheduledPreComputation, self).save(*args, **kwargs)
		# 	else:
		# 		msg = "A duplicate Raster already exists. ID {0}".format(exists.id)
		# 		print(msg)
		# 		raise Exception(msg) #cancel the save

class ScheduledTask(BaseModel):
	"""Model to store info about an asynchronous task"""
	owner = models.CharField(max_length=128)
	#created_on = models.DateTimeField(auto_now_add=True)
	name = models.CharField(max_length=128)
	job_id = models.CharField(max_length=128)
	result = models.TextField(blank=True, null=True)
	error = models.TextField(blank=True, null=True)
	method = models.CharField(max_length=128)
	args = models.TextField(blank=True, null=True)
	orig_args = models.TextField(blank=True, null=True, help_text=_("Original payload as passed by the user before modification"))
	request = models.TextField(blank=True, null=True)
	status = models.CharField(max_length=50)
	succeeded = models.BooleanField(default=False)
	completed_on = models.DateTimeField(blank=True, null=True)
	notified_owner = models.BooleanField(default=False)
	notified_on = models.DateTimeField(blank=True, null=True)
	message = models.TextField(blank=True, null=True, help_text=_("The message sent to the user"))
	scheduled_precomputation = models.ForeignKey(ScheduledPreComputation, on_delete=models.CASCADE, 
									default="", blank=True, null=True, 
									help_text=_("Scheduled PreComputation associated with this scheduled task"))
	change_enum = models.CharField(max_length=255, blank=True, null=True, help_text=_("Change Enum applied"))
	

class ComputedResult(BaseModel):
	"""
	Model to handle Computed results
	"""
	class Meta:
		ordering = ('created_on',)

	scheduled_precomputation = models.ForeignKey(ScheduledPreComputation, null=True, blank=True, on_delete=models.CASCADE)
	cache_key = models.TextField(blank=False, null=False, help_text=_("Cache key"))
	owner = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.CASCADE)
	continent = models.ForeignKey(ContinentalAdminLevel, null=True, blank=True, on_delete=models.CASCADE)
	region = models.ForeignKey(RegionalAdminLevel, null=True, blank=True, on_delete=models.CASCADE)
	admin_zero = models.ForeignKey(AdminLevelZero, null=True, blank=True, on_delete=models.CASCADE, related_name="admin_level_zero")
	admin_one = models.ForeignKey(AdminLevelOne, null=True, blank=True, on_delete=models.CASCADE, related_name="admin_level_one")
	admin_two = models.ForeignKey(AdminLevelTwo, null=True, blank=True, on_delete=models.CASCADE, related_name="admin_level_two")
	custom_polygon =  models.TextField(blank=True, null=True, help_text=_("Custom polygon"))
	computation_type = models.CharField(max_length=255, blank=True, null=True, help_text=_("The type of computation"))
	change_enum = models.CharField(max_length=255, blank=True, null=True, help_text=_("Change Enum applied"))
	datasource = models.CharField(max_length=255, blank=False, null=False, 
				choices=settings.RASTER_SOURCES, unique=False, default='',
				help_text=_("Datasource"))
	nodata = models.FloatField(blank=True, null=True, default=0)
	prefix = models.CharField(max_length=255, blank=True, null=True, help_text=_("Prefix to be prepended to resulting raster"))
	resolution = models.FloatField(blank=True, null=True, default=0)
	subdir = models.CharField(max_length=255, blank=True, null=True, help_text=_("Subdirectory for the resulting raster"))
	raster_file = models.FileField(null=True, blank=False, help_text=_("Computed raster file"))
	start_year = models.PositiveIntegerField(
			blank=False,
			#default=current_year(),
			validators=[MinValueValidator, max_year_validator]
	)
	end_year = models.PositiveIntegerField(
			blank=False,
			#default=current_year(),
			validators=[MinValueValidator, max_year_validator]
	)
	arguments = models.TextField(blank=True, null=True, help_text=_("Computation arguments"))
	results = models.TextField(blank=True, null=True, help_text=_("Results of the computation"))
	succeeded = models.BooleanField(default=False)
	completed_on = models.DateTimeField(blank=True, null=True)
	request = models.TextField(blank=True, null=True)
	queue_msg = models.TextField(blank=False, null=False, help_text=_("Message when computation is queued"))
	
class ComputedResultItem(BaseModel):
	"""
	Model to handle Computed results
	"""
	class Meta:
		ordering = ('result',)

	def __str__(self):
		return self.label
	
	result = models.ForeignKey(ComputedResult, on_delete=models.CASCADE)
	key = models.CharField(max_length=128)
	label = models.CharField(max_length=255, blank=True, null=True, help_text=_("Pixel label"))
	count = models.IntegerField(help_text=_("Pixel count"))
	value = models.FloatField(help_text=_("Value of area"))
	custom_string_01 = models.CharField(max_length=255, blank=True, null=True, help_text=_("String 01"))
	custom_string_02 = models.CharField(max_length=255, blank=True, null=True, help_text=_("String 02"))
	custom_string_03 = models.CharField(max_length=255, blank=True, null=True, help_text=_("String 03"))
	custom_string_04 = models.CharField(max_length=255, blank=True, null=True, help_text=_("String 04"))
	custom_string_05 = models.CharField(max_length=255, blank=True, null=True, help_text=_("String 05"))

@receiver(pre_save, sender=CustomShapeFile)
def load_shapefile_to_db(sender, instance, **kwargs):
	"""
	Extract GeoJSON from the uploaded shapefile
	"""
	# load shapefile to db
	# import the shapefile into the database
	from common_gis.utils.vector_util import read_shapefile
	if instance.id is None: # new record
		if instance.shapefile:
			#instance.geom = read_shapefile(instance.shapefile)	
			instance.geom = read_shapefile(instance.shapefile.path)				
	else: # record is being updated
		current = instance
		previous = CustomShapeFile.objects.get(id=instance.id)

		#Only read file if another one has been uploaded
		if current.shapefile != previous.shapefile: 
			instance.geom = read_shapefile(instance.shapefile)	

@receiver(post_save, sender=CustomShapeFile)
def delete_uploaded_shapefile(sender, instance, created, **kwargs):
	"""
	Delete uploaded shapefile
	"""
	os.remove(instance.shapefile.path)# delete the uploaded file

@receiver(post_save, sender=ScheduledPreComputation)
def trigger_precomputation(sender, instance, created, **kwargs):
	"""
	Trigger precomputations. It would have been preferrable to use django.signals but it was not working
	""" 
	if created:
		if settings.PRECOMPUTATION_FUNCTION:
			import importlib
			function_string = settings.PRECOMPUTATION_FUNCTION
			mod_name, func_name = function_string.rsplit('.',1)
			mod = importlib.import_module(mod_name)
			func = getattr(mod, func_name)
			result = func()
			# from ldms.utils.precomputation_util import run_computations
			# run_computations()