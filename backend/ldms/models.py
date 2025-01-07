# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from common.models import BaseModel
from common_gis.models import AdminLevelZero, RegionalAdminLevel, ContinentalAdminLevel
from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings
from common_gis.enums import AdminLevelEnum

def current_year():
	return datetime.date.today().year
	
def max_year_validator(value):
	return MaxValueValidator(current_year())(value)

class LDMSSettings(BaseModel):
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
	forest_fire_risk_max_days = models.IntegerField(help_text=_("Maximum number of days allowed for computation of forest fire risk"))
	
	class Meta:
		abstract = False # True
		verbose_name_plural = "OSS LDMS Settings"

	def __str__(self):
		return "OSS LDMS Settings"

	def save(self, *args, **kwargs):
		"""
		Save object to the database. Removes all other entries if there
		are any.
		"""
		self.__class__.objects.exclude(id=self.id).delete()
		super(LDMSSettings, self).save(*args, **kwargs)

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
