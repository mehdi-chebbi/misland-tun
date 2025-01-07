from django.conf.urls import url, include
from django.contrib import admin
from fcm_django.api.rest_framework import FCMDeviceViewSet, FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from communication import views

router = DefaultRouter()
router.register(r'devices', FCMDeviceViewSet)

urlpatterns = [
    url(r'updatefcmtoken/', views.set_firebase_token, name='update_firebase_token'),
    url(r'^', include(router.urls)),
]
