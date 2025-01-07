from django.shortcuts import render
#from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

class MockView(APIView):
	"""
	List all snippets, or create a new snippet.
	"""
	def get(self, request, format=None):
		return Response('Hello, Mock view')

	def post(self, request):
		return Response('Hello, Mock view')
