import os
from flask import Flask
from flask_oauthlib.client import OAuth
import redis

#app
app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))
oauth = OAuth(app)

redis_client = redis.from_url(app.config['REDISCLOUD_URL'])

from fishing import views
