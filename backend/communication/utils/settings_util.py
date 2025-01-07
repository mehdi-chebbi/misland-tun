from communication.models import CommunicationSettings

def get_communication_settings():
    """
    Load System Settings
    """
    setts = CommunicationSettings.load()
    return setts

def is_push_notification_enabled():
    setts = get_communication_settings()
    return setts.enable_push_notifications

def is_email_enabled():
    setts = get_communication_settings()
    return setts.enable_email