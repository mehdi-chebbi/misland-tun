from django.contrib.auth import get_user_model
from communication.push.firebase_service import FirebaseService
from communication.utils.communication_log_util import log_communication, update_communication_error, update_communication_sent
import json
from communication.enums import CommunicationChannelTypeEnum, CommunicationSentStatusEnum
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError
from fcm_django.models import FirebaseResponseDict

User = get_user_model()

def send_push_notification(user: User, subject, message, message_type, reference_doctype, reference_docname, arguments=None, method=None, request=None, task=None, device_id=None):
	"""  Send a notification to user's devices

	When we need to send notification to a particular user group, use django filters 
	like FCMDevice.objects.filter(user__in=[user_ids...]) this will return respective 
	devices for the users in list. Once you have devices list all you have to do is 
	devices.send_message(your message details)

	Args:
		user (User): _description_
		subject (_type_): _description_
		message (_type_): _description_
		recipients (_type_): _description_
		message_type (_type_): _description_
		reference_doctype (_type_): _description_
		reference_docname (_type_): _description_
		arguments (_type_, optional): _description_. Defaults to None.
		method (_type_, optional): _description_. Defaults to None.
		request (_type_, optional): _description_. Defaults to None.
		task (ScheduledTask, optional): _description_. Defaults to None.
		device_id: Device to send notification to. Defaults to None.
	"""
	from common.utils.log_util import log_error
	rec = log_communication(
			recipient=user.email,
			recipient_details= (user.first_name or "") + " " + (user.last_name or ""),
			channel_type=CommunicationChannelTypeEnum.PUSH.value,
			message=message,
			message_type=message_type, 
			reference_doctype=reference_doctype,
			reference_docname=reference_docname,
			arguments=arguments, 
			method=method,
			request=request,
			device_id=device_id
		)	
	try: 
		orig_args = json.loads(task.orig_args or task.args)
		results = task.result or {}
		orig_args['method'] = task.method
		orig_args['status'] = task.status
		orig_args['success'] = 1 if task.succeeded else 0
		notification, resp = FirebaseService.send_notification_to_user(user=user,
				title=subject,
				body=message,
				image=None,
				data=orig_args,
				results=results,
				device_id=device_id)
		rec.message = str(notification.data) # save notification data property as the message
		if isinstance(resp, FirebaseError) or isinstance(resp, ValueError):
			print(str(resp))
			update_communication_error(rec, resp, None)
			log_error(str(resp)) 
		# elif isinstance(resp, messaging.SendResponse):
		elif isinstance(resp, FirebaseResponseDict):
			internal_resp = resp.response
			print(str(resp))
			if resp.response.success_count > 0:
				rec.response_message_id = resp.response.responses[0].message_id
				update_communication_sent(rec)
				return True
			elif resp.response.failure_count > 0: # resp.exception:
				exception = resp.response.responses[0].exception
				print(str(exception))
				update_communication_error(rec, exception, None)
				log_error(str(exception))
		elif isinstance(resp, str):
			print(str(resp))
			update_communication_error(rec, Exception(resp), None)
			log_error(str(resp))		
	except Exception as e:
		print(str(e))
		update_communication_error(rec, e, None)
		log_error(str(e))   
	
	return False