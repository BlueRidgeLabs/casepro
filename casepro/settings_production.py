from __future__ import unicode_literals
import os
import dj_database_url

# import our default settings
from settings_common import *  # noqa

SECRET_KEY = os.environ.get('SECRET_KEY', 'REPLACEME')
if os.environ.get('DEBUG', 'False') == 'True':  # envvars are strings
    DEBUG = True
else:
    DEBUG = False
TEMPLATE_DEBUG = DEBUG
COMPRESS_OFFLINE = True
SEND_EMAILS = True

HOSTNAME = os.environ.get('HOSTNAME', 'localhost:8000')
SITE_HOST_PATTERN = os.environ.get('SITE_HOST_PATTERN', 'http://%s.localhost:8000')

SITE_API_HOST = os.environ.get('SITE_API_HOST', 'http://localhost:8001/')

SENTRY_DSN = os.environ.get('SENTRY_DSN')

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get(
            'DATABASE_URL',
            'postgres://casepro:nyaruka@localhost/casepro')),
}

# SMTP Settings
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')


# junebug configuration
def parse_channel_info(data):
    """
    Expected format: `<channel_id>,<from_addr>,<api_root>;<channel_id>,<from_addr>,<api_root>;`

    Returns a tuple.
    The first item is the assumed default junebug channel which can be used as a
    default fallback for JUNEBUG_DEFAULT_CHANNEL_ID.
    The second item is the dictionary that can be passed to JUNEBUG_CHANNELS

    :returns: tuple
    """
    channels = {}
    default_channel_id = None
    for channel in data.strip().split(';'):
        channel_id, from_addr, api_root = channel.split(',')
        if not default_channel_id:
            default_channel_id = channel_id.strip()
        channels[channel_id.strip()] = {
            'FROM_ADDRESS': from_addr.strip(),
            'API_ROOT': api_root.strip(),
        }
    return default_channel_id, channels


if 'JUNEBUG_CHANNELS' in os.environ:
    inferred_default_channel, channel_info = parse_channel_info(
        os.environ.get('JUNEBUG_CHANNELS'))
    JUNEBUG_DEFAULT_CHANNEL_ID = os.environ.get(
        'JUNEBUG_DEFAULT_CHANNEL_ID', inferred_default_channel)
    JUNEBUG_CHANNELS = channel_info
else:
    # NOTE: allows graceful fallback to previous configuration style, pre reply-affinity
    JUNEBUG_DEFAULT_CHANNEL_ID = os.environ.get('JUNEBUG_CHANNEL_ID', 'replace-me')
    JUNEBUG_CHANNELS = {
        JUNEBUG_DEFAULT_CHANNEL_ID: {
            'FROM_ADDRESS': os.environ.get('JUNEBUG_FROM_ADDRESS', None),
            'API_ROOT': os.environ.get('JUNEBUG_API_ROOT', 'http://localhost:8080/'),
        }
    }

JUNEBUG_INBOUND_URL = r'^junebug/inbound$'
JUNEBUG_HUB_BASE_URL = os.environ.get('JUNEBUG_HUB_BASE_URL', None)
JUNEBUG_HUB_AUTH_TOKEN = os.environ.get('JUNEBUG_HUB_AUTH_TOKEN', None)

SITE_BACKEND = 'casepro.backend.junebug.JunebugBackend'

# identity store configuration
IDENTITY_API_ROOT = os.environ.get('IDENTITY_API_ROOT',
                                   'http://localhost:8081/')
IDENTITY_AUTH_TOKEN = os.environ.get('IDENTITY_AUTH_TOKEN',
                                     'replace-with-auth-token')
IDENTITY_ADDRESS_TYPE = os.environ.get('IDENTITY_ADDRESS_TYPE',
                                       'msisdn')
IDENTITY_LANGUAGE_FIELD = os.environ.get('IDENTITY_LANGUAGE_FIELD',
                                         'language')

SITE_MAX_MESSAGE_CHARS = 640  # the max value for this is 800

# Time until a case is re-assigned (specified in minutes)
case_response_required_time_str = os.environ.get(
    'SITE_CASE_RESPONSE_REQUIRED_TIME')

if case_response_required_time_str:
    SITE_CASE_RESPONSE_REQUIRED_TIME = int(case_response_required_time_str)

SITE_HIDE_CONTACT_FIELDS = ["name"]
SITE_CONTACT_DISPLAY = os.environ.get('SITE_CONTACT_DISPLAY',
                                      'name')
SITE_MAX_MESSAGE_CHARS = 640  # the max value for this is 800

REDIS_HOST = os.environ.get('REDIS_URL', 'localhost:6379')
# REDIS_URL contains the scheme
BROKER_URL = '%s/%d' % (REDIS_HOST, 10 if TESTING else 15)  # noqa TESTING defined in settings_common (flake8)
CELERY_RESULT_BACKEND = BROKER_URL
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '%s:15' % REDIS_HOST,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

if os.environ.get('USE_DEFAULT_CACHE', 'False') == 'True':
    # Use Django's default cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# settings_common currently defines Nyaruka contact details. We use sentry.
ADMINS = []


ALLOWED_HOSTS = ['*']

INSTALLED_APPS += (  # noqa INSTALLED_APPS defined in settings_common (flake8)
    'casepropods.family_connect_registration.plugin.RegistrationPlugin',
    'casepropods.family_connect_subscription.plugin.SubscriptionPlugin',
)

if SENTRY_DSN:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
    }

# Pods
PODS = [{
    'label': "family_connect_registration_pod",
    'title': "Registration Information",
    'hub_api_url': os.environ.get('REGISTRATION_URL', ''),
    'hub_token': os.environ.get('REGISTRATION_AUTH_TOKEN',
                                'replace-with-auth-token'),
    'identity_store_api_url': '{0}api/v1/'.format(
        os.environ.get(
            'IDENTITY_API_ROOT',
            'https://identity-store/',
        )
    ),
    'identity_store_token': os.environ.get(
        'IDENTITY_AUTH_TOKEN',
        'identity-store-token',
    ),
    'contact_id_fieldname': os.environ.get('REGISTRATION_CONTACT_ID_FIELDNAME',
                                           'mother_id'),
    'field_mapping': [
        {"field": "last_period_date", "field_name": "Date of last period"},
        {"field": "language", "field_name": "Language Preference"},
        {"field": "mama_id_type", "field_name": "ID Type"},
        {"field": "mama_id_no", "field_name": "ID Number"},
        {"field": "msg_receiver", "field_name": "Message Receiver"},
        {"field": "receiver_id", "field_name": "Receiver ID"},
        {"field": "hoh_id", "field_name": "Head of Household ID"},
        {"field": "operator_id", "field_name": "Operator ID"},
        {"field": "msg_type", "field_name": "Receives Messages As"},
    ]
}, {
    'label': "family_connect_subscription_pod",
    'title': "Subscription Information",
    'url': os.environ.get('SUBSCRIPTION_URL', ''),
    'token': os.environ.get('SUBSCRIPTION_AUTH_TOKEN',
                            'replace-with-auth-token'),
}]
