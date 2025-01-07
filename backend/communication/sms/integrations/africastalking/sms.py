import africastalking as at
from django.conf import settings
from communication.logging import logger as comms_logger
from communication.utils.exception_util import process_exception
from communication.models import OutboundSMS
from communication.enums import SMSSentStatusEnum
from django.utils import timezone


class SMS:
	def __init__(self, outbound_sms=None):
		"""
		Initialize SMS handler

		Args:
			outbound_sms_id: ID of an OutboundSMS that we want to send, If value is null, we create a new record
		"""
		self.username = settings.AFRICASTALKING_USERNAME
		self.api_key = settings.AFRICASTALKING_API_KEY
		self.sender_id = settings.AFRICASTALKING_SENDER_ID

		# Initialize SDK
		at.initialize(self.username, self.api_key)

		# Initialize SMS service
		self.sms = at.SMS

		self.outbound_sms = outbound_sms

	def send_sms(self, message, message_type, recipients, reference_doctype=None, reference_docname=None, outbound_sms_doc=None):
		"""Send SMS synchronously

		Args:
			message (string): _description_
			message_type (string): _description_
			recipients (list): List of valid phone numbers
			reference_doctype (_type_, optional): The type of document (model) associated with the SMS. Defaults to None.
			reference_docname (_type_, optional): The id of document (model) associated with the SMS. Defaults to None.
			outbound_sms_doc (_type_, optional): The id of OutboundSMS model. Defaults to None.
		
		Sample Response:
		{
			"SMSMessageData": {
				"Message": "Sent to 1/1 Total Cost: KES 0.8000",
				"Recipients": [{
					"statusCode": 101,
					"number": "+254711XXXYYY",
					"status": "Success",
					"cost": "KES 0.8000",
					"messageId": "ATPid_SampleTxnId123"
				}]
			}
		}

		Possible values of statusCode   
		100: Processed
		101: Sent
		102: Queued
		401: RiskHold
		402: InvalidSenderId
		403: InvalidPhoneNumber
		404: UnsupportedNumberType
		405: InsufficientBalance
		406: UserInBlacklist
		407: CouldNotRoute
		500: InternalServerError
		501: GatewayError
		502: RejectedByGateway
		"""
		if not isinstance(recipients, list):
			recipients = [recipients]

		args = {
			'message': message, 
			'recipients': recipients,
			'sender_id': self.sender_id,
		}
		comms_logger.log_sms_sent(args=args)

		if outbound_sms_doc:
			self.outbound_sms = outbound_sms_doc
		else:
			from communication.utils.sms_util import save_outbound_sms
			self.outbound_sms = save_outbound_sms(recipient=recipients,
												  message=message, 
												  message_type=message_type,
												  reference_doctype=reference_doctype, 
												  reference_docname=reference_docname)
		try:			
			response = self.sms.send(message=message, 
									recipients=recipients,
									sender_id=self.sender_id,
									enqueue=False)
			self.on_send_finish(response=response)
		except Exception as e:
			error = process_exception(e)	
			comms_logger.log_sms_error(message=message, 
									error_type="SMS_NOT_SENT_ERROR", 
									error_desc=error,
									args=args)

	# def send_sms_async(self, message, message_type, recipients):
	# 	"""
	# 	Send SMS asynchronously		
	# 	"""
	# 	if not isinstance(recipients, list):
	# 		recipients = [recipients]
		
	# 	self.outbound_sms = self.make_outbound_sms_doc(
	# 				message=message, 
	# 				message_type=message_type, 
	# 				recipients=recipients)
	# 	response = self.sms.send(message=message, 
	# 							 recipients=recipients,
	# 							 sender_id=self.sender_id,
	# 							 enqueue=False, 
	# 							 callback=self.on_send_finish)

	def on_send_finish(self, response):
		"""
		Callback when SMS has been sent

		Sample Response:
		{
			"SMSMessageData": {
				"Message": "Sent to 1/1 Total Cost: KES 0.8000",
				"Recipients": [{
					"statusCode": 101,
					"number": "+254711XXXYYY",
					"status": "Success",
					"cost": "KES 0.8000",
					"messageId": "ATPid_SampleTxnId123"
				}]
			}
		}

		Possible values of statusCode   
		100: Processed
		101: Sent
		102: Queued
		401: RiskHold
		402: InvalidSenderId
		403: InvalidPhoneNumber
		404: UnsupportedNumberType
		405: InsufficientBalance
		406: UserInBlacklist
		407: CouldNotRoute
		500: InternalServerError
		501: GatewayError
		502: RejectedByGateway
		"""
		
		resp = response.json()
		doc = self.outbound_sms
		if 'statusCode' in resp: #if has succeeded
			if resp.get('statusCode') in [100, 101, 102]: #success
				doc.sent_status = SMSSentStatusEnum.SENT.value #SMS was sent

			comms_logger.log_send_sms_callback(response.text)
			doc.response_text = resp.text
			doc.response_code = resp.get('statusCode')
			doc.response_message_id = resp.get('messageId')
			doc.sms_cost = resp.get('cost')
			doc.save()
		# else:
		# 	if error is not None:
		# 		comms_logger.log_sms_error(args={
		# 			'message': message, 
		# 			'recipients': recipients,
		# 			'sender_id': self.sender_id,
		# 		}, 
		# 		error_type="Send SMS Error", 
		# 		error_desc=str(error))	
		# 		doc.response_text = error_desc
		# 		doc.response_code = resp.get('statusCode') 
		# 		doc.save()
		# 		#raise error
		print(response)
