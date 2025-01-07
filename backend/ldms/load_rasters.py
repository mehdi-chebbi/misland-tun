from common_gis.load_rasters import import_from_json as json_import
import os

default_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "rasters.json")
def import_from_json():
	json_import()