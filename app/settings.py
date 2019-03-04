""" Settings module """
import os
import logging
import pandas as pd


pd.options.display.max_rows = None
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('large_repr', 'truncate')
pd.set_option('precision',2)


"""Logging"""
LOG_CONFIG_PATH = './config/logging.yaml'
LOGLEVEL = logging.INFO
ROLLBAR_LEVEL = logging.ERROR


""" API keys """
# ROLLBAR_KEY = '7b733ed8c8444e67b691f53a74876962'


DATABASE_URI = 'mssql+pymssql://DWENRG-SQL01\\DRIFTWOOD_DB/'


















