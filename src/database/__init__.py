import os

import database.models

environment = os.getenv("ENVIRONMENT", "developing")

# TODO: implement switching db to sqlite/postgresql depends on environment state (developing/testing)
from database.session_postgresql import (
    get_postgresql_db as get_db,
    get_postgresql_db_contextmanager as get_db_contextmanager,
    postgresql_engine as engine
)