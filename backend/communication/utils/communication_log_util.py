from django.core.mail import EmailMessage, send_mail
from email.message import EmailMessage as CoreEmailMessage
from django.conf import settings
import smtplib# Import smtplib library to send email in python
from communication.utils.settings_util import get_communication_settings
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from communication.models import CommunicationLog
from django.utils import timezone
from communication.enums import CommunicationChannelTypeEnum, CommunicationSentStatusEnum
import datetime
from django.forms.models import model_to_dict

def log_communication(recipient, recipient_details, channel_type, message, message_type, reference_doctype, reference_docname, arguments, method, request, device_id=None):
	"""
	Log communication
	"""
	doc = CommunicationLog(
		#posting_date = models.DateTimeField(default=timezone.now, help_text=_("Date when record was created"))
		channel_type = channel_type, # CommunicationChannelTypeEnum.EMAIL.value,
		recipient = recipient,
		recipient_details = recipient_details,
		message = str(message),
		message_type = message_type,
		is_sent = False,
		sent_status = CommunicationSentStatusEnum.PENDING.value,
		# sent_date = models.DateTimeField(null=True, blank=True, help_text=_("Date when it was sent"))
		# is_sent_successful = models.Boolean(default=False, help=_("Was the sending successful ?"))
		# response_text = models.TextField(blank=True, null=True, help_text=_("Response message from carrier network. Applies to SMS"))
		# response_code = models.IntegerField(blank=True, null=True, help_text=_("Response status codes from carrier network. Applies to SMS"))
		# response_message_id = models.CharField(max_length=50, blank=True, null=True, help_text=_("ID assigned to an SMS by the carrier network. Applies to SMS"))
		# is_delivered = models.BooleanField(blank=True, null=True, help_text=_("Has the SMS been delivered. Applies to SMS"))
		# delivery_response_text = models.TextField(blank=True, null=True, help_text=_("Delivery status response message from carrier network. Applies to SMS"))
		# delivery_status = models.TextField(blank=True, null=True, help_text=_("Delivery status of the message. Applies to SMS"))
		# delivery_date = models.DateTimeField(blank=True, null=True, help_text=_("Date/Time when SMS was delivered. Applies to SMS"))
		reference_doctype = reference_doctype,
		reference_docname = reference_docname,
		arguments=arguments, 
		method=method,
		request=request,
		device_id=device_id
		# sms_units = models.IntegerField(blank=True, null=True, help_text=_("SMS units utilized to send this SMS. Applies to SMS"))
		# sms_cost = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2, help_text=_("Cost to send SMS. Applies to SMS"))	
		# error_type = models.CharField(blank=False, null=True, max_length=15, help_text=_("Type of error encountered when sending"))
		# error_description = models.TextField(blank=False, null=True, help_text=_("Error description when sending"))
		# arguments = models.TextField(blank=True, null=True, help_text=_("Request arguments when attempting to send"))
	)
	doc.save()
	return doc

def update_communication_sent(rec):
	"""
	Update communication log record with sent status
	"""
	rec.sent_date = timezone.now()
	rec.sent_status = CommunicationSentStatusEnum.SENT.value
	rec.is_sent = True
	rec.save()

def update_communication_error(rec, exception, comm_settings=None):
	"""
	Update communication log error
	"""
	error = str(exception)
	if not comm_settings:
		comm_settings = get_communication_settings()
	dct = model_to_dict(comm_settings)
	del dct['email_host_password']
	del dct['created_by']
	del dct['updated_by']
	# update send error status 
	rec.error_date = timezone.now()
	rec.error_type = str(type(exception))
	rec.error_description = error
	rec.error_arguments = str(dct)
	rec.sent_status = CommunicationSentStatusEnum.FAILED.value
	rec.is_sent = False
	rec.save()