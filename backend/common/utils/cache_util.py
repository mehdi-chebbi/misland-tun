from django.core.cache import cache
from . import CacheParamError
from django.utils.translation import gettext as _
from .json_sem_hash import get_json_sem_hash 
import copy

def get_cached_results(request):
    """Retrieve computed values from cache

    Args:
        request: HttpRequest object
    """
    payload = copy.copy(request.data)
    key = generate_cache_key(payload, request.path)    
    return get_cache_key(key) # Retrieve value of a cache key

def get_cache_key(key):
    """Retrieve value of a cache key"""
    return cache.get(key)

def set_cache_key(key, value, timeout=None):
    """Set a cache key

    Args:
        key (string): Cache key
        value (value): Value associated with the cache key
        timeout (int, optional): Timeout of the cache key in seconds. Defaults to None.
    """
    #limit = SystemSettings.load().cache_limit or 86400 # 1 day
    limit = timeout or 86400 # 1 day
    cache.set(key, value, limit)

def generate_cache_key(obj, api_path):
    """Generate a hash key based on a dict

    Args:
        obj (object): An object with key value pairs
        api_path (string): API Endpoint. We want to distinguish hash keys for 
                            different API calls since different APIs may consume
                            the same inputs
    """
    props_to_remove = ['cached', 'device_key', 'scheduled_precomputation_id', 'precomputation_context']
    obj = copy.copy(obj)
    if not isinstance(obj, dict):
        raise CacheParamError(_("You must specify a dict"))
    if 'path' not in obj:
        for prop in props_to_remove:
            if prop in obj:
                del obj[prop] #remove cached property and other cosmetic properties
        obj['path'] = api_path
    return get_json_sem_hash(obj)