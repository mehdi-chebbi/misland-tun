from django.contrib import admin
from common.models import (CommonSettings, Gallery, Topic, Question, MonitoringLog, MonitoringLogItem)
from common.forms import CommonSettingsForm
from common.enums import CommunicationChannelTypeEnum

class BaseModelAdmin(admin.ModelAdmin):
	"""
	Base class for model admins
	"""	
	readonly_fields = ('created_on', 'created_by', 'updated_on', 'updated_by')	

class CommonSettingsAdmin(BaseModelAdmin):
	form = CommonSettingsForm
	list_display = ['backend_url', 'backend_port', 'override_backend_port', 'enable_execution_monitoring']

class GalleryAdmin(BaseModelAdmin):
	list_display = ['image_name', 'image_file', 'is_published', 'is_document']

class TopicAdmin(BaseModelAdmin):
	list_display = ("topic_name", "slug", "sort_order")

class QuestionAdmin(BaseModelAdmin):
	list_display = ("question_text", "topic", "answer", "status", "protected", "sort_order")

class MonitoringLogItemInline(admin.TabularInline):
	model = MonitoringLogItem
	extra = 0
	list_display = ("time_entry", "cpu", "memory", "disk") 
	ordering = ("time_entry",)

class MonitoringLogAdmin(BaseModelAdmin):
	inlines = [MonitoringLogItemInline]
	exclude = ("created_on", "updated_on", "created_by", "updated_by")
	list_display = ("execution_name", "caller_type", 'is_critical_memory_usage', 'is_critical_cpu_usage', 'is_critical_disk_usage', 'is_critical_temp')
	list_filter = ['is_completed', 'is_critical_memory_usage', 'is_critical_cpu_usage', 'is_critical_disk_usage', 'is_critical_temp']

	def has_change_permission(self, request, obj=None):
		return False

	def has_add_permission(self, request):
		return False

	def has_delete_permission(self, request, obj=None):
		return False

	def get_readonly_fields(self, request, obj=None):
        # make all fields readonly
		readonly_fields = list(
			set([field.name for field in self.opts.local_fields] +
				[field.name for field in self.opts.local_many_to_many])
				)					
		return readonly_fields

# class CommunicationLogAdmin(BaseModelAdmin):
# 	list_display = ("posting_date", "channel_type", "recipient", "message_type", "is_sent", "sent_status")

# 	def has_change_permission(self, request, obj=None):
# 		return False

# 	def has_add_permission(self, request):
# 		return False

# 	def has_delete_permission(self, request, obj=None):
# 		return False
		
# 	def get_readonly_fields(self, request, obj=None):
# 		readonly_fields = []
# 		if obj.channel_type != CommunicationChannelTypeEnum.SMS.value:
# 			readonly_fields = ['response_text', 'response_code', 'response_message_id', 'is_delivered', 
# 								'delivery_response_text', 'delivery_status', 'delivery_date',
# 								'sms_units', 'sms_cost']
# 		return readonly_fields

admin.site.register(CommonSettings, CommonSettingsAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(MonitoringLog, MonitoringLogAdmin)
