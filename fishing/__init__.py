import os
from flask import Flask, request_finished
from flask_oauthlib.client import OAuth

#app
app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))
oauth = OAuth(app)

import json
import redis

from messenger import Connector
locator = Connector(app)

from fishing import views
