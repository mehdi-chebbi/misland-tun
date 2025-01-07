# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import communication.logging.file_logger as logger
from communication.utils.exception_util import process_exception
from communication.models import SMSError
from django.utils import timezone

USE_SINGLE_LOG_FILE = True #this is preferred since all events are logged in chronologically as they occur

sms_log = "sms.log"
sms_error_log = 'sms.error.log'
if USE_SINGLE_LOG_FILE:
	sms_log = "sms.log"
	sms_error_log = "sms.log" #"sms.error.log"
	
# def log_mpesa_in(args):
# 	"""
# 	Save Mpesa In record
# 	"""
# 	#args = frappe.form_dict
# 	args = frappe._dict(args)
# 	doc = make_doc('Mpesa In', args)
# 	doc.status = 'Pending' if not 'status' not in args.status else args.status
# 	doc.insert(ignore_permissions=True)	
# 	return doc

# def send_mpesa_acknowledgement(mpesa_in_doc):
# 	"""
# 	Send mpesa payment acknowledgement
# 	"""
# 	mpesa_in_doc.send_payment_or_reversal_acknowledgement()

# def make_doc(doctype, args):
# 	return frappe.get_doc({
# 			'doctype': doctype,
# 			'transaction_id': args.TransID,
# 			'transaction_time': args.TransTime,			
# 			'transaction_type': args.TransactionType,
# 			'amount': args.TransAmount,
# 			'short_code': args.BusinessShortCode,
# 			'bill_ref_number': args.BillRefNumber,
# 			'invoice_number': args.InvoiceNumber,
# 			'account_balance': args.OrgAccountBalance,
# 			'third_party_transaction_id': args.ThirdPartyTransID,
# 			'phone_number': args.MSISDN,
# 			'first_name': args.FirstName,
# 			'middle_name': args.MiddleName,
# 			'last_name': args.LastName,
# 			'manual_mpesa_receipt': args.ManualMpesaReceipt if "ManualMpesaReceipt" in args else None, #incase the record is being created manually using Manual Mpesa Receipt			
# 		})

# def log_mpesa_error(args, error_type, error_desc):
# 	"""
# 	Log mpesa error
# 	"""
# 	logger.log_error("Mpesa Error. {0}".format(error_desc), filename=mpesa_error_log)
# 	doc = make_doc('Mpesa Error Log', args)
# 	doc.error_type = error_type
# 	doc.error_description = error_desc
# 	doc.arguments = str(args)
# 	doc.insert(ignore_permissions=True)

def log_sms_error(message, error_type, error_desc, args):
	"""
	Log sms error
	"""
	logger.log_error("SMS Error: {0} | Type: {1} | Args : {2}".format(error_type, error_desc, str(args)), filename=sms_error_log)

	doc = SMSError.objects.create(
		posting_date = timezone.now(),
		error_type = error_type,
		error_description = error_desc,
		arguments = str(args)
	)
	doc.save()

# def log_c2b_validation_callback(args):
# 	"""
# 	Log c2b validation callback as received from SMS Server
# 	"""
# 	message = 'C2B_VALIDATION_CALLBACK | {}'.format(str(args))
# 	logger.log_message(message, mpesa_log)

def log_sms_credit_balance_callback(args):
	"""
	Log c2b validation callback as received from SMS Server
	"""
	message = 'SMS_CREDIT_BALANCE_CALLBACK | {}'.format(str(args))
	logger.log_message(message, sms_log)

# def log_c2b_confirmation_callback(args):
# 	"""
# 	Log c2b confirmation callback as received from SMS Server
# 	"""
# 	message = 'C2B_CONFIRMATION_CALLBACK | {}'.format(str(args))
# 	logger.log_message(message, mpesa_log)

def log_sms_received_callback(args):
	"""
	Log c2b confirmation callback as received from SMS Server
	"""
	message = 'SMS_PULLED_CALLBACK | {}'.format(str(args))
	logger.log_message(message, sms_log)

def log_sms_sent_callback(args):
	"""
	Log c2b confirmation callback as received from SMS Server
	"""
	message = 'SMS_SENT_CALLBACK: {}'.format(str(args))
	logger.log_message(message, sms_log)

def log_sms_sent(args):
	"""
	Log SMS Sending
	"""
	message = 'SMS_SENDING: {}'.format(str(args))
	logger.log_message(message, sms_log)

def log_sms_delivery_status_callback(args):
	"""
	Log c2b confirmation callback as received from SMS Server
	"""
	message = 'SMS_DELIVERY_CALLBACK | {}'.format(str(args))
	logger.log_message(message, sms_log)

# def log_invalid_token_error():
# 	"""
# 	Log invalid token error
# 	"""
# 	message = 'INVALID_TOKEN | {} | {} | {}'.format(
# 			str(frappe.request.args.to_dict()) if frappe.request else "",
# 			str(frappe.form_dict),
# 			frappe.local.request_ip)
# 	# logger.log_message(message, mpesa_error_log)
# 	log_mpesa_error(args=frappe.form_dict, error_type="Invalid Mpesa Token", error_desc=message)

def test_message():
	logger.log_message("test log message", sms_log)

def test_error():
	logger.log_error("Exception")
	a = 5
	b = 0
	try:
		c = a / b
	except Exception as e:
		logger.log_error("Exception")