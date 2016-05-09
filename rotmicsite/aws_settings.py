import os

AWS_QUERYSTRING_AUTH = False

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

MEDIA_URL = 'http://%s.s3.amazonaws.com/usruploads/' % AWS_STORAGE_BUCKET_NAME
DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

