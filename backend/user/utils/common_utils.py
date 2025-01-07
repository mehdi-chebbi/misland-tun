from django.conf import settings

def generate_firebase_token(user):
    """
    Generate firebase token
    """
    from communication.utils.settings_util import is_push_notification_enabled
    if is_push_notification_enabled():
        from communication.push.firebase_service import FirebaseService
        return FirebaseService.get_user_custom_token(user)
    return None

def register_loggedin_user_device(user, firebase_token, device_type=None):
    """
    Register device used for login
    """
    from communication.utils.settings_util import is_push_notification_enabled
    if is_push_notification_enabled():
        from communication.push.firebase_service import FirebaseService
        return FirebaseService.register_user_device(user, firebase_token=firebase_token, type=device_type)