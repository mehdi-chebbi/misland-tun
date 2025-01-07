from django.contrib import admin
from communication.enums import CommunicationChannelTypeEnum
from communication.models import CommunicationSettings, CommunicationLog
from communication.forms import CommunicationSettingsForm

class BaseModelAdmin(admin.ModelAdmin):
	"""
	Base class for model admins
	"""	
	readonly_fields = ('created_on', 'created_by', 'updated_on', 'updated_by')	

class CommunicationLogAdmin(BaseModelAdmin):
	list_display = ("posting_date", "channel_type", "recipient", "message_type", "is_sent", "sent_status")

	def has_change_permission(self, request, obj=None):
		return False

	def has_add_permission(self, request):
		return False

	def has_delete_permission(self, request, obj=None):
		return False
		
	def get_readonly_fields(self, request, obj=None):
		readonly_fields = []
		if obj.channel_type != CommunicationChannelTypeEnum.SMS.value:
			readonly_fields = ['response_text', 'response_code', 'response_message_id', 'is_delivered', 
								'delivery_response_text', 'delivery_status', 'delivery_date',
								'sms_units', 'sms_cost']
		return readonly_fields


class CommunicationSettingsAdmin(BaseModelAdmin):
	form = CommunicationSettingsForm
	list_display = ['email_host', 'email_host_user', 'email_host_protocol', 'email_host_port', 'enable_email', 'enable_push_notifications']

admin.site.register(CommunicationLog, CommunicationLogAdmin)
admin.site.register(CommunicationSettings, CommunicationSettingsAdmin)
