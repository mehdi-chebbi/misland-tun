# -*- coding: utf-8 -*-
# Copyright (c) 2019, Steve Nyaga and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
#from frappe.core.doctype.sms_settings.sms_settings import send_sms as do_send_sms
import requests
import datetime
from requests.auth import HTTPBasicAuth
import communication.integrations.africastalking.sms as ATSMS
from communication.models import InboundSMS, OutboundSMS
from communication.enums import SMSSentStatusEnum, SMSApprovalStatusEnum
from django.utils import timezone
from django.utils.translation import gettext as _

def pull_sms():
	"""
	Pull SMSs via the SMS Gateway
	"""
	pass

# def send_sms(receiver_list, msg, sender_name = '', success_msg = True):
# 	"""
# 	Send SMS and Log
# 	"""
# 	return do_send()
# 	#do_send_sms(receiver_list, msg, sender_name = '', success_msg = True)	

def send_single_sms(recipient, message, message_type, reference_doctype, reference_docname, outbound_sms_doc=None):
	"""
	recipient = SMS Recipient
	destination = Shortcode
	message = message to send
	message_type = Type of message being sent
	"""
	return ATSMS.SMS().send_sms(recipients=recipient,
					message=message, 
					message_type=message_type, 
				 	reference_doctype=reference_doctype,
					reference_docname=reference_docname,
					outbound_sms_doc=outbound_sms_doc)

def save_outbound_sms(recipient, message, message_type, reference_doctype, reference_docname):
	"""Log outgoing SMS

	Args:
		recipient (str or list): Phone numbers to send SMS to
		message (str): Actual message
		message_type (str): Type of message
		reference_doctype (str): Type of record associated with the SMS
		reference_docname (str): Id of record associated with the SMS

	Returns:
		OutboundSMS: Returns OutboundSMS model
	"""
	doc = OutboundSMS(	
			posting_date=timezone.now(),			
			message=message,
			recipient=recipient,
			sent_status=SMSSentStatusEnum.PENDING.value,
			message_type=message_type,
			reference_doctype=reference_doctype, 
			reference_docname=reference_docname
		)
	doc.save()
	return doc

def save_inbound_sms(self, sender, message, message_type, message_timestamp, network, shortcode, env="Prod"):
	"""Log incoming SMS

	Args:
		sender (str): Phone number of sender
		message (str): _description_
		message_type (str): Type of message
		message_timestamp (str): Timestamp of the message
		network (str): Which network was the message sent through
		shortcode (str): Shortcode to which the message was sent
		env (str, optional): Environment . Defaults to "Prod".

	Returns:
		InboundSMS model
	"""
	doc = InboundSMS(
		posting_date=timezone.now(),		
		message=message,
		message_type=message_type,
		phone_number=sender,
		message_timestamp=message_timestamp,
		network=network,
		shortcode=shortcode,
		message_id=None,
		approval_status=SMSApprovalStatusEnum.PENDING.value,
		issue_category=None,
		issue_type=None		
	)
	doc.save()
	return doc

def make_sms(template_name, context, default_template=None):
	"""
	Replace template
	param: template_name = The template name
	param: context = context to use to render the template
	param: default_template = Template text to use in case the template has not been created 
	"""
	message = ""
	exists = frappe.db.exists('SMS Template', template_name)
	if not exists and not default_template:
		frappe.throw(_("SMS Template to generate Full Balance SMS has not been created. Create an SMS Template and give it %s as its name" % template_name))
	
	if context:
		context = {"doc": context}
		#jinja to string convertion happens here
		if exists:
			template = frappe.get_doc("SMS Template", template_name)
			message = frappe.render_template(template.template_value, context)
		else:
			message = frappe.render_template(default_template, context)
	return message

def get_delivery_statuses():
	"""
	This will be a scheduled method
	"""
	last_30_days = add_days(datetime.datetime.today(), -90) #only get delivery status for messages later than 90 days
	lst = frappe.db.get_list('Outbound SMS', 
			filters={'is_delivered': 0, 'status': 'Sent', 
					'response_message_id': ('!=', None),
					'posting_date': ('<=', last_30_days)}, 
			fields=['response_message_id'])
	#lst = [x for x in lst if x['response_message_id'] == "115681566"]
	handle = SMSHandler()
	for itm in lst[:50]:#process 50 messages at a time
		handle.get_sms_delivery_reports(itm.response_message_id)

def get_credit_balance(settings_id):
	"""
	Get the current balance of SMS units
	"""
	handle = SMSHandler()
	return handle.get_credit_balance(settings_id=settings_id)

def send_pending_sms(days=3):
	"""Process any pending sms in case there had been an issue
	By default, it will send pending SMS for the past 3 days

	Args:
		days (int, optional): Number of days before today. Defaults to 3.
	"""
	start_date = datetime.datetime.today() - datetime.timedelta(days=days)
	end_date = datetime.datetime.today()
	lst = frappe.db.get_list('Outbound SMS', 
			filters={'status': 'Pending',
					 'posting_date': ('between', [start_date, end_date])
					 },
			fields=['name'])
	handle = SMSHandler()	
	for i, x in enumerate(lst):
		print ("Sending Pending SMS: {0}. {1} of {2}".format(x.name, i+1, len(lst)))
		out_doc = frappe.get_doc('Outbound SMS', x.name)
		handle.send_sms(recipient=out_doc.recipient, 
						message=out_doc.message, 
						message_type=out_doc.message_type, 
						reference_doctype=out_doc.reference_doctype,
						reference_name=out_doc.reference_name, 
						destination=None, 
						outbound_sms_doc=out_doc)
		frappe.db.commit()

# def test_sms_delivery():
# 	handle = SMSHandler()
# 	handle.get_sms_delivery_reports("115681566")


def test_send_sms():
	# send_single_sms(recipient="0720991307", message="TEST SMS", message_type="Order Confirmation", 
	# 			 	reference_doctype="Sales Order", reference_name="SAL-ORD-2020-00005", 
	# 				 destination=None, outbound_sms_doc=None)
	send_single_sms(recipient="+254720991307", 
					message="TEST SMS", 
					message_type="Complaint", 
				 	reference_doctype="Settler", 
					reference_docname="4960171", 
					outbound_sms_doc=None)
