from django.contrib import admin
from ldms.forms import LDMSSettingsForm
from ldms.models import LDMSSettings

class BaseModelAdmin(admin.ModelAdmin):
	"""
	Base class for model admins
	"""	
	readonly_fields = ('created_on', 'created_by', 'updated_on', 'updated_by')	

class LDMSSettingsAdmin(BaseModelAdmin):
	form = LDMSSettingsForm

	# list_display = ('__all__',)

admin.site.register(LDMSSettings, LDMSSettingsAdmin)
