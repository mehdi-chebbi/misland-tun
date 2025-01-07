from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth import get_user_model

class CustomUserManager(BaseUserManager):
	"""Manager for a custom user model"""
	
	def _create_user(self, email, password, **extra_fields):
		"""
		Create and return a user `User` with an email, username and password
		"""
		if not email:
			raise ValueError(_('Users must have an email address'))
			
		extra_fields.pop("is_superuser", None)
		now = timezone.now()
		user = self.model(
			# username=self.normalize_email(email),
			email=self.normalize_email(email),
			# is_staff=is_staff,
			# is_admin=is_admin,
			is_superuser=False, # is_superuser. Superuser should be created only from Django Admin,
			# last_login=now,
			date_joined=now,
			**extra_fields
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password=None, **extra_fields):
		"""
		Create and return a `User` 
		"""
		if password is None:
			raise ValueError (_("Users must have a password"))
		return self._create_user(email, password, **extra_fields)
	
	def create_superuser(self, email, password=None, **extra_fields):
		"""
		Create and return a `User`. 
		"""
		
		if password is None:
			raise ValueError (_("Users must have a password"))
		user = self._create_user(email, password, **extra_fields) 
		user.is_staff=True
		user.is_admin=True
		user.is_superuser=True
		user.save(using=self._db)

class CustomUser(AbstractBaseUser, PermissionsMixin):
	"""Model for Custom User"""
	created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	#created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_creator")
	updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
	#updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_updater")
		
	username = models.CharField(max_length=50, 
				unique=True,
				blank=True)
	email = models.EmailField(
		verbose_name=_('Email address'),
		max_length=255,
		unique=True,
		blank=False
	)
	first_name = models.CharField(max_length=50, unique=False,
					help_text=_("First Name"))
	last_name = models.CharField(max_length=50, unique=False,
					help_text=_("Last Name"))
	is_active = models.BooleanField(_('active'), 
			  help_text=_('Designates whether this user should be treated as '
					'active. Unselect this instead of deleting accounts.'),
			  default=True)
	is_staff = models.BooleanField(_('staff status'),
			  help_text=_('Designates whether the user can log into this admin '
					'site.'), 
			  default=True)
	is_superuser = models.BooleanField(default=False,
					help_text=_("Is a super user"))
	is_admin = models.BooleanField(default=False,
					help_text=_("Has access to the admin panel"))
	date_joined = models.DateTimeField(_('date joined'), default=timezone.now,
					help_text=_("Date user signed up"))
	password2 = models.CharField(max_length=255, blank=True, default="")
	
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	'''Tells DJango that the UserManager class defined above
	should manage objects of this type
	'''
	objects = CustomUserManager()

	def __str__(self):
		return self.email

	class Meta:
		'''
		to set table name in the database
		'''
		# db_table = 'user'
		# app_label = 'users'
		verbose_name = _('user')
		verbose_name_plural = _('users')

	def get_absolute_url(self):
		return "/users/%s/" % urlquote(self.email)

	def get_full_name(self):
		"""
		Returns the first_name plus the last_name, with a space in between.
		"""
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()

	def get_short_name(self):
		"Returns the short name for the user."
		return self.first_name

	def email_user(self, subject, message, from_email=None):
		"""
		Sends an email to this User.
		"""
		send_mail(subject, message, from_email, [self.email])

class UserProfile(models.Model):
	"""
	Profile Model for user
	"""	
	user = models.OneToOneField(get_user_model(), 
			on_delete=models.CASCADE, 
			related_name='profile',
			help_text=_("User"))
	profession = models.CharField(max_length=100,
		help_text=_("Profession"))
	title = models.CharField(max_length=100,
		help_text=_("Designation"))
	institution = models.CharField(max_length=100,
		help_text=_("Institution"))
	can_upload_custom_shapefile = models.BooleanField(default=False,
		help_text=_("Can user upload custom shapefiles"))
	can_upload_standard_raster = models.BooleanField(default=False,
		help_text=_("Can user upload standard rasters"))
	
	class Meta:
		'''
		to set table name in the database
		'''        
		# db_table = 'userprofile'
		pass

class BaseModel(models.Model):
	"""Base model from which all models should inherit from

	Args:
		models (_type_): _description_
	"""
	created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	created_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_creator")
	updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
	updated_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_updater")
	# is_deleted = models.Boolean(default=False)
	# deleted_on = models.DateTimeField(null=True)
	# deleted_by = models.ForeignKey(get_user_model(), null=True)
	
	class Meta:
		abstract = True	

class UserSettings(BaseModel):
	"""Singleton Django Model
	Ensures there's always only one entry in the database, and can fix the
	table (by deleting extra entries) even if added via another mechanism.
	
	Also has a static load() method which always returns the object - from
	the database if possible, or a new empty (default) instance if the
	database is still empty. If your instance has sane defaults (recommended),
	you can use it immediately without worrying if it was saved to the
	database or not.
	
	Useful for things like system-wide user-editable settings.
	"""
	# frontend_port = models.IntegerField(blank=False, null=False, help_text=_("Server port for the front end"))
	enable_user_account_email_activation = models.BooleanField(help_text=_("If checked, users will activate their accounts via email"))
	account_activation_url = models.CharField(max_length=255, blank=False, default="http://0.0.0.0:8080/#/dashboard/activate/", null=False, help_text=_("Url sent to user to activate his account. Uid and token will be appended to the url"))
	change_password_url = models.CharField(max_length=255, blank=False, default="http://0.0.0.0:8080/#/dashboard/forgotpassword/", null=False, help_text=_("Url sent to user to reset his password. Uid and token will be appended to the url"))
	
	class Meta:
		abstract = False # True
		verbose_name_plural = "User Settings"

	def save(self, *args, **kwargs):
		"""
		Save object to the database. Removes all other entries if there
		are any.
		"""
		self.__class__.objects.exclude(id=self.id).delete()
		super(UserSettings, self).save(*args, **kwargs)

	@classmethod
	def load(cls):
		"""
		Load object from the database. Failing that, create a new empty
		(default) instance of the object and return it (without saving it
		to the database).
		"""
		try:
			return cls.objects.get()
		except cls.DoesNotExist:
			return cls()
