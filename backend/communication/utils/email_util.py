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
from communication.utils.communication_log_util import log_communication, update_communication_error, update_communication_sent

def send(subject, message, recipients, message_type, reference_doctype, reference_docname, arguments=None, method=None, request=None):
	"""Send email"""
	return send_email_core(subject, message, recipients, message_type, reference_doctype, reference_docname, arguments, method, request)

# def send_email_core(subject, message, recipients, message_type, reference_doctype, reference_docname):

# 	def log_communication(recipient, recipient_details, message):
# 		"""
# 		Log communication
# 		"""
# 		doc = CommunicationLog(
# 			#posting_date = models.DateTimeField(default=timezone.now, help_text=_("Date when record was created"))
# 			channel_type = CommunicationChannelTypeEnum.EMAIL.key,
# 			recipient = recipient,
# 			recipient_details = recipient_details,
# 			message = str(message)
# 			message_type = message_type
# 			sent_status = CommunicationSentStatusEnum.PENDING.key,
# 			is_sent = False, 
# 			# sent_date = models.DateTimeField(null=True, blank=True, help_text=_("Date when it was sent"))
# 			# is_sent_successful = models.Boolean(default=False, help=_("Was the sending successful ?"))
# 			# response_text = models.TextField(blank=True, null=True, help_text=_("Response message from carrier network. Applies to SMS"))
# 			# response_code = models.IntegerField(blank=True, null=True, help_text=_("Response status codes from carrier network. Applies to SMS"))
# 			# response_message_id = models.CharField(max_length=50, blank=True, null=True, help_text=_("ID assigned to an SMS by the carrier network. Applies to SMS"))
# 			# is_delivered = models.BooleanField(blank=True, null=True, help_text=_("Has the SMS been delivered. Applies to SMS"))
# 			# delivery_response_text = models.TextField(blank=True, null=True, help_text=_("Delivery status response message from carrier network. Applies to SMS"))
# 			# delivery_status = models.TextField(blank=True, null=True, help_text=_("Delivery status of the message. Applies to SMS"))
# 			# delivery_date = models.DateTimeField(blank=True, null=True, help_text=_("Date/Time when SMS was delivered. Applies to SMS"))
# 			reference_doctype = reference_doctype,
# 			reference_docname = reference_docname,
# 			# sms_units = models.IntegerField(blank=True, null=True, help_text=_("SMS units utilized to send this SMS. Applies to SMS"))
# 			# sms_cost = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2, help_text=_("Cost to send SMS. Applies to SMS"))	
# 			# error_type = models.CharField(blank=False, null=True, max_length=15, help_text=_("Type of error encountered when sending"))
# 			# error_description = models.TextField(blank=False, null=True, help_text=_("Error description when sending"))
# 			# arguments = models.TextField(blank=True, null=True, help_text=_("Request arguments when attempting to send"))
# 		)
# 		doc.save()
# 		return doc

# 	"""Send email"""
# 	if type(recipients) != list:
# 		recipients = [recipients]

# 	setts = get_common_settings()
# 	if isinstance(message, CoreEmailMessage):
# 		message['subject'] = subject
# 		message['From'] = formataddr((setts.email_from_name, setts.email_from_address))
# 		email = message.as_string()
# 	else:
# 		email = MIMEMultipart()
# 		email['From'] = '{0} <{1}>'.format(setts.email_from_name, setts.email_from_address)
# 		email['To'] = ", ".join(recipients)
# 		email['Subject'] = subject
# 		email.attach(MIMEText(message))
# 		email = email.as_string()
		
# 	if setts.email_host_port:
# 		settings.EMAIL_HOST = setts.email_host
# 		settings.EMAIL_HOST_PASSWORD = setts.email_host_password
# 		settings.EMAIL_HOST_USER = setts.email_host_user
# 		settings.EMAIL_PORT = setts.email_host_port
# 		settings.EMAIL_USE_TLS = setts.email_host_protocol=="TLS"
# 		settings.EMAIL_USE_SSL = setts.email_host_protocol=="SSL"	

