import os
from django.contrib.gis import geos
import numpy as np
from pathlib import Path
from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.contrib.gis.gdal import GDALRaster
from django.conf import settings 
import datetime
from django.utils.translation import gettext as _
from common import AnalysisParamError 
from common.utils.settings_util import get_backend_port
import requests
import tempfile
import shutil
import zipfile
import time
import sys

def save_file_to_system_storage(file_obj):
	fs = FileSystemStorage()
	filename = fs.save(file_obj.name, file_obj)
	file_url = fs.url(filename)
	return file_url

def read_image_tiff(file_path, unique=False):
	"""Read an image and return the values as an array

	Args:
		file_path ([type]): [Absolute Path of the image file]
		unique (bool, optional): Determines if we return the distinct pixel values. Defaults to False.
	"""    
	file = Path(file_path)
	file_exists(file_path, raise_exception=True)
	rst = GDALRaster(file_path, write=False)
	img_array = rst.bands[0].data()
	#extract pixel values as arrays for all the bands
	for i, band in enumerate(rst.bands):
		if i > 0:
			np.append(img_array, band.data())
			
	if unique:
		# flatten the array then get unique  values
		return np.unique(img_array.flatten())
	return img_array
	
def file_exists(file_path, raise_exception=True):
	"""
	Check if the `file_path` refers to a valid file path

	Args:
		file_path (string): Location of a file
	"""
	file = Path(file_path)
	res = file.is_file()
	if raise_exception and not res:
		raise FileNotFoundError("%s does not exist" % file_path)
	return res

def get_temp_file(suffix=".tif", prefix=None, delete=False):
	"""Generate a temp file"""
	return tempfile.NamedTemporaryFile(delete=delete, suffix=suffix, prefix=prefix).name

def get_absolute_media_path(file_path=None, is_random_file=False, random_file_prefix=None, 
		random_file_ext=None, sub_dir=None, use_static_dir=False):
	"""Get absolute file location given a relative file path
	   Also generates random file names and returns the absolute path
	Args:
		file_path (string): Relative file path
		is_random_file (bool): If True, a random file will be generated
		random_file_prefix (string): Prefix to pre-prepend the random file with
		random_file_ext (string): Extension of the random file to be generated
		sub_dir (string): Sub-directory within the parent directory

	Returns:
		string: A valid file location on file system
	"""
	# Validate
	if not file_path and not is_random_file:
		raise AnalysisParamError(_("Specify either a file_path or set is_random_file=True"))
	elif file_path and is_random_file:
		raise AnalysisParamError(_("File path cannot be specified when is_random_file=True"))
	
	if is_random_file:
		file_path = generate_file_name(prefix=random_file_prefix, extension=random_file_ext)
		path = get_media_dir(sub_dir, use_static_dir=use_static_dir) + file_path
	else: # validate that it is a valid path
		if file_exists(file_path, raise_exception=False):
			path = file_path
		else:
			path = get_media_dir(sub_dir, use_static_dir=use_static_dir) + file_path
	return path.replace("//", "/")

def get_media_dir(subdir=None, use_static_dir=False):
	"""
	Return the directory path where media are stored

	Args:
		subdir (string): Sub-directory to append to directory
	"""
	root = settings.STATIC_ROOT if use_static_dir else settings.MEDIA_ROOT	
	path = root.rstrip("/") + "/"
	if subdir:
		path = "%s/%s/" % (root.rstrip("/"), subdir.rstrip("/"))
		path = path.replace("//", "/")
	return path

def get_download_url(request, file, backend_port=None, use_static_dir=False):
	"""
	Returns download url for file 
	"""
	backend_port = get_backend_port(backend_port=backend_port)
	root = settings.STATIC_URL if use_static_dir else settings.MEDIA_URL
	url = get_server_url(request, backend_port)
	if request:
		return "%s/%s/%s" % (url.rstrip("/"), root.strip("/"), file)
	else:
		return get_absolute_media_path(file, use_static_dir)

def generate_file_name(prefix=None, extension=None):
	"""Generate a file name based on timestamp"""
	return "%s%s%s" % ("" if not prefix else prefix, 
					 datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"),
					 "{}".format(extension) if extension else "")

def get_server_url(request, backend_port=None):
	"""
	Returns url for site 
	"""
	backend_port = get_backend_port(backend_port=backend_port)
	use_system_settings_port = True
	if use_system_settings_port:
		port = backend_port or settings.BACKEND_PORT or 80 
		url = "%s://%s:%s/" % (request.scheme, request.get_host().split(':')[0], port)
	else:
		url = "%s://%s/" % (request.scheme, request.get_host())
	return url
	# return "%s://%s/" % (request.scheme, request.get_host())

