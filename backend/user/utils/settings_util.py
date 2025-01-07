from user.models import UserSettings

def get_user_settings():
    """
    Load System Settings
    """
    setts = UserSettings.load()
    return setts