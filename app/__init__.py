# coding=utf-8

# ---------------
# ---- IDEAC ----
# ---------------

import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .envvars import db_path

# Set up Flask
app = Flask(__name__)

# Set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# In production mode, add log handler to sys.stderr.
@app.before_first_request
def setup_logging():
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

# Load views
from .views import *
