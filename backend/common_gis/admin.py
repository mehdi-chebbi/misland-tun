from django.contrib import admin
from common_gis.models import (ContinentalAdminLevel, AdminLevelZero, AdminLevelOne, AdminLevelTwo,
					Raster, RasterType, RasterValueMapping,
					RegionalAdminLevel, 
                    ComputationThreshold,
					DataImportSettings,
					CustomShapeFile, PublishedComputation, PublishedComputationYear, 
					ScheduledTask, GISSettings, ComputedResult, ComputedResultItem,
					ScheduledPreComputation)
from common_gis.forms import GISSettingsForm
from common.admin import BaseModelAdmin
# Register your models here.

class AdminLevelZeroAdmin(BaseModelAdmin):
	list_display = ['gid_0', 'name_0', 'regional_admin']

class AdminLevelOneAdmin(BaseModelAdmin):
	list_display = ['name_0', 'name_1', 'varname_1', 'admin_zero']
	list_filter = ['admin_zero']

class AdminLevelTwoAdmin(BaseModelAdmin):
	list_display = ['name_0', 'name_1', 'name_2', 'type_2', 'admin_one']
	list_filter = [ 'name_0', 'admin_one']

class RasterAdmin(BaseModelAdmin):
	list_display = ["name", "rasterfile", "raster_category", "raster_year", "raster_source", "admin_level", "admin_zero"]
	#list_filter = ["raster_category", "admin_zero", "raster_source", 'raster_year']
	list_filter = ["admin_level", "raster_category", "admin_zero", "raster_source", 'raster_year', 'regional_admin', 'continent_admin']

	# def change_view(self, request, object_id, extra_context=None):
	# 	self.exclude = ('raster_type', ) #exclude raster type
	# 	return super().change_view(request, object_id, extra_context)

	def get_fields(self, request, obj=None):
		fields = super().get_fields(request, obj)
		# if obj:
		# fields.remove('raster_type')#exclude raster type
		return fields

class ContinentalAdminLevelAdmin(BaseModelAdmin):
	list_display = ["id", "name"]

class RegionalAdminLevelAdmin(BaseModelAdmin):
	list_display = ["id", "name", "continent_admin"]

class ScheduledTaskAdmin(BaseModelAdmin):
	list_display = ['name', 'created_on', 'status', 'succeeded', 'notified_owner']
	list_filter = ['succeeded', 'name']

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

class ComputationThresholdAdmin(BaseModelAdmin):
	list_display = ("datasource", "guest_user_threshold", "authenticated_user_threshold", "enable_guest_user_limit", "enable_signedup_user_limit")

class PublishedComputationYearInline(admin.TabularInline):
	model = PublishedComputationYear
	extra = 1

class PublishedComputationAdmin(BaseModelAdmin):
	fieldsets = [
		(None, {'fields': ['computation_type', 'style', 'admin_zero', 'published']}),
	]
	inlines = [PublishedComputationYearInline]
	list_display = ['computation_type', 'published', 'admin_zero']
	list_filter = ['computation_type']
	search_fields = ['computation_type']

class CustomShapeFileAdmin(BaseModelAdmin):
	list_display = ("shapefile_name", "owner", "shapefile")

class RasterValueMappingInline(admin.TabularInline):
    model = RasterValueMapping
    extra = 1

class RasterTypeAdmin(BaseModelAdmin):
	inlines = [RasterValueMappingInline]

class DataImportSettingsAdmin(BaseModelAdmin):
	list_display = ['raster_data_file']

class GISSettingsAdmin(BaseModelAdmin):
	form = GISSettingsForm

	list_display = ['raster_clipping_algorithm', 'enable_guest_user_limit', 'enable_signedup_user_limit', 'enable_cache', 'enable_tiles']

class ScheduledPreComputationAdmin(BaseModelAdmin):
	list_display = ('computation_type', 'admin_level', 'admin_zero', 'start_year', 'end_year', 'started_on', 'status', 'succeeded')
	readonly_fields = ["created_on", "created_by", "updated_on", "updated_by", "started_on", "status", "args", "method", "error", "succeeded", "completed_on", "change_enum"]
	rdering = ("-started_on",)
 
class ComputedResultItemInline(admin.TabularInline):
	model = ComputedResultItem
	extra = 1
	exclude = ("created_on", "updated_on", "created_by", "updated_by", "custom_string_01", "custom_string_04", "custom_string_05")
	list_display = ('key', 'label', 'count', 'value')
	ordering = ("key",)

class ComputedResultAdmin(BaseModelAdmin):
	# fieldsets = [
	# 	(None, {'fields': ['computation_type', 'style', 'admin_zero', 'published']}),
	# ]
	inlines = [ComputedResultItemInline]
	list_display = ['computation_type', 'admin_zero', 'admin_one', 'raster_file', 'succeeded', 'completed_on']
	list_filter = ['computation_type', 'admin_zero']
	search_fields = ['computation_type']
	ordering = ("-completed_on",)

	def has_change_permission(self, request, obj=None):
		return False

	def has_add_permission(self, request):
		return False

	def has_delete_permission(self, request, obj=None):
		return True # request.user.email.startswith("admin")# False

admin.site.register(AdminLevelZero, AdminLevelZeroAdmin)
admin.site.register(AdminLevelOne, AdminLevelOneAdmin)
admin.site.register(AdminLevelTwo, AdminLevelTwoAdmin)
admin.site.register(Raster, RasterAdmin)
# admin.site.register(RasterType, RasterTypeAdmin)
admin.site.register(ContinentalAdminLevel, ContinentalAdminLevelAdmin)
admin.site.register(RegionalAdminLevel, RegionalAdminLevelAdmin)
admin.site.register(ComputationThreshold, ComputationThresholdAdmin)
admin.site.register(CustomShapeFile, CustomShapeFileAdmin)
admin.site.register(PublishedComputation, PublishedComputationAdmin)
admin.site.register(ScheduledTask, ScheduledTaskAdmin)
admin.site.register(DataImportSettings, DataImportSettingsAdmin)
admin.site.register(GISSettings, GISSettingsAdmin)
admin.site.register(ComputedResult, ComputedResultAdmin)
admin.site.register(ScheduledPreComputation, ScheduledPreComputationAdmin)