"""oss_ldms URL Configuration

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
from ldms import views
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.documentation import include_docs_urls
from ldms.analysis import analysis_router

urlpatterns = [
    url(r'search/', analysis_router.search_vector, name='search'),
    url(r'lulc/', analysis_router.enqueue_lulc, name='lulc'),
    url(r'soc/', analysis_router.enqueue_soc, name='soc'), 
    url(r'forestchange/', analysis_router.enqueue_forest_change, name='forest_change'), 
    url(r'forestfire/', analysis_router.enqueue_forest_fire, name='forest_fire'),    
    url(r'state/', analysis_router.enqueue_state, name='state'),  
    url(r'trajectory/', analysis_router.enqueue_trajectory, name='trajectory'),
    url(r'performance/', analysis_router.enqueue_performance, name='performance'),   
    url(r'productivity/', analysis_router.enqueue_productivity, name='productivity'),   
    url(r'degradation/', analysis_router.enqueue_land_degradation, name='land_degradation'), 
    url(r'aridity/', analysis_router.enqueue_aridity, name='aridity_index'), 
    url(r'climatequality/', analysis_router.enqueue_climate_quality_index, name='climate_quality_index'),
    url(r'soilquality/', analysis_router.enqueue_soil_quality_index, name='soil_quality_index'),  
    url(r'managementquality/', analysis_router.enqueue_management_quality_index, name='management_quality_index'),  
    url(r'vegetationquality/', analysis_router.enqueue_vegetation_quality_index, name='vegetation_quality_index'),  
    url(r'esai/', analysis_router.enqueue_esai, name='esai'),  
    url(r'carbonemission/', analysis_router.enqueue_forest_carbon_emission, name='carbonemission'), 
    url(r'forestfirerisk/', analysis_router.enqueue_forest_fire_risk, name='forest_fire_risk'),  
    url(r'ilswe/', analysis_router.enqueue_ilswe, name='ilswe'),  
    url(r'rusle/', analysis_router.enqueue_rusle, name='rusle'), 
    url(r'cvi/', analysis_router.enqueue_coastal_vulnerability_index, name='cvi'), 
    url(r'test/', analysis_router.test_render, name='test'),     
    url(r'forest_fire_qml/', analysis_router.forest_fire_qml, name='forest_fire_qml'),      
    url(r'test_tiles/', analysis_router.test_tiles, name='test_tiles'),     
    url(r'test_push/', analysis_router.test_push_notifications, name='test_push_notifications'),     
    url(r'test_precomputation/', analysis_router.test_precomputations, name='test_precomputations'),
    url(r'dummyview', views.MockView.as_view(), name="dummy view")
]

# Allow serving of media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Allow serving of static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('django-rq/', include('django_rq.urls')),
]