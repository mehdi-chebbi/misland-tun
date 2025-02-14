
from rest_framework import serializers
from user.models import UserProfile, CustomUser
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_jwt.settings import api_settings
from django.utils.translation import gettext as _
from django.conf import settings
from user.utils.settings_util import get_user_settings
from user.utils.common_utils import generate_firebase_token, register_loggedin_user_device

class UserProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = UserProfile
		fields = ('institution', 'profession', 'title', 'can_upload_custom_shapefile', 'can_upload_standard_raster')

class UserRegistrationSerializer(serializers.ModelSerializer):

	profile = UserProfileSerializer(required=False)

	class Meta:
		model = CustomUser
		fields = ('email', 'first_name', 'last_name', 'is_active', 'is_admin', 'password', 'password2', 'profile')
		# set password as read_only
		extra_kwargs = {'password': {'write_only': True}, 'password2': {'write_only': True}}
		
	def create(self, validated_data):
		profile_data = validated_data.pop('profile')		
		email = validated_data["email"]		
		# Validate passwords
		password = validated_data["password"]
		password2 = validated_data["password2"]

		# if (email and User.objects.filter(email=email).exclude(username=username).exists()):
		#     raise serializers.ValidationError(
		#         {"email": "Email addresses must be unique."})
		if password != password2:
			raise serializers.ValidationError(
				{"password": _("The two passwords do not match.")})
		
		# validated_data['is_active'] = False if settings.ENABLE_EMAIL_ACTIVATION else True
		validated_data['is_active'] = False if get_user_settings().enable_user_account_email_activation else True
		"""
		When a new user registers, disable is_superuser, is_admin and is_staff
		They have to be explicitly signed by an admin
		in an update process
		"""
		validated_data['is_superuser'] = False
		validated_data['is_admin'] = False
		validated_data['is_staff'] = False

		validated_data.pop('password', None)
		#set username as the email
		user = CustomUser.objects.create_user(username=email, password=password, **validated_data)

		"""
		Set can_upload_custom_shapefile and can_upload_standard_raster 
		to False. They have to be explicitly signed by an admin
		in an update process
		"""
		profile_data["can_upload_custom_shapefile"] = False
		profile_data["can_upload_standard_raster"] = False

		UserProfile.objects.create(
			user=user,
			profession=profile_data['profession'],
			title=profile_data['title'],
			institution=profile_data['institution']
		)
		return user


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class UserLoginSerializer(serializers.Serializer):

	email = serializers.CharField(max_length=255)
	password = serializers.CharField(max_length=128, write_only=True)
	token = serializers.CharField(max_length=255, read_only=True)
	# firebase_token = serializers.CharField(max_length=255, read_only=True)

	def validate(self, data):
		"""
		Custom validate user credentials and returns a token        
		"""
		email = data.get('email', None)
		password = data.get('password', None)
		# Raise an exception if an email is not provided.
		if email is None:
			raise serializers.ValidationError(
				_('An email address is required to log in.')
			)

		# Raise an exception if a password is not provided.
		if password is None:
			raise serializers.ValidationError(
				_('A password is required to log in.')
			)
		"""
		If no user was found matching this email/password combination then
		`authenticate` will return `None`. Raise an exception in this case.
		"""
		user = authenticate(email=email, password=password)
		if user is None:
			raise serializers.ValidationError(
				_('Incorrect Login or Password entered')
			)
		
		"""
		Check if user has been deactivated
		"""
		if not user.is_active:
			raise serializers.ValidationError(
				_('This user has been deactivated.')
			)
		#firebase_token = generate_firebase_token(user)

		try:
			"""
			If user is authenticated, user is passed as a payload to
			JWT_PAYLOAD_HANDLER and the token is generated by encoding
			the payload which is then passed as an argument to JWT_ENCODE_HANDLER
			"""
			payload = JWT_PAYLOAD_HANDLER(user)
			jwt_token = JWT_ENCODE_HANDLER(payload)
			update_last_login(None, user)
			# register_loggedin_user_device(user=user, firebase_token=firebase_token)
		except CustomUser.DoesNotExist:
			raise serializers.ValidationError(
				_('Either the email or password is incorrect')
			)
		return {
			'email': user.email,
			'token': jwt_token #,
			# 'firebase_token': firebase_token
		}

class UserUpdateSerializer(serializers.ModelSerializer):
	"""
	Handles serialization and deserialization of user objects"""
	"""
	Passwords must be at least 8 characters, but no more than 128 
	characters. These values are the default provided by Django. We could
	change them, but that would create extra work while introducing no real
	benefit, so lets just stick with the defaults.

	NB:  It's possible to create a user with this serializer, 
	but we want the creation of a User to be handled by RegistrationSerializer.
	"""
	# password = serializers.CharField(
	# 	max_length=128,
	# 	min_length=8,
	# 	write_only=True
	# )
	profile = UserProfileSerializer(required=False)
	
	class Meta:
		model = CustomUser		
		fields = ('email', 'first_name', 'last_name', 'is_active', 'is_admin', 'is_superuser', 'password', 'password2', 'profile')
		# set password as read_only
		extra_kwargs = {'password': {'write_only': True}, 'password2': {'write_only': True}}

	def update(self, instance, validated_data):
		"""
		Perform updates on a user
		
		Passwords should not be handled with `setattr`, unlike other fields.
		Django provides a function that handles hashing and
		salting passwords. That means
		we need to remove the password field from the
		`validated_data` dictionary before iterating over it.
		"""
		password = validated_data.pop('password', None)
		user_profile = validated_data.pop('profile', {})

		# pop username since we dont want to update initial username and email
		email = validated_data.pop('email', None)
		username = validated_data.pop('username', None)

		for (key, val) in validated_data.items():
			"""
			For the keys remaining in `validated_data`, we will set them on
			the current `User` instance one at a time.
			"""
			setattr(instance, key, val)
		
		if password is not None:
			instance.set_password(password)

		instance.save()

		# save profile 
		profile = instance.profile        
		profile.profession = user_profile['profession']
		profile.title = user_profile['title']
		profile.institution = user_profile['institution']
		profile.can_upload_custom_shapefile = user_profile['can_upload_custom_shapefile']
		profile.can_upload_standard_raster = user_profile['can_upload_standard_raster']
		profile.save()

		return instance

class ChangePasswordSerializer(serializers.Serializer):
	"""
	Serializer for normal password change endpoint
	"""
	model = CustomUser

	old_password = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)
	confirm_password = serializers.CharField(required=True)
	
class UserAccountActivateSerializer(serializers.Serializer):
	"""
	Serializer for user account activation
	"""
	class Meta:
		model = CustomUser
		fields = ('email', )

class RequestResetForgottenPasswordSerializer(serializers.Serializer):
	"""
	Serializer for user account reset password request
	"""
	model = CustomUser

	class Meta:
		fields = ('email', )

class ResetForgottenPasswordSerializer(serializers.Serializer):
	"""
	Serializer for resetting of forgotten user password
	"""
	model = CustomUser

	uid = serializers.CharField(required=True)
	token = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)
	confirm_password = serializers.CharField(required=True)