def get_physical_file_path_from_url(request, url, backend_port=None, use_static_dir=False):
	"""
	Returns the physical path of file given a url
	Args:
		request (Request): HttpRequest
		url (string): Url from where to extract the physical file path
	"""
	backend_port = get_backend_port(backend_port=backend_port)
	root = settings.STATIC_URL if use_static_dir else settings.MEDIA_URL
	file = url.replace(get_server_url(request, backend_port), "/").replace(settings.MEDIA_URL, "")
	return get_absolute_media_path(file_path=file)

def download_file(url, dest_file):
	"""Download a file
	Args:
		url (string): Url to download
		dest_file (string): Destination of the downloaded file
	Returns:
		String: Path to the downloaded file
	"""
	file_url = url # 'https://www.journaldev.com/wp-content/uploads/2019/08/Python-Tutorial.png'	
	file_stream = requests.get(file_url, stream=True)	
	with open(dest_file, 'wb') as local_file:
		for data in file_stream:
			local_file.write(data)
	return dest_file

def unzip_file(file_path, use_temp_dir=True, dest_dir=None, return_full_path=True):
	"""Unzip a file into a temp folder or a custom folder

	Args:
		file_path (string): Path to zip file
		use_temp_dir (bool, optional): Extract the file to a temp folder. Defaults to True.
		dest_dir (string, optional): Custom folder to extract zip file to. Defaults to None.

	Raises:
		AnalysisParamError: [description]

	Returns:
		list: List of extracted files
	"""
	if not use_temp_dir and not dest_dir:
		raise AnalysisParamError("You must specify the `dest_dir` if `use_temp_dir` is set as False")
	fp = get_absolute_media_path(file_path)
	if dest_dir == ".":
		dest_dir = os.path.dirname(file_path) + "/"
	tmpdir = tempfile.mkdtemp() if use_temp_dir else dest_dir

	zf = zipfile.ZipFile(fp)
	zf.extractall(tmpdir)
	files = []
	for fl in os.listdir(tmpdir):
		files.append(os.path.join(tmpdir, fl) if return_full_path else fl)
	return files

def copy_file(src, dest):
	"""Copy source file to destination

	Args:
		src (string): Path to source file
		dest (string): Path to destination file
	"""
	shutil.copy(src, dest)
	return dest

def download_and_unzip_file(url, dest_file):
	"""
	Download file from the returned url
	"""
	#dest_file = self.generate_file_name()
	fl = download_file(url, dest_file)
	return unzip_file(file_path=fl, 
			use_temp_dir=True, 
			dest_dir=".", 
			return_full_path=True
		)[0]
		
# def image_upload(request):
#     if request.method == 'POST' and request.FILES["image_file"]:
#         image_file = request.FILES["image_file"]
#         fs = FileSystemStorage()
#         filename = fs.save(image_file.name, image_file)
#         image_url = fs.url(filename)
#         print(image_url)
#         return render(request, "upload.html", {
#             "image_url": image_url
#         })
#     return render(request, "upload.html")

def delete_temp_files(extension=None, age_in_seconds=0):
	"""Delete temp files

	Args:
		extension: File extension. Defaults to None.
		age_in_seconds (int, optional): Time since the file was created. For a day specify 86400. Defaults to 0.
	"""
	print("*************************************temporary directory********************************************",file=sys.stderr)
	print(tempfile.gettempdir(),file=sys.stderr)
	print("*************************************temporary directory********************************************",file=sys.stderr)
	delete_files(tempfile.gettempdir(), extension=extension, age_in_seconds=age_in_seconds)

def delete_files(directory, extension=None, age_in_seconds=0):
	"""Delete files from a directory

	Args:
		directory: Directory containing the files
		extension: File extension. Defaults to None.
		age_in_seconds (int, optional): Time since the file was created. For a day specify 86400. Defaults to 0.
	"""
	now = time.time()
	for filename in os.listdir(directory):
		fname, fextn = os.path.splitext(filename)
		if extension and fextn != extension:
			continue
		# timestamp when the file contents were last modified
		file_full_path = os.path.join(directory, filename)
		if age_in_seconds:
			timestamp = os.stat(file_full_path).st_mtime
			reference_time = now - age_in_seconds
			if timestamp < reference_time: 
				os.remove(file_full_path)
		else: 
			os.remove(file_full_path)
