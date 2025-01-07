# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from django.template.defaultfilters import slugify
import os
from django.contrib.auth import get_user_model
from common.enums import CommunicationChannelTypeEnum, CommunicationSentStatusEnum
from django.db.models import Q

User = get_user_model()

# Create your models here.

class SearchableQuerySet(models.QuerySet):
	"""Generic queryset for admin levels
	"""
	def search(self, query=None):
		qs = self
		if query is not None:			
			if self.values: #If query set has values,
				lst = list(enumerate(self))
				if not lst:
					return qs
				obj = lst[0][1]
				cols = obj.search_columns
				if cols:
					or_condition = Q()
					for fld in cols:
						column = fld
						search_type = 'icontains' #case insensitive
						filter = column + '__' + search_type
						or_condition.add(Q(**{ filter: query }), Q.OR)
					qs = qs.filter(or_condition).distinct() # distinct is often necessary with Q
		return qs

class SearchableModelManager(models.Manager):
	"""
	Extend GeoManager to maintain the ability for spatial querying as we allow for more definition of methods
	"""
	def get_queryset(self):
		return SearchableQuerySet(self.model, using=self._db)
	
	def search(self, query=None):
		return self.get_queryset().search(query=query)

User = get_user_model()
class BaseModel(models.Model):
	"""Base model from which all models should inherit from

	Args:
		models (_type_): _description_
	"""
	created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_creator")
	updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
	updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_updater")
	# is_deleted = models.Boolean(default=False)
	# deleted_on = models.DateTimeField(null=True)
	# deleted_by = models.ForeignKey(get_user_model(), null=True)
	
	class Meta:
		abstract = True		

class Gallery(BaseModel):
	"""
	Class to store images to show on the front end
	"""	
	image_name = models.CharField(max_length=255, blank=False, help_text=_("Name of image"))
	image_file = models.FileField(max_length=255, blank=False, help_text=_("Attach image"))
	image_desc = models.TextField(blank=True, help_text=_("Image description"))
	is_published = models.BooleanField(help_text=_("If not published, the image will not be shown to users"))
	is_document = models.BooleanField(help_text=_("Is this a document"), default=0)

	class Meta:
		verbose_name_plural = "Gallery"

class Topic(BaseModel):
	"""
	Generic topics for grouping FAQ
	"""
	topic_name = models.CharField(blank=False, max_length=255)
	slug = models.SlugField(max_length=255)
	sort_order = models.IntegerField(default=0, verbose_name=_("Sort order"), 
							help_text=_("The order you would like the topic to be displayed"))

	def get_absolute_url(self):
		return '/faq/' + self.slug

	class Meta:
		verbose_name = _("Topic")
		verbose_name_plural = _("Topics")
		ordering = ['sort_order', 'topic_name']

	def __unicode__(self):
		return self.topic_name
	
	def __str__(self):
		return self.topic_name

class Question(BaseModel):
	INACTIVE = 0
	ACTIVE = 1
	HEADER = 2

	STATUS_CHOICES = (
		(ACTIVE, _("Active")),
		(INACTIVE, _("Inactive")),
		(HEADER, _("Group Header")),
	)
	question_text = models.TextField(_("question"), help_text="The question details")
	answer = models.TextField(_("answer"), blank=True, help_text=_("The answer text"))
	topic = models.ForeignKey(Topic, verbose_name=_("topic"), related_name="questions", on_delete=models.CASCADE)
	slug = models.SlugField(_("slug"), max_length=100, blank=True, null=True)
	status = models.IntegerField(_("status"), choices=STATUS_CHOICES,
								default=INACTIVE,
								help_text=_("Only questions with their status set to 'Active' will be "
											"displayed. Questions marked as 'Group Header are treated as "
											"views"
								))
	protected = models.BooleanField(_('is protected'), default=False,
				help_text=_("Set true if this question is only visible to authenticated users"))
	sort_order = models.IntegerField(default=0, verbose_name=_("Sort order"),
							 help_text=_("The order you would like this question to be displayed"))
	created_on = models.DateTimeField(_('created on'), default=timezone.now)
	updated_on = models.DateTimeField(_('updated on'), blank=True, null=True, default=timezone.now)
	created_by = models.ForeignKey(User, verbose_name=_('created by'), blank=True,
									null=True, related_name="+", on_delete=models.CASCADE)
	updated_by = models.ForeignKey(User, verbose_name=_('updated by'), blank=True,
									null=True, related_name="+", on_delete=models.CASCADE)

	def save(self, *args, **kwargs):
		# Set date updated
		self.updated_on = timezone.now()

		# create a unique slug
		if not self.slug:
			suffix = 0
			potential = base = slugify(self.question_text[:90])
			while not self.slug:
				if suffix:
					potential = "%s-%s" % (base, suffix)
				if not Question.objects.filter(slug=potential).exists():
					self.slug = potential
				# We hit a conflicting slug; increment suffix and try again
				suffix += 1
		
		super(Question, self).save(*args, **kwargs)

	def is_header(self):
		return self.status == Question.HEADER

	def is_active(self):
		return self.status == Question.ACTIVE

