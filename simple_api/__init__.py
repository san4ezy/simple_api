import urls
from simple_api.api import *
from simple_api import signals, dispatcher
__version__ = '0.1.3'

def connect(**kwargs):
    from django.conf import settings
    from django.utils.importlib import import_module

    for app in settings.INSTALLED_APPS:
        try:
            mod = import_module('%s.api_models' % app)
            dispatcher.register(mod)
        except:
            pass
