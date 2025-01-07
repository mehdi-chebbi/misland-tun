"""oss_rcmrd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path
from common_gis import views
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls
from common.utils import auth_util
from common_gis import router as gis_router

router = DefaultRouter()

router.register(r'tasks', views.ScheduledTaskViewSet)
router.register(r'rasters', views.RasterViewSet)
router.register(r'vectcontinental', views.ContinentalAdminLevelViewSet)
router.register(r'vectregional', views.RegionalAdminLevelViewSet)
router.register(r'vect0', views.AdminLevelZeroViewSet)
router.register(r'vect1', views.AdminLevelOneViewSet)
router.register(r'vect2', views.AdminLevelTwoViewSet)
router.register(r'customvect', views.CustomShapeFileViewSet)
router.register(r'rastertype', views.RasterTypeViewSet)
router.register(r'computationyears', views.PublishedComputationViewSet)
router.register(r'precomputations', views.ScheduledPreComputationViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),    
    url(r'^uploadraster/', views.UploadRasterView.as_view(), name='upload-raster'),
    path('tasks/<int:task_id>/', gis_router.task_result, name='task_result'),  
]