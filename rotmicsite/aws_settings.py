import os

AWS_QUERYSTRING_AUTH = False

AWS_HEADERS = {  # see http://developer.yahoo.com/performance/rules.html#expires
        'Cache-Control': 'max-age=6000',
    }

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

S3_URL = 'https://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

MEDIA_URL = S3_URL + '/media/'
DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"
