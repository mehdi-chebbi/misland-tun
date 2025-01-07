from common.models import CommonSettings

def get_common_settings():
    """
    Load System Settings
    """
    setts = CommonSettings.load()
    return setts

def get_backend_port(backend_port):
    return backend_port or get_common_settings().backend_port