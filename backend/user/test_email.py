from email.message import EmailMessage as CoreEmailMessage  
import smtplib# Import smtplib library to send email in python 
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_core(subject="Test Email", message="Message for testing email", recipients="stevenyaga@gmail.com"):
	"""Send email"""
	if type(recipients) != list:
		recipients = [recipients]

	email_from_name = "Misland Oss"
	email_from_address = "plateforme@oss.org.tn"
	if isinstance(message, CoreEmailMessage):
		message['subject'] = subject
		message['From'] = formataddr((email_from_name, email_from_address))
		email = message.as_string()
	else:
		email = MIMEMultipart()
		email['From'] = '{0} <{1}>'.format(email_from_name, email_from_address)
		email['To'] = ", ".join(recipients)
		email['Subject'] = subject
		email.attach(MIMEText(message))
		email = email.as_string()
		
	EMAIL_HOST = "smtp.office365.com"
	EMAIL_HOST_PASSWORD = "OSSinfo21"
	EMAIL_HOST_USER = "plateforme@oss.org.tn"
	EMAIL_PORT = 587
	EMAIL_USE_TLS = False
	EMAIL_USE_SSL = True

	def _send_no_ssl():
		try:
			print("Sending email to {0}".format(recipients)) 
			# Create an smtplib.SMTP object to send the email.
			smtp = smtplib.SMTP(EMAIL_HOST, port=EMAIL_PORT)
			smtp.ehlo()
			smtp.starttls()
			# Login to the SMTP server with username and password.
			smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
			
			# Send email with the smtp object sendmail method.
			send_errors = smtp.sendmail(email_from_address, recipients, email)
			# send_errors = smtp.sendmail(settings.EMAIL_HOST_USER, recipients, email)
			# Quit the SMTP server after sending the email.
			smtp.quit()
			return not send_errors
		except Exception as e:
			print(str(e))
			#log_error(str(e))
			pass

	def _send_with_ssl(): 
		try:
			print("Sending email to {0}".format(recipients))
			# Create an smtplib.SMTP object to send the email.
			smtp = smtplib.SMTP_SSL(EMAIL_HOST, port=EMAIL_PORT)
			smtp.ehlo()
			# Login to the SMTP server with username and password.
			smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
			
			# Send email with the smtp object sendmail method.
			send_errors = smtp.sendmail(email_from_address, recipients, email)
			# send_errors = smtp.sendmail(settings.EMAIL_HOST_USER, recipients, email)
			# Quit the SMTP server after sending the email.
			smtp.quit()
			return not send_errors
		except Exception as e:
			print(str(e))
			#log_error(str(e))
			pass
	
	if "office365" in EMAIL_HOST:
		return _send_no_ssl()
	else:
		return _send_with_ssl()
send_email_core()