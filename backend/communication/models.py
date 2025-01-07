from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from communication.enums import SMSApprovalStatusEnum, SMSSentStatusEnum, CommunicationChannelTypeEnum, CommunicationSentStatusEnum
from django.contrib.auth import get_user_model

User = get_user_model()
class BaseModel(models.Model):
	created_on = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_creator")
	updated_on = models.DateTimeField(auto_now=True)
	updated_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_updater")
	# is_deleted = models.Boolean(default=False)
	# deleted_on = models.DateTimeField(null=True)
	# deleted_by = models.ForeignKey(get_user_model(), null=True)
	
	class Meta:
		abstract = True

class IssueCategory(BaseModel):
	"""
	Model to handle broad issue category e.g appreciation, complaint
	"""
	category_name = models.CharField(blank=False, null=False, max_length=255, help_text=_("Issue category"))

class IssueType(BaseModel):
	"""
	Model to handle specify issue type e.g corruption, safety/hazard
	"""
	issue_type_name = models.CharField(blank=False, null=False, max_length=255, help_text=_("Issue type"))

# Create your models here.
class InboundSMS(BaseModel):
	"""
	Model to store inbound SMS message
	"""
	STATUS = []
	for itm in SMSApprovalStatusEnum:
		STATUS.append((itm.value, itm.value))

	posting_date = models.DateTimeField(default=timezone.now, help_text=_("Date when SMS was sent"))
	message = models.TextField(blank=False, null=False, help_text=_("SMS Message"))
	phone_number = models.CharField(blank=False, null=False, max_length=15, help_text=_("Sender's phone number"))
	timestamp = models.CharField(blank=True, null=True, max_length=15, help_text=_("When the message was received on the carrier's network"))
	network = models.CharField(blank=True, null=True, max_length=15, help_text=_("Which carrier network was the message sent through"))
	shortcode = models.CharField(blank=True, null=True, max_length=15, help_text=_("Which shortcode was the message sent to"))
	message_id = models.CharField(blank=True, null=True, max_length=15, help_text=_("Id assigned to the message by the carrier"))
	approval_status = models.CharField(blank=False, null=False, max_length=50, 
									choices=STATUS, 
									default=SMSApprovalStatusEnum.PENDING.value,
									help_text=_("Approval status"))
	issue_category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, 
									blank=True, null=True,
									help_text=_("Broad issue categorization"))
	issue_type = models.ForeignKey(IssueType, on_delete=models.CASCADE, 
									blank=True, null=True,
									help_text=_("Specific type of issue"))

	def send_sms(self):
		"""
		Send SMS Linked to this Inbound SMS
		"""
		pass
		
class OutboundSMS(BaseModel):
	"""
	Model to store SMS that are outbound
	"""
	STATUS = []
	for itm in SMSSentStatusEnum:
		STATUS.append((itm.value, itm.value))

	posting_date = models.DateTimeField(default=timezone.now, help_text=_("Date when SMS was created"))
	message = models.TextField(blank=False, null=False, help_text=_("SMS Message"))
	recipient = models.CharField(max_length=255, blank=False, null=False, help_text=_("Message recipients"))
	sent_status = models.CharField(blank=False, null=False, max_length=50, 
									choices=STATUS, 
									default=SMSSentStatusEnum.PENDING.value,
									help_text=_("Sent status"))
	message_type = models.CharField(max_length=255, blank=False, null=False, help_text=_("Type of message"))
	response_text = models.TextField(blank=True, null=True, help_text=_("Response message from carrier network"))
	response_code = models.IntegerField(blank=True, null=True, help_text=_("Response status codes from carrier network"))
	response_message_id = models.CharField(max_length=50, blank=True, null=True, help_text=_("ID assigned to an SMS by the carrier network"))
	is_delivered = models.BooleanField(blank=True, null=True, help_text=_("Has the SMS been delivered"))
	delivery_response_text = models.TextField(blank=True, null=True, help_text=_("Delivery status response message from carrier network"))
	delivery_status = models.TextField(blank=True, null=True, help_text=_("Delivery status of the message"))
	delivery_date = models.DateTimeField(blank=True, null=True, help_text=_("Date/Time when SMS was delivered"))
	reference_doctype = models.CharField(max_length=255, blank=True, null=True, help_text=_("Type of record associated with this SMS"))
	reference_docname = models.IntegerField(blank=True, null=True, help_text=_("ID of record associated with this SMS"))
	sms_units = models.IntegerField(blank=True, null=True, help_text=_("SMS units utilized to send this SMS"))
	sms_cost = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2, help_text=_("Cost to send SMS"))
	
class SMSError(BaseModel):
	"""
	Model to store SMS related errors
	"""
	posting_date = models.DateTimeField(default=timezone.now, help_text=_("Date when Error was logged"))
	error_type = models.CharField(blank=False, null=True, max_length=15, help_text=_("Type of error"))
	error_description = models.TextField(blank=False, null=True, help_text=_("Error description"))
	arguments = models.TextField(blank=True, null=True, help_text=_("Request arguments"))

