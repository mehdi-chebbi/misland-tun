# -*- coding: utf-8 -*-
# Copyright (c) 2019, Steve Nyaga and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
#from frappe.core.doctype.sms_settings.sms_settings import send_sms as do_send_sms
import requests
import datetime
from requests.auth import HTTPBasicAuth
from frappe import _
import e_biz.utils.logger as ebiz_logger
from frappe.utils import cint

class SMSHandler:
	def __init__(self, settings=None):
		"""Initialize SMSHandler

		Args:
			settings (Bulk SMS Settings): Bulk SMS Settings to use. If not specified, default Bulk SMS Settings will be used
		"""
		self.default_settings = None
		if not settings:
			self.get_default_settings()
		else:
			self.default_settings = settings
		self.do_actual_sms_send = self.default_settings.disable_sms_sending == False

	def _send_sms_africastalking(self, recipient, message, message_type, reference_doctype, reference_name, outbound_sms_doc=None):
		"""
		Make request to Bongatech servers. Careful you do not leave unterminated commas in the json body, otherwise the 
		server will throw an unsupported data type error
		@param: do_not_send_sms = if True, only a simulation will happen and no actual sending of SMS
		"""

		def update_message_response(response):
			"""
			Send body of the format:
			[
				{
					"sender": "BONGATECH",
					"message": "Test API",
					"phone": "07XXXXXXXX",
					"correlator": 1
				},
				{
					"sender": "BONGATECH",
					"message": "Test API 2",
					"phone": "07XXXXXXXX",
					"correlator": 2
				}
			]

			Response of the format : 
			[
				{
					"status": true,
					"message": "Message successfully queued!",
					"data": {
						"correlator": 1,
						"uniqueId": "unique-string",
						"phone": "254XXXXXXXXX",
						"sms_units": 1
					}
				},
				{
					"status": true,
					"message": "Message successfully queued!",
					"data": {
						"correlator": 2,
						"uniqueId": "unique-string",
						"phone": "254XXXXXXXXX",
						"sms_units": 1
					}
				}
			]

			Example: {'status': True, 'message': 'Message successfully queued!', 'data': {'correlator': 'SOUT-000002', 'uniqueId': '2e4924e9-47aa-4ac8-8aaa-e28e8043e733', 'phone': '254720991307', 'sms_units': 1}}
			"""
			# mp = {	
			# 	'200' : 'Successful Request Call',
			# 	'1001' : 'Invalid sender id',
			# 	'1002' : 'Network not allowed',
			# 	'1003' : 'Invalid mobile number',
			# 	'1004' : 'Low bulk credits',
			# 	'1005' : 'Failed. System error',
			# 	'1006' : 'Invalid credentials',
			# 	'1007' : 'Failed. System error',
			# 	'1008' : 'No Delivery Report',
			# 	'1009' : 'unsupported data type',
			# 	'1010' : 'unsupported request type',
			# 	'4090' : 'Internal Error. Try again after 5 minutes',
			# 	'4091' : 'No Partner ID is Set',
			# 	'4092' : 'No API KEY Provided',
			# 	'4093' : 'Details Not Found'
			# }
			responses = response.json()#['responses']
			resp_code = responses.get('status')
			resp_text = responses.get('message')

			doc.status = "Sent" if resp_code == True else "Pending"
			doc.response_type = resp_code
			doc.response_text = resp_text
			doc.response_message_id = responses.get('data').get('uniqueId')
			doc.sms_units = responses.get('data').get('sms_units')
			doc.save()
			return responses.get('data').get('uniqueId')
		
		if not outbound_sms_doc:
			doc = self.save_outbound_sms(recipient, message, message_type, reference_doctype, reference_name)
		else:
			doc = outbound_sms_doc

		access_token = self.get_parameter("client_secret")
		headers = {} 	
		headers.update({
			'Content-type': 'application/json',
			"Accept": "application/json",
			"Authorization": "Bearer %s" % access_token
		})
		body = {
				"sender": self.get_parameter("client_id"), # "77",				
				#"message": frappe.safe_decode(message).encode('utf-8'), # "For Python 2",
				"message": frappe.safe_encode(message).decode('utf-8'), # "For both Python 2 and 3",
				"phone": recipient, 
				"correlator": doc.name
			}	
		if not self.default_settings.send_sms_gateway_url:
			frappe.throw("SMS Gateway URL in Bulk SMS Settings is empty. You must specify it")
		
		external_sms_id = None
		if self.do_actual_sms_send:
			response = requests.post(self.default_settings.send_sms_gateway_url, 
					headers=headers, json=body)
			ebiz_logger.log_sms_sent_callback(response.__dict__)
			print (response.text)
			external_sms_id = update_message_response(response)
		return doc.name, external_sms_id
		
	def _send_sms_onfonmedia(self, recipient, destination, message, message_type, reference_doctype, reference_name):
		"""
		Make request to Safcom servers
		"""
		def get_authenticate_token():
			"""
			get authentication token
			"""			
			def authenticate_onfonmedia():				
				body= get_authentication_body_content()
				body.update({'grant_type': 'password'})
				res = requests.post(self.default_settings.access_token_url, 
									data=body)
				print (res.text)
				return res.json()['access_token']

			return authenticate_onfonmedia()

		def get_authentication_body_content():
			"""
			Build request body content
			"""
			body = {}
			for d in self.default_settings.get("parameters"):
				if d.header == 0:
					body.update({d.parameter: d.value})					
			return body

		def update_message_response(response):
			mp = {	
				'100': 'Transaction Processed Successfully',
				'101': 'Invalid mobile number provided',
				'102': 'Invalid destination',
				'103': 'Duplicate SMS ID provided',
				'104': 'Bulk SMS Depleted',
				'105': 'Empty packet',
				'106': 'Invalid SMS ID',
				'107': 'Exceeded limit per request',
				'404': 'General Error'
			}

			resp_text = mp['{0}'.format(response.status)]

			doc.status = "Sent" if response[0].status == 100 else "Pending"
			doc.message_id = response[0].message_id
			doc.response_type = response.status
			doc.response_text = resp_text
			doc.save()
			return response[0].message_id

		access_token = get_authenticate_token()
		headers = { "Authorization": "Bearer %s" % access_token }
		headers.update({'Content-type': 'application/json'}) #, 'Accept': 'text/plain'})
		body= [{
				"msisdn":recipient,
				"destination": '22141',
				"sms_id": '12333',
				"message": frappe.safe_decode(message).encode('utf-8'),
				# "sms_id": '12333' # frappe.safe_decode("123666").encode('utf-8'),# "{0}".format(doc.message_id)
			}]
		# headers.update(get_headers())
		# request = kwargs.pop("request")		
		# url = kwargs.pop("url")
		# headers = kwargs.pop("headers")
		external_sms_id = None
		doc = self.save_outbound_sms(recipient, message, message_type, reference_doctype, reference_name)		
		if self.do_actual_sms_send:
			response = requests.post(self.default_settings.send_sms_gateway_url, 
						headers=headers, json=body)
			print (response.text)
			external_sms_id = update_message_response(response)

		return doc.name, external_sms_id

	def _send_sms_celcomafrica(self, recipient, message, message_type, reference_doctype, reference_name, outbound_sms_doc=None): #, do_not_send_sms=False):
		"""
		Make request to celcom servers. Careful you do not leave unterminated commas in the json body, otherwise the 
		server will throw an unsupported data type error
		@param: do_not_send_sms = if True, only a simulation will happen and no actual sending of SMS
		"""

		def update_message_response(response):
			"""
			Response of the format : 
			"responses": [				
				{
					"respose-code": 200,
					"response-code": 200,
					"response-description": "Success",
					"mobile": "254720991307",
					"messageid": 331033293,
					"clientsmsid": "",
					"networkid": "1"
				}
			]
			or 
			"responses": [
					{
						"response-code": 200,
						"response-description": "Success",
						"mobile": "254720991307",
						"messageid": "XBBdqnhA4bwpPKEJ",
						"networkid": 1
					}
				]
			"""
			response_code_key = "response-code" #respose-code
			mp = {	
				'200' : 'Successful Request Call',
				'1001' : 'Invalid sender id',
				'1002' : 'Network not allowed',
				'1003' : 'Invalid mobile number',
				'1004' : 'Low bulk credits',
				'1005' : 'Failed. System error',
				'1006' : 'Invalid credentials',
				'1007' : 'Failed. System error',
				'1008' : 'No Delivery Report',
				'1009' : 'unsupported data type',
				'1010' : 'unsupported request type',
				'4090' : 'Internal Error. Try again after 5 minutes',
				'4091' : 'No Partner ID is Set',
				'4092' : 'No API KEY Provided',
				'4093' : 'Details Not Found'
			}
			responses = response.json()['responses']
			resp_code = responses[0].get(response_code_key)
			resp_text = mp['{0}'.format(resp_code)]

			doc.status = "Sent" if resp_code == 200 else "Pending"
			doc.response_type = resp_code
			doc.response_text = resp_text
			doc.response_message_id = responses[0].get('messageid')
			doc.save()
			return responses[0].get('messageid')
		
		headers = {} # { "Authorization": "Bearer %s" % access_token }
		headers.update({'Content-type': 'application/json'}) #, 'Accept': 'text/plain'})
		body = {
				"partnerID": self.get_parameter("client_id"), # "77",
				"apikey": self.get_parameter("client_secret"), # "5c82636fd8d7b",
				"mobile": recipient, 
				#"message": frappe.safe_decode(message).encode('utf-8'), # "For Python 2",
				"message": frappe.safe_encode(message).decode('utf-8'), # "For both Python 2 and 3",
				"shortcode": self.get_parameter("shortcode"), #"INFOTEXT",
				"pass_type": "plain"
			}	
		if not self.default_settings.send_sms_gateway_url:
			frappe.throw("SMS Gateway URL in Bulk SMS Settings is empty. You must specify it")

		if not outbound_sms_doc:
			doc = self.save_outbound_sms(recipient, message, message_type, reference_doctype, reference_name)
		else:
			doc = outbound_sms_doc
		external_sms_id = None
		if self.do_actual_sms_send:
			response = requests.post(self.default_settings.send_sms_gateway_url, 
					headers=headers, json=body)
			ebiz_logger.log_sms_sent_callback(response.__dict__)
			print (response.text)
			external_sms_id = update_message_response(response)
		return doc.name, external_sms_id

	def _get_sms_delivery_status_celcomafrica(self, message_id):
		"""
		Make request to celcomafrica servers. Careful you do not leave unterminated commas in the json body, otherwise the 
		server will throw an unsupported data type error
		"""

		def update_message_response(response):
			"""
			Response of the format : 
			"{
				"response-code": 200,
				"message-id": 12980847,
				"response-description": "Success",
				"delivery-status": 1,
				"delivery-description": "DeliveredToTerminal",
				"delivery-time": "2019-06-19 15:17:54"
			}
			"""			
			pi = frappe.db.exists("Outbound SMS", {"response_message_id": message_id})		
			if pi:	
				resp = response.json() #frappe._dict(response.text)
				if 'delivery-time' in resp and resp.get('delivery-time'): #if has been delivered					
					dt = datetime.datetime.strptime(resp.get('delivery-time'), '%Y-%m-%d %H:%M:%S')
					delivery_date = dt.date()
					delivery_time = dt.time().strftime("%H:%M:%S")

					#update delivery status
					frappe.db.set_value('Outbound SMS', pi, {
						'is_delivered': 1, #if resp.get('delivery-status') == 1 else 0, 
						'delivery_response_description': resp.get('response-description'), 					
						'delivery_status': resp.get('delivery-status'),
						'delivery_description': resp.get('delivery-description'),
						'delivery_time_string': resp.get('delivery-time'),
						'delivery_date': delivery_date,
						'delivery_time': delivery_time,
						'delivery_tat': resp.get('delivery-tat') if 'delivery-tat' in resp else '00:00:00'
						}, None, update_modified=True)
		
		headers = {} # { "Authorization": "Bearer %s" % access_token }
		headers.update({'Content-type': 'application/json'}) #, 'Accept': 'text/plain'})
		body = {
				"partnerID": self.get_parameter("client_id"), # "77",
				"apikey": self.get_parameter("client_secret"), # "5c82636fd8d7b",
				"messageID": message_id				
			}		
		
		if not self.default_settings.sms_delivery_reports_url:
			frappe.throw("SMS Delivery Reports Url in Bulk SMS Settings is empty. You must specify it")
		
		# response = {"response-code":200,"message-id":12980847,"response-description":"Success","delivery-status":1,"delivery-description":"DeliveredToTerminal","delivery-time":"2019-06-19 15:17:54"}
		response = requests.post(self.default_settings.sms_delivery_reports_url, 
					headers=headers, json=body)		
		ebiz_logger.log_sms_delivery_status_callback(response.text) #response.__dict__)

		print (response.text)
		update_message_response(response)
	
	def _get_credit_balance_celcomafrica(self, settings_id):
		"""
		Make request to celcomafrica servers. Careful you do not leave unterminated commas in the json body, otherwise the 
		server will throw an unsupported data type error.
		Response of the format : 
		{
			"response-code": "200",
			"credit": "25406.00",
			"partner-id": "310"
		}
		"""		
		headers = {} # { "Authorization": "Bearer %s" % access_token }
		headers.update({'Content-type': 'application/json'}) #, 'Accept': 'text/plain'})
		body = {
				"partnerID": self.get_parameter("client_id"), # "77",
				"apikey": self.get_parameter("client_secret"), # "5c82636fd8d7b",
			}		
		settings = self.default_settings
		# settings = frappe.get_doc("Bulk SMS Settings", settings_id)
		if not settings.credit_balance_url:
			frappe.throw("The URL to retrieve credit balance from in Bulk SMS Settings is empty. You must specify it")
		
		# response = {"response-code":200,"message-id":12980847,"response-description":"Success","delivery-status":1,"delivery-description":"DeliveredToTerminal","delivery-time":"2019-06-19 15:17:54"}
		response = requests.post(settings.credit_balance_url, 
					headers=headers, json=body)		
		ebiz_logger.log_sms_credit_balance_callback(response.text)

		print (response.text)
		resp = response.json()
		credit = 0
		if 'response-code' in resp: #if has succeeded
			if cint(resp.get('response-code')) == 200: #success
				credit = resp.get('credit')
		return cint(credit)		
	
	def send_sms(self, recipient, message, message_type, reference_doctype, reference_name, destination=None, outbound_sms_doc=None):	
		provider = self.default_settings.provider
		if provider == "Celcom":
			return self._send_sms_celcomafrica(recipient, message, message_type, reference_doctype, reference_name, outbound_sms_doc)
		if provider == "BongaTech":
			return self._send_sms_bongatech(recipient, message, message_type, reference_doctype, reference_name, outbound_sms_doc)			
		if provider == "Onfon":
			return self._send_sms_onfonmedia(recipient, destination, message, message_type, reference_doctype, reference_name)		

	def get_sms_delivery_reports(self, message_id):
		"""
		Get delivery status for the SMS
		"""
		return self._get_sms_delivery_status_celcomafrica(message_id)
	
	def get_credit_balance(self, settings_id):
		"""
		Get current SMS Units
		"""
		return self._get_credit_balance_celcomafrica(settings_id)

	def save_outbound_sms(self, recipient, message, message_type, reference_doctype, reference_name):
		"""
		Log outbound sms
		"""
		doc = frappe.get_doc({
				'doctype': 'Outbound SMS',
				'posting_date': datetime.datetime.today(),
				'posting_time': datetime.datetime.now(),
				'message': message,
				'recipient': recipient,
				'status': 'Pending',
				'message_type': message_type,
				'reference_doctype': reference_doctype, 
				'reference_name': reference_name
			}).insert(ignore_permissions=True)
		return doc

	def save_inbound_sms(self, sender, message, message_type, message_timestamp, network, shortcode, env="Prod"):
		"""
		Log inbound sms
		"""
		doc = frappe.get_doc({
			'doctype': 'Inbound SMS',
			'posting_date': datetime.datetime.today(),
			'posting_time': datetime.datetime.now(),
			'message': message,
			'phone_number': sender,
			'request_type': message_type,
			'message_timestamp': message_timestamp,
			'network': network,
			'shortcode': shortcode,
			'environment': env,
			'status': 'Pending'			
			}).insert(ignore_permissions=True)
		return doc

	def get_default_settings(self):
		exists = frappe.db.get_value('Bulk SMS Settings', {'is_default': 1})
		if not exists:
			frappe.throw(_("Set the default Bulk SMS Settings to use."))

		self.default_settings = frappe.get_doc('Bulk SMS Settings', exists)

	def get_headers(self):
		headers={'Accept': "text/plain, text/html, */*"}
		for d in self.default_settings.get("parameters"):
			if d.header == 1:
				headers.update({d.parameter: d.value})

		return headers

	def get_parameter(self, param_name):
		"""
		Get the parameter from default_settings.parameters
		"""
		parameters = self.default_settings.get("parameters")
		for p in parameters:
			if p.parameter == param_name:
				return p.value
		return None