# coding=utf-8

# ---------------
# ---- IDEAC ----
# ---------------

import logging
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from .envvars import DATABASE_PATH, SECRET_KEY, SERVER_NAME, CERTIFICATE_FILE, PRIVATE_KEY_FILE, IDP_DISPLAY_NAME, IDP_METADATA, IDP_SSO, IDP_SLO, IDP_CERTIFICATE_FILE
from flask_saml2.sp import ServiceProvider
from flask_saml2.utils import certificate_from_file, private_key_from_file

# Set up Flask
app = Flask(__name__)

# Set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SERVER_NAME'] = SERVER_NAME
app.secret_key = SECRET_KEY
db = SQLAlchemy(app)

# In production mode, add log handler to sys.stderr.
@app.before_first_request
def setup_logging():
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)



# Set up SAML service provider
class AppServiceProvider(ServiceProvider):
    def get_logout_return_url(self):
        return url_for('index', _external=True)

    def get_default_login_return_url(self):
        return url_for('index', _external=True)

sp = AppServiceProvider()

app.config['SAML2_SP'] = {
    'certificate': certificate_from_file(CERTIFICATE_FILE),
    'private_key': private_key_from_file(PRIVATE_KEY_FILE),
    'nameid_format': 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
}

app.config['SAML2_IDENTITY_PROVIDERS'] = [
    {
        'CLASS': 'flask_saml2.sp.idphandler.IdPHandler',
        'OPTIONS': {
            'display_name': IDP_DISPLAY_NAME,
            'entity_id': IDP_METADATA,
            'sso_url': IDP_SSO,
            'slo_url': IDP_SLO,
            'certificate': certificate_from_file(IDP_CERTIFICATE_FILE),
        },
    },
]

app.register_blueprint(sp.create_blueprint(), url_prefix='/saml/')



# Load views
from .views import *