# 	logs = []
# 	try:		
# 		for recipient in recipients:
# 			logs.append(log_communication(
# 				recipient=recipient,
# 				recipient_details="",
# 				message=email
# 			))
# 		# Create an smtplib.SMTP object to send the email.
# 		smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, port=settings.EMAIL_PORT)
# 		smtp.ehlo()
# 		# Login to the SMTP server with username and password.
# 		smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
		
# 		# Send email with the smtp object sendmail method.
# 		send_errors = smtp.sendmail(setts.email_from_address, recipients, email)
# 		# send_errors = smtp.sendmail(settings.EMAIL_HOST_USER, recipients, email)
# 		# Quit the SMTP server after sending the email.
# 		smtp.quit()

# 		# update sent status
# 		for rec in logs:
# 			rec.is_sent = True
# 			rec.sent_date = timezone.now()
# 			rec.sent_status = CommunicationSentStatusEnum.SENT.key
# 			rec.save()
# 		return not send_errors
# 	except Exception as e:
# 		error = str(e)
# 		# update sent status
# 		for rec in logs:
# 			rec.error_date = timezone.now()
# 			rec.error_type = str(type(e))
# 			rec.error_description = error
# 			rec.arguments = str(model_to_dict(setts))
# 			rec.save()
# 		log_error(error) # log error to flat file

