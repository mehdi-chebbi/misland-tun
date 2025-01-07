from communication.utils import email_util 
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from communication.utils.settings_util import get_communication_settings

def send_email(subject, message, recipients, message_type, reference_doctype, reference_docname, arguments=None, method=None, request=None):
	setts = get_communication_settings()
	if setts.email_host_port:
		settings.EMAIL_HOST = setts.email_host
		settings.EMAIL_HOST_PASSWORD = setts.email_host_password
		settings.EMAIL_HOST_USER = setts.email_host_user
		settings.EMAIL_PORT = setts.email_host_port
		settings.EMAIL_USE_TLS = setts.email_host_protocol=="TLS"
		settings.EMAIL_USE_SSL = setts.email_host_protocol=="SSL"	
	return email_util.send(subject, message, recipients, message_type, reference_doctype, reference_docname, arguments, method, request)