from rest_framework import serializers
from django.contrib.auth.models import User, Group 
from common.models import (Gallery, Question)
from common.models import CommonSettings
from rest_framework_gis.serializers import GeoModelSerializer, GeoFeatureModelSerializer
from django.contrib.gis.gdal.field import OGRFieldTypes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404  

import numpy as np
from django.conf import settings
from common.utils.file_util import read_image_tiff, get_media_dir
import json

class CommonSettingsDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for CommonSettings object
    """    
    email_host_password = serializers.SerializerMethodField()
    class Meta:
        model = CommonSettings
        fields = "__all__"

    def get_email_host_password(self, obj):
        """
        Method must be prefixed with get_        
        """
        return obj.email_host_password # ""

class GalleryListSerializer(serializers.ModelSerializer):
    """
    Serializer for Gallery listing
    """
    class Meta:
        model = Gallery
        fields = ("image_name", "image_file", "is_published", "is_document", "image_desc")

class GalleryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Gallery object
    """        
    class Meta:
        model = Gallery
        fields = ("image_name", "image_file", "is_published", "is_document", "image_desc")


class QuestionListSerializer(serializers.ModelSerializer):
    """
    Serializer for Question listing
    """
    topic = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = ("question_text", "answer", "topic")

    def get_topic(self, obj):
        return obj.topic.topic_name if obj.topic else ""

class QuestionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Question object
    """     
    topic = serializers.SerializerMethodField()   
    class Meta:
        model = Question
        fields = ("question_text", "answer", "topic")

    def get_topic(self, obj):
        return obj.topic.topic_name if obj.topic else ""