def send_email_core(subject, message, recipients, message_type, reference_doctype, reference_docname, arguments, method, request):
	def _log_communication(recipient, recipient_details, message):
		"""
		Log communication
		"""
		# doc = CommunicationLog(
		# 	#posting_date = models.DateTimeField(default=timezone.now, help_text=_("Date when record was created"))
		# 	channel_type = CommunicationChannelTypeEnum.EMAIL.value,
		# 	recipient = recipient,
		# 	recipient_details = recipient_details,
		# 	message = str(message),
		# 	message_type = message_type,
		# 	is_sent = False,
		# 	sent_status = CommunicationSentStatusEnum.PENDING.value,
		# 	# sent_date = models.DateTimeField(null=True, blank=True, help_text=_("Date when it was sent"))
		# 	# is_sent_successful = models.Boolean(default=False, help=_("Was the sending successful ?"))
		# 	# response_text = models.TextField(blank=True, null=True, help_text=_("Response message from carrier network. Applies to SMS"))
		# 	# response_code = models.IntegerField(blank=True, null=True, help_text=_("Response status codes from carrier network. Applies to SMS"))
		# 	# response_message_id = models.CharField(max_length=50, blank=True, null=True, help_text=_("ID assigned to an SMS by the carrier network. Applies to SMS"))
		# 	# is_delivered = models.BooleanField(blank=True, null=True, help_text=_("Has the SMS been delivered. Applies to SMS"))
		# 	# delivery_response_text = models.TextField(blank=True, null=True, help_text=_("Delivery status response message from carrier network. Applies to SMS"))
		# 	# delivery_status = models.TextField(blank=True, null=True, help_text=_("Delivery status of the message. Applies to SMS"))
		# 	# delivery_date = models.DateTimeField(blank=True, null=True, help_text=_("Date/Time when SMS was delivered. Applies to SMS"))
		# 	reference_doctype = reference_doctype,
		# 	reference_docname = reference_docname,
		# 	arguments=arguments, 
		# 	method=method,
		# 	request=request
		# 	# sms_units = models.IntegerField(blank=True, null=True, help_text=_("SMS units utilized to send this SMS. Applies to SMS"))
		# 	# sms_cost = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2, help_text=_("Cost to send SMS. Applies to SMS"))	
		# 	# error_type = models.CharField(blank=False, null=True, max_length=15, help_text=_("Type of error encountered when sending"))
		# 	# error_description = models.TextField(blank=False, null=True, help_text=_("Error description when sending"))
		# 	# arguments = models.TextField(blank=True, null=True, help_text=_("Request arguments when attempting to send"))
		# )
		# doc.save()
		doc = log_communication(
			recipient=recipient, 
			recipient_details=recipient_details, 
			channel_type=CommunicationChannelTypeEnum.EMAIL.value,
			message=message, 
			message_type=message_type, 
			reference_doctype=reference_doctype, 
			reference_docname=reference_docname, 
			arguments=arguments, 
			method=method, 
			request=request)
		return doc

	def save_log(msg):
		"""
		Generate communication log records
		"""
		recs = []
		for recipient in recipients:
			recs.append(_log_communication(
				recipient=recipient,
				recipient_details="",
				message=msg
			))
		return recs

	def update_sent():
		"""
		Update communication log records
		"""
		for rec in log_recs:
			update_communication_sent(rec)
			# rec.sent_date = timezone.now()
			# rec.sent_status = CommunicationSentStatusEnum.SENT.value
			# rec.is_sent = True
			# rec.save()

	def update_error(exception):
		"""
		Update communication log erro
		"""
		error = str(exception)
		# dct = model_to_dict(setts)
		# del dct['email_host_password']
		# del dct['created_by']
		# del dct['updated_by']
		# update sent status
		for rec in log_recs:
			update_communication_error(rec, exception=exception, comm_settings=setts)
			# rec.error_date = timezone.now()
			# rec.error_type = str(type(exception))
			# rec.error_description = error
			# rec.error_arguments = str(dct)
			# rec.sent_status = CommunicationSentStatusEnum.FAILED.value
			# rec.is_sent = False
			# rec.save()
	
	from common.utils.log_util import log_error
	"""Send email"""
	if type(recipients) != list:
		recipients = [recipients]

	setts = get_communication_settings()
	if isinstance(message, CoreEmailMessage):
		message['subject'] = subject
		message['From'] = formataddr((setts.email_from_name, setts.email_from_address))
		email = message.as_string()
	else:
		email = MIMEMultipart()
		email['From'] = '{0} <{1}>'.format(setts.email_from_name, setts.email_from_address)
		email['To'] = ", ".join(recipients)
		email['Subject'] = subject
		email.attach(MIMEText(message))
		email = email.as_string()
		
	if setts.email_host_port:
		settings.EMAIL_HOST = setts.email_host
		settings.EMAIL_HOST_PASSWORD = setts.email_host_password
		settings.EMAIL_HOST_USER = setts.email_host_user
		settings.EMAIL_PORT = setts.email_host_port
		settings.EMAIL_USE_TLS = setts.email_host_protocol=="TLS"
		settings.EMAIL_USE_SSL = setts.email_host_protocol=="SSL"	

	def _send_no_ssl():
		try:
			print("Sending email to {0}".format(recipients)) 
			# Create an smtplib.SMTP object to send the email.
			smtp = smtplib.SMTP(settings.EMAIL_HOST, port=settings.EMAIL_PORT)
			smtp.ehlo()
			smtp.starttls()
			# Login to the SMTP server with username and password.
			smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
			
			# Send email with the smtp object sendmail method.
			send_errors = smtp.sendmail(setts.email_from_address, recipients, email)
			# send_errors = smtp.sendmail(settings.EMAIL_HOST_USER, recipients, email)
			# Quit the SMTP server after sending the email.
			smtp.quit()
			update_sent()
			return not send_errors
		except Exception as e:
			print("Email sending without ssl error: " + str(e))
			update_error(e)
			log_error(str(e))

	def _send_with_ssl(): 
		try:
			print("Sending email to {0}".format(recipients))
			# Create an smtplib.SMTP object to send the email.
			smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, port=settings.EMAIL_PORT)
			smtp.ehlo()
			# Login to the SMTP server with username and password.
			smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
			
			# Send email with the smtp object sendmail method.
			send_errors = smtp.sendmail(setts.email_from_address, recipients, email)
			# send_errors = smtp.sendmail(settings.EMAIL_HOST_USER, recipients, email)
			# Quit the SMTP server after sending the email.			
			smtp.quit()
			update_sent()
			return not send_errors
		except Exception as e:
			print("Email sending with ssl error: " + str(e))
			update_error(e)
			log_error(str(e))
	
	log_recs = save_log(email)
	if setts.enable_email:
		if "office365" in settings.EMAIL_HOST: #smtp.office365.com does not support smtp.SMTP_SSL
			return _send_no_ssl()
		else:
			return _send_with_ssl()
	else:
		print("Sending emails is disabled")
		return False
