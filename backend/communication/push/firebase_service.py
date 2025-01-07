import logging
from typing import Any, Dict
from uuid import uuid4
from django.conf import settings
from django.core.cache import cache

from communication.utils.settings_util import is_push_notification_enabled
import datetime
import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin.messaging import Message, Notification, AndroidConfig, AndroidNotification
from communication.utils.communication_log_util import log_communication, update_communication_error, update_communication_sent

from fcm_django.models import FCMDevice
from django.contrib.auth import get_user_model
User = get_user_model()

class FirebaseAccount:
	# @property
	# def service_account(self):
	# 	return settings.FIREBASE['SERVICE_ACCOUNT'] #"osss-ldms@velvety-being-293814.iam.gserviceaccount.com"			
	
	@property
	def credentials_file(self):
		"""
		Path to JSON file storing credentials. 
		The preferred way is to have an environment variable FIREBASE_APPLICATION_CREDENTIALS which is a path pointing to your JSON-file stored credentials.
		"""
		return settings.FIREBASE['CREDENTIALS_FILE']

# initialization
accnt = FirebaseAccount()
creds = credentials.Certificate(accnt.credentials_file)
firebase_app = firebase_admin.initialize_app(creds)
auth_client = auth.Client(app=firebase_app)
firestore_client = firestore.client(app=firebase_app)

class FirebaseService:
	"""
	Singleton class to handle Firebase services

	See https://awstip.com/using-firebase-to-send-real-time-notifications-in-django-apps-aa5f19869b26
	See https://morioh.com/p/e5c4c50a7979
	See https://fcm-django.readthedocs.io/en/latest/
	See https://www.navin.sh/setting-up-platform-independent-push-notifications-with-django-and-firebase
	See https://github.com/firebase/firebase-admin-python/blob/b9e95e8248eb1473ca5a13bf64e8a33b79dc9db3/snippets/messaging/cloud_messaging.py#L163-L182
	
	NB: Notification messages are delivered to the notification tray when the app is in the background. 
	For apps in the foreground, messages are handled by a callback function. 

	To test:
	- Navigate to `push_frontend_demo` subfolder within this directory
	- Navigate to the sub-directory from the terminal and type

	```bash
	python3 -m http.server 8002
	```
	- Open the frontend site on a browser. A token will be displayed and is already stored on localstorage
	- Using Postman, do a POST call to `/api/login`
	- Using Postman, do a POST call to `/api/test_push`. In case the browser whereon you are running the frontend site
	  is still running and active, Check the browser for display of the message. If the browser is not active, a notification
	  will pop up on the Notification Tray
	"""
	# def __new__(cls, *args, **kwargs):
	# 	if cls.instance is not None:
	# 		return cls.instance
	# 	else:
	# 		inst = cls.instance = super(FirebaseService, cls).__new__(cls, *args, **kwargs)
	# 		cls.initialize()
	# 		return inst

	@staticmethod
	def get_user_custom_token(user: User):
		"""Creating Firebase tokens for a given django user. 
		This token is then sent to the client to be used to authenticate with firebase.
		This ideally should be called when a user logins in

		Args:
			user (User): _description_

		Returns:
			token: Generated Firebase token
		"""

		# this object/dict will be available in the firebase request.auth object. This means you can access this object on the client and even in the firebase security rules
		auth_claims = {
			'uid': user.id,
		}
		token = auth_client.create_custom_token(uid=str(user.id), developer_claims=auth_claims)
		return token.decode()

	@staticmethod
	def register_user_device(user: User, firebase_token: str, type: str):
		"""
		Register a user device. 
		The device id is the same as the firebase_token generated

		Usually this method is called when a sign successfully signs in
		"""
		fcm_device = FCMDevice()
		fcm_device.device_id = firebase_token
		fcm_device.registration_id = firebase_token
		fcm_device.user = user
		fcm_device.save()

	@staticmethod
	def send_notification_to_user(user: User, title: str, body: str, image=None, data={}, results={}, device_id=None): 
		"""
		Send a notification to user's devices

		When we need to send notification to a particular user group, use django filters 
	    like FCMDevice.objects.filter(user__in=[user_ids...]) this will return respective 
		devices for the users in list. Once you have devices list all you have to do is 
		devices.send_message(your message details)
		"""
		def _send_to_one_device():
			"""
			Send notification to single device
			"""
			device = FCMDevice.objects.all().first()
			# device.send_message(notification=Notification(title='title', body='message'))
			return device.send_message(message)

		def _send_to_all_user_devices():
			"""
			Send notification to multiple devices
			"""			
			# devices.send_message(notification=Notification(title='title', body='message'))
			return devices.send_message(message=message)			
			# device.send_message(title="Title", body="Message", data={"test": "test"})

		def _get_devices():
			if device_id:
				devices = FCMDevice.objects.filter(user=user.id, registration_id=device_id)
			else:
				devices = FCMDevice.objects.filter(user=user.id)
			return devices

		if data and isinstance(data, dict):
			# convert data into string keys and string values
			data = { str(key): str(value) for key, value in data.items() }
		if results:
			if isinstance(results, dict):
				results = { str(key): str(value) for key, value in results.items() }
			data['results'] = results
		if body:
			data['body'] = str(body)

		message = Message(					
			#notification=Notification(
			#title=title,
			#body=body,
			#image=None),
			#topic="SampleTopic",
			#android=AndroidConfig(
			# 	ttl=datetime.timedelta(seconds=3600),
			# 	priority='normal',
			# 	notification=AndroidNotification(
			# 		icon='stock_ticker_update',
			# 		color='#f45342'
			# 	),
    		# ),
			data=data
		)	 
		res = None
		if is_push_notification_enabled():
			devices = _get_devices()
			if devices:
				res = _send_to_all_user_devices()
			else:
				res = "The user does not have registered devices"
		else:
			print("Push notifications are disabled")
		import common.utils.log_util as log_util
		log_util.log(u'Notification sent to user {}'.format(user.id)) 
		return message, res
 
	@staticmethod
	def send_notification_to_user_baremetal(user: User, message: Dict[str, Any]):
		"""Send notifications by creating a new document in the firestore in a 
		   specific collection identified as app-notifications/{user_id}/user-notifications.
		   The store structure is specifically chosen as it allows for the creation of security 
		   rules on this collection and only allows the user `user_id` to access the user-notifications collection

		Args:
			user (User): _description_
			message (Dict[str, Any]): _description_
		"""
		msg_id = str(uuid4())		
		notification_ref = firestore_client.collection(u'app-notifications') \
							.document(u'{}'.format(user.id)) \
							.collection("user-notifications") \
							.document(u'{}'.format(msg_id))
		
		notification_ref.set({
			u'message': message,
			'id': msg_id
		})
		import common.utils.log_util as log_util
		log_util.log(logging.INFO, u'Notification sent to user {}'.format(user.id))