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
from common.utils import auth_util

urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^api-auth/', include('rest_framework.urls',
								namespace='rest_framework')),

	url(r'^', include('common_gis.urls')),

	# Include the documentation for the API
	url(r'api-docs/', include_docs_urls(title='OSS LDMS API')),
	
	#url(r'^api/test_tiles/', analysis_router.test_tiles, name='test_tiles'), 
	
	# common urls 
	path('api/', include('common.urls')),
 
	# common_gis urls
	path('api/', include('common_gis.urls')),
	
	# Custom user model urls
	path('api/', include('user.urls')),

	# ldms urls
	path('api/', include('ldms.urls')),    

	# communication urls
	path('', include('communication.urls')),    
]

# Allow serving of media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Allow serving of static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
	path('django-rq/', include('django_rq.urls')),
]