class CommonSettings(BaseModel):
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
	# # frontend_port = models.IntegerField(blank=False, null=False, help_text=_("Server port for the front end"))
	# email_host = models.CharField(max_length=255, help_text=_("Email server host"))
	# email_from_name = models.CharField("Sender Name", max_length=255, blank=False, null=True,
	# 		help_text=_("Sender Name"))
	# email_from_address = models.CharField("Sender Address", max_length=255, blank=False, null=True, 
	# 		help_text=_("Sender Email Address"))	
	# email_host_user = models.CharField(max_length=255, help_text=_("Email server user"))
	# email_host_password = models.CharField(max_length=255, help_text=_("Email server password"))
	# email_host_protocol = models.CharField(max_length=20, choices=[("TLS", "TLS"), ("SSL", "SSL")], blank=True, default="TLS", help_text=_("Email protocol"))
	# email_host_port = models.IntegerField(help_text=_("Email server port"))	
	
	backend_url = models.CharField(_("Backend url"), max_length=200, 
			default="http://0.0.0.0/", 
			blank=False, 
			null=False,
			help_text=_("URL of server (without port) hosting the backend."))
	backend_port = models.IntegerField(_("Backend port"), default=80, 
			help_text=_("Port from which the system is served"))
	override_backend_port = models.BooleanField(default=True, 
			help_text=_("If checked, the system will override the default port and use the value of Backend port. Important when constructing URL of computed Raster"))
	enable_execution_monitoring = models.BooleanField(default=False, help_text=_("Enable monitoring of computations"))


	class Meta:
		abstract = False # True
		verbose_name_plural = "General Settings"

	def __str__(self):
		return "Common Settings"

	def save(self, *args, **kwargs):
		"""
		Save object to the database. Removes all other entries if there
		are any.
		"""
		self.__class__.objects.exclude(id=self.id).delete()
		super(CommonSettings, self).save(*args, **kwargs)

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

class MonitoringLog(BaseModel):
	def __str__(self):
		return "Monitoring Log"

	execution_name = models.CharField(max_length=255, blank=False, null=True, help_text="Execution Name")
	params = models.TextField(blank=True, null=True, help_text=_("Parameters to execution"))
	caller_id = models.CharField(max_length=255, blank=True, null=True, help_text=_("Calling object id"))
	caller_type = models.CharField(max_length=255, null=True, blank=False, help_text=_("Calling object type"))
	caller_details = models.CharField(max_length=255, null=True, blank=False, help_text=_("Calling object details"))
	execution_start_time = models.DateTimeField(default=timezone.now)
	pre_execution_stats = models.JSONField(blank=True, null=True, help_text=_("Resources pre-execution"))
	# resource_delta_stats = models.JSONField(blank=True, null=True, help_text=_("Resources utilization change"))
	post_execution_stats = models.JSONField(blank=True, null=True, help_text=_("Resources post-execution"))
	boot_time = models.DateTimeField(null=True, blank=True, help_text=_("Server boot time"))
	uptime_minutes = models.IntegerField(blank=True, default=False, null=True, help_text=_("Uptime in minutes?"))
	execution_end_time = models.DateTimeField(null=True, blank=True)
	is_completed = models.BooleanField(blank=True, default=False, null=True, help_text=_("Has the monitoring completed ?"))
	is_critical_memory_usage = models.BooleanField(blank=True, default=False, null=True, help_text=_("Is memory usage critical?"))
	is_critical_cpu_usage = models.BooleanField(blank=True, default=False, null=True, help_text=_("Is cpu usage critical?"))
	is_critical_disk_usage = models.BooleanField(blank=True, default=False, null=True, help_text=_("Is disk usage critical?"))
	is_critical_temp = models.BooleanField(blank=True, default=False, null=True, help_text=_("Is temperature critical?"))
	mem_profile = models.TextField(blank=True, null=True, help_text=_("Memory profile"))

