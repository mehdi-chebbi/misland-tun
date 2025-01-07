from ldms.models import LDMSSettings

def get_ldms_settings():
    """
    Load LDMS Settings
    """
    setts = LDMSSettings.load()
    return setts