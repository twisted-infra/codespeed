from speedcenter.settings import *

import os
from twisted.python.util import sibpath

from . import secret_key

SECRET_KEY = secret_key.SECRET_KEY

TEMPLATE_DIRS = ( sibpath(__file__, 'templates'), ) + TEMPLATE_DIRS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.expanduser("~/data/codespeed.db")

TIME_ZONE = 'America/New_York'
