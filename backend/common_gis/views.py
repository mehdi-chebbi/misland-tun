from django.shortcuts import render
from django.contrib.auth.models import Group #, User
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
import os
import json
from common.utils.cache_util import get_cached_results
from rest_framework import permissions as rest_permissions
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, action 
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from common.utils.common_util import cint
from common_gis.models import (ContinentalAdminLevel, RegionalAdminLevel, AdminLevelZero, AdminLevelOne, AdminLevelTwo, 
                    ShapeFile, CustomShapeFile, Raster, RasterType,
                    ScheduledTask, PublishedComputation, ScheduledPreComputation)
# from raster.models import RasterLayer
from common_gis.serializers import (
                    RegionalAdminLevelDetailSerializer, RegionalAdminLevelListSerializer,
                    AdminLevelZeroDetailSerializer, AdminLevelZeroListSerializer,
                    AdminLevelOneDetailSerializer, AdminLevelOneListSerializer,
                    AdminLevelTwoDetailSerializer, AdminLevelTwoListSerializer,
                    ShapeFileSerializer, CustomShapeFileDetailSerializer, CustomShapeFileSerializer,
                    # RasterLayerDetailSerializer, RasterLayerListSerializer,
                    RasterDetailSerializer, RasterListSerializer,
                    RasterTypeDetailSerializer, RasterTypeListSerializer,
                    ScheduledTaskDetailSerializer, ScheduledTaskListSerializer,
					PublishedComputationListSerializer, ContinentalAdminLevelListSerializer,
					ContinentalAdminLevelDetailSerializer, ScheduledPreComputationListSerializer
                )
from common_gis.parsers import ShapeFileParser
from common.utils.file_util import save_file_to_system_storage
from common_gis.utils.vector_util import verify_shapefile, load_shapefile_dynamic, delete_shapefile, read_shapefile
from django.shortcuts import get_object_or_404 
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
from rest_framework.decorators import api_view, action 

User = get_user_model()

# Create your views here.

class RegionalAdminLevelViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	Exposes API endpoints that allows RegionalAdminLevel to be viewed or edited
	In ListView mode, we exclude geo data, but when retrieving,
	we including geo data
	"""
	queryset = RegionalAdminLevel.objects.all()
	serializer_class = RegionalAdminLevelListSerializer
	detail_serializer_class = RegionalAdminLevelDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)


class ContinentalAdminLevelViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	Exposes API endpoints that allows ContinentalAdminLevel to be viewed or edited
	In ListView mode, we exclude geo data, but when retrieving,
	we including geo data
	"""
	queryset = ContinentalAdminLevel.objects.all()
	serializer_class = ContinentalAdminLevelListSerializer
	detail_serializer_class = ContinentalAdminLevelDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)		

class AdminLevelZeroViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	Exposes API endpoints that allows AdminLevelZero to be viewed or edited
	In ListView mode, we exclude geo data, but when retrieving,
	we including geo data
	"""	
	queryset = AdminLevelZero.objects.all()
	serializer_class = AdminLevelZeroListSerializer
	detail_serializer_class = AdminLevelZeroDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""We can either request all admin_level_ones or
		only show the filtered ones
		"""
		include_all = self.request.query_params.get('include', '')
		filter = cint(os.getenv('FILTER_COUNTRIES', 0))
		if include_all == 'all':#if we are to return all, then no need to filter
			filter = None
		if filter == 1:
			countries = os.getenv('PUBLISHED_COUNTRIES', '')
			queryset = AdminLevelZero.objects.filter(name_0__in=countries.split(','))
		else:
			queryset = AdminLevelZero.objects.all()
		
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data)

class AdminLevelOneViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	Exposes API endpoints that allows AdminLevelOne to be viewed or edited
	In ListView mode, we exclude geo data, but when retrieving,
	we including geo data
	"""
	queryset = AdminLevelOne.objects.all()
	serializer_class = AdminLevelOneListSerializer
	detail_serializer_class = AdminLevelOneDetailSerializer

	def retrieve(self, request, *args, **kwargs):	
		"""
		Retrieve an instance of AdminLevelZero	
		"""		
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""We can either request all admin_level_ones or
		we can request admin_level_one items given an admin_level_zero id
		""" 
		queryset = AdminLevelOne.objects.all()
		parent_id = self.request.query_params.get('pid', None)
		if parent_id is not None:
			queryset = queryset.filter(admin_zero_id=parent_id)
		return queryset

class AdminLevelOneViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API Endpoint that allows AdminLevelOne to be viewed or edited
	In ListView mode, we exclude geo data, but when retrieving,
	we including geo data
	"""
	queryset = AdminLevelOne.objects.all()
	serializer_class = AdminLevelOneListSerializer
	detail_serializer_class = AdminLevelOneDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		"""
		Retrieve an instance of AdminLevelOne	
		"""	
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""We can either request all admin_level_ones or
		we can request admin_level_one items given an admin_level_zero id
		"""
		queryset = AdminLevelOne.objects.all()
		parent_id = self.request.query_params.get('pid', None)
		if parent_id is not None:
			queryset = queryset.filter(admin_zero_id=parent_id)
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data)

class AdminLevelTwoViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	Exposes API endpoints that allows AdminLevelOne to be viewed or edited
	In ListView mode, we exclude geo data, but when retrieving,
	we including geo data
	"""
	queryset = AdminLevelTwo.objects.all()
	serializer_class = AdminLevelTwoListSerializer
	detail_serializer_class = AdminLevelTwoDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		"""Retrieve an instance of AdminLevelTwo
		"""
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""We can either request all admin_level_ones or
		we can request admin_level_two items given an admin_level_one id
		Args:
			request ([type]): [description]

		Returns:
			[type]: [description]
		"""
		queryset = AdminLevelTwo.objects.all()
		parent_id = self.request.query_params.get('pid', None)
		if parent_id is not None:
			queryset = queryset.filter(admin_one_id=parent_id)
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data)

class ShapeFileViewSet(viewsets.ModelViewSet):
	"""
	Class to handle uploading of shapefiles
	serializer_class Required for the Browsable API renderer to have a nice form.
	"""
	parser_class = (ShapeFileParser,)
	queryset = ShapeFile.objects.all()
	serializer_class = ShapeFileSerializer
	
	# @action(methods=['POST'], detail=True)
	def create(self, request, *args, **kwargs):
		# for field, value in validated_data.items():
		#     setattr(instance, field, value)
		# return instance

		if 'shapefile' not in request.data:
			raise ParseError("No Shape File uploaded")
		
		"""
		if request.method == 'POST' and request.FILES["image_file"]:
			image_file = request.FILES["image_file"]
			fs = FileSystemStorage()
			filename = fs.save(image_file.name, image_file)
			image_url = fs.url(filename)
			print(image_url)
			return render(request, "upload.html", {
				"image_url": image_url
			})

		"""
		sh_file = request.FILES["shapefile"] if request.FILES else None
		if sh_file:
			# save the file first onto the file system
			file_url = save_file_to_system_storage(sh_file)
			
			# TODO: validate that it is a shapefile
			verify_shapefile(sh_file)
			
			# import the shapefile into the database
			load_shapefile_dynamic(shape_file_path=file_url)

		return Response(status=status.HTTP_201_CREATED)

	def list(self, request):
		"""
		Expose the listing method
		Only show the shapefile meta data since showing 
		features and attributes is quite heavy
		"""
		queryset = ShapeFile.objects.all()
		serializer = ShapeFileSerializer(
			instance=queryset,
			many=True
		)
		return Response(serializer.data)

	def retrieve(self, request, pk=None):
		try:
			shapefile = get_object_or_404(ShapeFile, pk=pk)
		except KeyError:
			return Response(status=status.HTTP_404_NOT_FOUND)
		except ValueError:
			return Response(status=status.HTTP_400_BAD_REQUEST)

		serializer = ShapeFileSerializer(instance=shapefile)
		return Response(serializer.data)
 
	def delete(self, request, format=None):
		# mymodel.my_file_field.delete(save=True)
		delete_shapefile(None)
		return Response(status=status.HTTP_204_NO_CONTENT)

	def update(self, request, pk):
		"""
		We should not assume all fields are available. 
		This helps to deal with partial updates
		"""
		return self.create(request)
		# for field, value in validated_data.items():
		# 	setattr(instance, field, value)
		# return instance