class MonitoringLogItem(models.Model):
	monitoring_log = models.ForeignKey(MonitoringLog, blank=True,
									null=True, related_name="+", on_delete=models.CASCADE)
	time_entry = models.DateTimeField(null=True, blank=True)
	cpu = models.CharField(max_length=255, null=True, blank=False, help_text=_("CPU utilized(%)"))
	memory = models.CharField(max_length=255, null=True, blank=False, help_text=_("Memory usage (GB)"))
	disk = models.CharField(max_length=255, null=True, blank=False, help_text=_("Disk usage (GB)"))
	highest_temp = models.CharField(max_length=255, null=True, blank=False, help_text=_("Highest Temp (C)"))

# class CommunicationLog(BaseModel):
# 	"""
# 	Model to handle communication
# 	"""
# 	CHANNEL_TYPES = [] 
# 	for itm in CommunicationChannelTypeEnum:
# 		CHANNEL_TYPES.append((itm.value, itm.value))

# 	SENT_STATUS = []
# 	for itm in CommunicationSentStatusEnum:
# 		SENT_STATUS.append((itm.value, itm.value))

# 	posting_date = models.DateTimeField(default=timezone.now, help_text=_("Date when record was created"))
# 	channel_type = models.TextField(_("channel_type"),
# 								max_length=255, 
# 								choices=CHANNEL_TYPES,
# 								help_text=_("Type of communication"											
# 								))
# 	recipient = models.CharField(_("recipient"), max_length=1000, help_text=_("Recipient"))
# 	recipient_details = models.TextField(_("recipient_details"), help_text=_("Details of the recipient"))
# 	message = models.TextField(_("message"), help_text=_("Message"))
# 	message_type = models.CharField(max_length=255, blank=False, null=False, help_text=_("Type of message"))
# 	sent_status = models.CharField(blank=False, null=False, max_length=50, 
# 									choices=SENT_STATUS, 
# 									default=CommunicationSentStatusEnum.PENDING.value,
# 									help_text=_("Sent status"))
# 	is_sent = models.BooleanField(blank=True, default=False, null=True, help_text=_("Has the message been sent ?"))
# 	sent_date = models.DateTimeField(null=True, blank=True, help_text=_("Date when it was sent")) 
# 	method = models.CharField(max_length=255, blank=True, null=True, help_text=_("Triggering method"))
# 	arguments = models.TextField(blank=True, null=True, help_text=_("Request arguments when attempting to send"))
# 	request = models.TextField(blank=True, null=True, help_text=_("Http request"))
# 	response_text = models.TextField(blank=True, null=True, help_text=_("Response message from carrier network. Applies to SMS"))
# 	response_code = models.IntegerField(blank=True, null=True, help_text=_("Response status codes from carrier network. Applies to SMS"))
# 	response_message_id = models.CharField(max_length=255, blank=True, null=True, help_text=_("ID assigned to an SMS by the carrier network. Applies to SMS"))
# 	is_delivered = models.BooleanField(blank=True, null=True, help_text=_("Has the SMS been delivered. Applies to SMS"))
# 	delivery_response_text = models.TextField(blank=True, null=True, help_text=_("Delivery status response message from carrier network. Applies to SMS"))
# 	delivery_status = models.TextField(blank=True, null=True, help_text=_("Delivery status of the message. Applies to SMS"))
# 	delivery_date = models.DateTimeField(blank=True, null=True, help_text=_("Date/Time when SMS was delivered. Applies to SMS"))
# 	reference_doctype = models.CharField(max_length=255, blank=True, null=True, help_text=_("Type of record associated with this SMS. Applies to SMS"))
# 	reference_docname = models.IntegerField(blank=True, null=True, help_text=_("ID of record associated with this SMS. Applies to SMS"))
# 	sms_units = models.IntegerField(blank=True, null=True, help_text=_("SMS units utilized to send this SMS. Applies to SMS"))
# 	sms_cost = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2, help_text=_("Cost to send SMS. Applies to SMS"))	
# 	error_date = models.DateTimeField(null=True, blank=True, help_text=_("Date when error occurred")) 
# 	error_type = models.CharField(blank=False, null=True, max_length=255, help_text=_("Type of error encountered when sending"))
# 	error_description = models.TextField(blank=False, null=True, help_text=_("Error description when sending"))
# 	error_arguments = models.TextField(blank=True, null=True, help_text=_("Request arguments when error occured"))

