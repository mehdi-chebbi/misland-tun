import json
import os
from pathlib import Path
from common.utils.file_util import get_absolute_media_path
from common.utils.common_util import get_client_ip_address, get_client_ip_with_port
from django.conf import settings

#default_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "return_url_map.json")		
default_path = settings.RETURN_URL_MAP_PATH # os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir, 'return_url_map.json'))

def get_mapped_url(url_key, request=None, origin=None):
	"""Get the url to be used given the origin

	Args:
		url_key: The unique key for the url block in the json file
		request: Request object
		origin: Origin of the request		
	"""
	if not origin and not request:
		raise Exception("The origin or the Request must be specified")
	url = ''
	if not origin:
		origin = get_client_ip_with_port(request) # get_client_ip_address(request)
	
	print ("Origin: ", origin, "Url Key: ", url_key)
	# have localhost representing 0.0.0.0 and 127.0.0.1
	origin = origin.replace("0.0.0.0", "localhost").replace("127.0.0.1", "localhost")
	data = load_urls_map()
	if data:
		if "urls" in data:
			urls = data.get("urls")
			if url_key in urls:
				url_block = urls.get(url_key)
				url = url_block.get(origin)
				if url == None: #if url not found, return default
					if os.getenv("ENV_TYPE") == "PROD":
						url = url_block.get("default_prod")
					elif os.getenv("ENV_TYPE") == "UAT":
						url = url_block.get("default_uat")
					else:
						url = url_block.get("default")
	print ("Mapped url: ", url)
	return url

def load_urls_map():
	"""
	Parse json file containing the URL mapping for different task/requests
	json_path (string): Absolute file path for the json file. See rasters.json as an example of json format expected
	"""
	path = get_absolute_media_path(default_path)
	data = None
	with open(path) as fp:
		data = json.load(fp)
	return data

def process_json_file(json_path):
	"""Import rasters from a json file

	Args:
		json_path (string): Absolute file path for the json file. See rasters.json as an example of json format expected
	"""
	data = None
	with open(json_path) as fp:
		data = json.load(fp)

	return data
	# not_loaded = []
	# for i, d in enumerate(data['urls']):
	# 	print("Processing {0}: {1} of {2}".format(d['name'], i+1, len(data['rasters'])))		
	# 	try:
	# 		obj = Raster.objects.create(
	# 			name=d['name'],
	# 			resolution=d['resolution'] if 'resolution' in d else data['defaults']['resolution'],
	# 			description=d['name'],
	# 			raster_category=d['raster_category'],
	# 			raster_year=d['raster_year'],
	# 			raster_source=d['raster_source'],
	# 			admin_level=d['admin_level'] if 'admin_level' in d else None,
	# 			admin_zero_id=d['admin_zero_id'] if 'admin_zero_id' in d else None,
	# 			regional_admin_id=d['regional_admin_id'] if 'regional_admin_id' in d else None,
	# 			continent_admin_id=d['continent_admin_id'] if 'continent_admin_id' in d else None
	# 		)
	# 		exists = duplicate_raster_exists(obj)
	# 		if exists:		
	# 			not_loaded.append(d['name'])	
	# 			continue			
	# 		path = Path(d['file_path'])
	# 		with path.open(mode='rb') as f:
	# 			obj.rasterfile = File(f, name=path.name)			
	# 			obj.save()
	# 	except Exception as e:
	# 		print("ERROR: {0}".format(str(e)))