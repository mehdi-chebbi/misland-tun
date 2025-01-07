from django.shortcuts import render
from django.contrib.auth.models import Group #, User
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
import json
from common.utils.cache_util import get_cached_results
from rest_framework import permissions as rest_permissions
from django.contrib.auth import get_user_model
from common.models import Gallery, Question, CommonSettings
from common.serializers import (GalleryDetailSerializer, GalleryListSerializer,
            QuestionDetailSerializer, QuestionListSerializer,
            CommonSettingsDetailSerializer)
from rest_framework.response import Response
from rest_framework.decorators import api_view, action  
from rest_framework.response import Response
from django.urls import reverse

User = get_user_model()

class GalleryViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API Endpoint that allows Image galleries to be viewed
	"""
	queryset = Gallery.objects.all()
	serializer_class = GalleryListSerializer
	detail_serializer_class = GalleryDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""
		Return all the published images
		"""		
		queryset = Gallery.objects.all()
		queryset = queryset.filter(is_published=True)		
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data) 

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API Endpoint that allows FAQs to be viewed
	"""
	queryset = Question.objects.all()
	serializer_class =QuestionListSerializer
	detail_serializer_class = QuestionDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	def list(self, request, *args, **kwargs):
		"""
		Return all the published questions
		"""		
		queryset = Question.objects.all()
		queryset = queryset.filter(status=1)		
		if request.user.is_anonymous:
			queryset = queryset.exclude(protected=True)
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data) 

class SystemSettingsViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	API Endpoint that allows System Settings to be viewed
	"""
	queryset = CommonSettings.objects.all()
	serializer_class = CommonSettingsDetailSerializer
	detail_serializer_class = CommonSettingsDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.detail_serializer_class(instance, context=self.get_serializer_context())
		return Response(serializer.data)
		
@api_view(['POST'])
def cache_exists(request):
	results = get_cached_results(request)
	return Response({ "exists": results != None })