from django.shortcuts import render
from rest_framework.decorators import api_view

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from django.utils.translation import gettext as _

User = get_user_model()

@api_view(['POST'])
def set_firebase_token(request):
	params = request.data
	token = params.get('token', None)
	email = params.get('email', None)
	#check if user exists
	usr = User.objects.get(email=email)
	if not usr:
		return Response({ "success": 'false', "error": _("User does not exist")})    

	from communication.push.firebase_service import FirebaseService    
	res = FirebaseService.register_user_device(user=usr, firebase_token=str(token), type=None)
	return Response({ "success": 'true', 'message': _("FCM token updated successfully") })