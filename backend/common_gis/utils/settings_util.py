from common_gis.models import GISSettings

def get_gis_settings():
    """
    Load System Settings
    """
    setts = GISSettings.load()
    return setts