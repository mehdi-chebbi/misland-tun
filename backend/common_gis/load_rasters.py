from common_gis.models import Raster, DataImportSettings
from common.utils.file_util import get_absolute_media_path
from common_gis.utils.raster_util import duplicate_raster_exists
import json
from pathlib import Path
from django.core.files import File
import os

default_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "rasters.json")
def import_from_json():
	imp_settings = DataImportSettings.load()
	if not imp_settings.raster_data_file:
		# Initialize
		# imp_settings = DataImportSettings()
		path = Path(default_path)
		with path.open(mode='rb') as f:
			imp_settings.raster_data_file = File(f, name=path.name)			
			imp_settings.save()
			
	if imp_settings.raster_data_file:
		path = get_absolute_media_path(imp_settings.raster_data_file.name)
		process_json_file(path)
	else:
		print ("Raster data json file definition cannot be found")

def process_json_file(json_path):
	"""Import rasters from a json file

	Args:
		json_path (string): Absolute file path for the json file. See rasters.json as an example of json format expected
	"""
	data = None
	with open(json_path) as fp:
		data = json.load(fp)

	not_loaded = []
	for i, d in enumerate(data['rasters']):
		print("Processing {0}: {1} of {2}".format(d['name'], i+1, len(data['rasters'])))		
		try:
			obj = Raster(
				name=d['name'],
				resolution=d['resolution'] if 'resolution' in d else data['defaults']['resolution'],
				description=d['name'],
				raster_category=d['raster_category'],
				raster_year=d['raster_year'],
				raster_source=d['raster_source'],
				admin_level=d['admin_level'] if 'admin_level' in d else None,
				admin_zero_id=d['admin_zero_id'] if 'admin_zero_id' in d else None,
				regional_admin_id=d['regional_admin_id'] if 'regional_admin_id' in d else None,
				continent_admin_id=d['continent_admin_id'] if 'continent_admin_id' in d else None
			)
			exists = duplicate_raster_exists(obj)
			if exists:		
				not_loaded.append(d['name'])	
				continue			
			path = Path(d['file_path'])
			with path.open(mode='rb') as f:
				obj.rasterfile = File(f, name=path.name)			
				obj.save()
		except Exception as e:
			print("ERROR: {0}".format(str(e)))
	
	if not_loaded:
		print ("Rasters not loaded: ", not_loaded)