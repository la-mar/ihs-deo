
import os
import logging
import pandas as pd

# from dotenv import load_dotenv

# load_dotenv()

pd.options.display.max_rows = None
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('large_repr', 'truncate')
pd.set_option('precision',2)

SERVICE_NAME = 'completion-report-ingest'


LOGLEVEL = os.getenv('LOGLEVEL', 20)

ENV = os.getenv('ENV', 'unknown')

SENTRY_KEY = os.getenv('SENTRY_KEY', None)
SENTRY_LEVEL = logging.INFO
SENTRY_EVENT_LEVEL = logging.INFO

DB_DNS_NAME = os.getenv('DB_DNS_NAME', 'localhost')
DB_PORT = os.getenv('DB_PORT', 27017)
DB_NAME = os.getenv('DB_NAME', None)
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DATABASE_URI = f'mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@{DB_DNS_NAME}/{DB_NAME}?retryWrites=true&w=majority'
# f'mongodb://{DB_USERNAME}:{DB_PORT}/?authSource=admin'
S3_BUCKET = os.getenv('S3_BUCKET', None)

# mongodb+srv://driftwood:<password>@test-zwlcj.mongodb.net/test