class CustomShapeFileViewSet(viewsets.ModelViewSet):
	"""
	Class to handle uploading of custom shapefiles by users
	serializer_class Required for the Browsable API renderer to have a nice form.
	"""
	# parser_class = (ShapeFileParser,)
	parser_classes = (MultiPartParser,) #(FileUploadParser, MultiPartParser, FormParser, JSONParser)
	queryset = CustomShapeFile.objects.all()
	serializer_class = CustomShapeFileSerializer
	detail_serializer_class = CustomShapeFileDetailSerializer
	permission_classes = [rest_permissions.IsAuthenticated]

	def pre_save(self, obj):
		obj.shapefile = self.request.FILES.get('shapefile')

	# @action(methods=['POST'], detail=True)
	def create(self, request, *args, **kwargs):
		# for field, value in validated_data.items():
		#     setattr(instance, field, value)
		# return instance

		if 'shapefile' not in request.data:
			raise ParseError("No Shape File uploaded")
		
		"""
		if request.method == 'POST' and request.FILES["image_file"]:
			image_file = request.FILES["image_file"]
			fs = FileSystemStorage()
			filename = fs.save(image_file.name, image_file)
			image_url = fs.url(filename)
			print(image_url)
			return render(request, "upload.html", {
				"image_url": image_url
			})

		"""
		"""
		serializer = SnippetSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		"""

		sh_file = request.FILES["shapefile"] if request.FILES else None
		if sh_file:
			if sh_file.content_type != 'application/zip':
				# raise ParseError("You must upload a zip file")
				return Response(data={'message': "You must upload a zip file"}, status=status.HTTP_400_BAD_REQUEST, )

			# save the file first onto the file system
			file_url = save_file_to_system_storage(sh_file)
			
			# TODO: validate that it is a shapefile
			verify_shapefile(sh_file)

			"""			
			# import the shapefile into the database
			#corr(shape_file_path=file_url)
			res = read_shapefile(file_path=file_url.split('/')[-1])
			"""
			data = request.data
			data['owner'] = request.user.id
			data['shapefile'].name = file_url
			serializer = CustomShapeFileDetailSerializer(data=data)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			else:
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		return Response(data={'message': "You must upload a zip file"}, status=status.HTTP_201_CREATED)

	def list(self, request):
		"""
		Expose the listing method
		Only show the shapefile meta data since showing 
		features and attributes is quite heavy
		"""
		queryset = CustomShapeFile.objects.filter(owner_id=request.user.id)
		serializer = CustomShapeFileSerializer(
			instance=queryset,
			many=True
		)
		return Response(serializer.data)

	def retrieve(self, request, pk=None):
		try:
			shapefile = get_object_or_404(CustomShapeFile, pk=pk)
		except KeyError:
			return Response(status=status.HTTP_404_NOT_FOUND)
		except ValueError:
			return Response(status=status.HTTP_400_BAD_REQUEST)

		serializer = CustomShapeFileDetailSerializer(instance=shapefile)
		return Response(serializer.data)
 
	def delete(self, request, format=None):
		# mymodel.my_file_field.delete(save=True)
		delete_shapefile(None)
		return Response(status=status.HTTP_204_NO_CONTENT)

	def update(self, request, pk):
		"""
		We should not assume all fields are available. 
		This helps to deal with partial updates
		"""
		return self.create(request)
		# for field, value in validated_data.items():
		# 	setattr(instance, field, value)
		# return instance

# class RasterLayerViewSet(viewsets.ReadOnlyModelViewSet):
# 	"""
# 	API Endpoint that allows raster layers to be viewed
# 	"""
# 	queryset = RasterLayer.objects.all()
# 	serializer_class = RasterLayerListSerializer
# 	detail_serializer_class = RasterLayerDetailSerializer

# 	def retrieve(self, request, *args, **kwargs):
# 		instance = self.get_object()
# 		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
# 		return Response(serializer.data)
 
class RasterViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API Endpoint that allows raster layers to be viewed
	"""
	queryset = Raster.objects.all()
	serializer_class = RasterListSerializer
	detail_serializer_class = RasterDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""We can either request all rasters or
		we can request rasters given a raster type
		"""
		queryset = Raster.objects.all()
		raster_type = self.request.query_params.get('type', None)
		if raster_type is not None:
			queryset = queryset.filter(raster_type=raster_type)
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data) 

class RasterTypeViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API Endpoint that allows raster types to be viewed
	"""
	queryset = RasterType.objects.all()
	serializer_class = RasterTypeListSerializer
	detail_serializer_class = RasterTypeDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)

class UploadRasterView(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		content = {'message': 'You can do a GET request upload a raster'}
		return Response(content)

	def post(self, request):
		content = {'message': 'You can do a POST request upload a raster'}
		return Response(content)

class ScheduledTaskViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API Endpoint that allows scheduled tasks to be viewed
	"""
	queryset = ScheduledTask.objects.all()
	serializer_class = ScheduledTaskListSerializer
	detail_serializer_class = ScheduledTaskDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""We can either request all tasks or
		we can request tasks given a status
		"""		
		queryset = ScheduledTask.objects.all()
		status = self.request.query_params.get('status', None)		
		if request.user.is_authenticated:
			if status:
				queryset = queryset.filter(owner=request.user.email, status=status)
			else:
				queryset = queryset.filter(owner=request.user.email)
		else:
			if status:
				queryset = queryset.filter(owner=None, status=status)
			else:
				queryset = queryset.filter(owner=None)
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data) 

class PublishedComputationViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API Endpoint that allows Published Computations to be viewed
	"""
	queryset = PublishedComputation.objects.all()
	serializer_class = PublishedComputationListSerializer 

	# def retrieve(self, request, *args, **kwargs):
	# 	instance = self.get_object()
	# 	serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
	# 	return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""
		Return all the published computations
		"""		
		queryset = PublishedComputation.objects.all()
		queryset = queryset.filter(published=1)		
		# if request.user.is_anonymous:
		# 	queryset = queryset.exclude(protected=True)
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data)

class ScheduledPreComputationViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API Endpoint that allows Scheduled PreComputations to be viewed
	"""
	queryset = ScheduledPreComputation.objects.all()
	serializer_class = ScheduledPreComputationListSerializer 

	# def retrieve(self, request, *args, **kwargs):
	# 	instance = self.get_object()
	# 	serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
	# 	return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""
		Return all the Scheduled PreComputations that have completed
		"""		
		queryset = ScheduledPreComputation.objects.all()
		queryset = queryset.filter(succeeded=1)		
		# if request.user.is_anonymous:
		# 	queryset = queryset.exclude(protected=True)
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data)