class CommunicationSettings(BaseModel):
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
	enable_email = models.BooleanField(default=True, 
			help_text=_("If checked, the system will enable sending of emails using the specified SMTP protocols"))
	email_host = models.CharField(max_length=255, help_text=_("Email server host"))
	email_from_name = models.CharField("Sender Name", max_length=255, blank=False, null=True,
			help_text=_("Sender Name"))
	email_from_address = models.CharField("Sender Address", max_length=255, blank=False, null=True, 
			help_text=_("Sender Email Address"))	
	email_host_user = models.CharField(max_length=255, help_text=_("Email server user"))
	email_host_password = models.CharField(max_length=255, help_text=_("Email server password"))
	email_host_protocol = models.CharField(max_length=20, choices=[("TLS", "TLS"), ("SSL", "SSL")], blank=True, default="TLS", help_text=_("Email protocol"))
	email_host_port = models.IntegerField(help_text=_("Email server port"))	
	enable_push_notifications = models.BooleanField(default=True, 
			help_text=_("If checked, the system will enable sending of push notifications"))
	
	class Meta:
		abstract = False # True
		verbose_name_plural = "Communication Settings"

	def __str__(self):
		return "Communication Settings"

	def save(self, *args, **kwargs):
		"""
		Save object to the database. Removes all other entries if there
		are any.
		"""
		self.__class__.objects.exclude(id=self.id).delete()
		super(CommunicationSettings, self).save(*args, **kwargs)

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

class CommunicationLog(BaseModel):
	"""
	Model to handle communication
	"""
	CHANNEL_TYPES = [] 
	for itm in CommunicationChannelTypeEnum:
		CHANNEL_TYPES.append((itm.value, itm.value))

	SENT_STATUS = []
	for itm in CommunicationSentStatusEnum:
		SENT_STATUS.append((itm.value, itm.value))

	posting_date = models.DateTimeField(default=timezone.now, help_text=_("Date when record was created"))
	channel_type = models.TextField(_("channel_type"),
								max_length=255, 
								choices=CHANNEL_TYPES,
								help_text=_("Type of communication"											
							))
	recipient = models.CharField(_("recipient"), max_length=1000, help_text=_("Recipient"))
	recipient_details = models.TextField(_("recipient_details"), help_text=_("Details of the recipient"))
	device_id = models.CharField(max_length=255, blank=True, null=True, help_text=_("Device ID"))
	message = models.TextField(_("message"), help_text=_("Message"))
	message_type = models.CharField(max_length=255, blank=False, null=False, help_text=_("Type of message"))
	sent_status = models.CharField(blank=False, null=False, max_length=50, 
									choices=SENT_STATUS, 
									default=CommunicationSentStatusEnum.PENDING.value,
									help_text=_("Sent status"))
	is_sent = models.BooleanField(blank=True, default=False, null=True, help_text=_("Has the message been sent ?"))
	sent_date = models.DateTimeField(null=True, blank=True, help_text=_("Date when it was sent")) 
	method = models.CharField(max_length=255, blank=True, null=True, help_text=_("Triggering method"))
	arguments = models.TextField(blank=True, null=True, help_text=_("Request arguments when attempting to send"))
	request = models.TextField(blank=True, null=True, help_text=_("Http request"))
	response_text = models.TextField(blank=True, null=True, help_text=_("Response message from carrier network. Applies to SMS"))
	response_code = models.IntegerField(blank=True, null=True, help_text=_("Response status codes from carrier network. Applies to SMS"))
	response_message_id = models.CharField(max_length=255, blank=True, null=True, help_text=_("ID assigned to an SMS by the carrier network. Applies to SMS"))
	is_delivered = models.BooleanField(blank=True, null=True, help_text=_("Has the SMS been delivered. Applies to SMS"))
	delivery_response_text = models.TextField(blank=True, null=True, help_text=_("Delivery status response message from carrier network. Applies to SMS"))
	delivery_status = models.TextField(blank=True, null=True, help_text=_("Delivery status of the message. Applies to SMS"))
	delivery_date = models.DateTimeField(blank=True, null=True, help_text=_("Date/Time when SMS was delivered. Applies to SMS"))
	reference_doctype = models.CharField(max_length=255, blank=True, null=True, help_text=_("Type of record associated with this SMS. Applies to SMS"))
	reference_docname = models.IntegerField(blank=True, null=True, help_text=_("ID of record associated with this SMS. Applies to SMS"))
	sms_units = models.IntegerField(blank=True, null=True, help_text=_("SMS units utilized to send this SMS. Applies to SMS"))
	sms_cost = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2, help_text=_("Cost to send SMS. Applies to SMS"))	
	error_date = models.DateTimeField(null=True, blank=True, help_text=_("Date when error occurred")) 
	error_type = models.CharField(blank=False, null=True, max_length=255, help_text=_("Type of error encountered when sending"))
	error_description = models.TextField(blank=False, null=True, help_text=_("Error description when sending"))
	error_arguments = models.TextField(blank=True, null=True, help_text=_("Request arguments when error occured"))
	
	class Meta:
		abstract = False # True
		verbose_name_plural = "Communication Log"