import os
from flask import Flask, request_finished
from flask_oauthlib.client import OAuth

#app
app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))
oauth = OAuth(app)

if 'SENTRY_DSN' in os.environ:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app, dsn=os.environ['SENTRY_DSN'])

import json

from messenger import Connector
locator = Connector(app)

from fishing import views
