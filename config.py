import os
class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ['SECRET_KEY']
    REGISTRY_BASE_URL = os.environ['REGISTRY_BASE_URL']
    REGISTRY_CONSUMER_KEY = os.environ['REGISTRY_CONSUMER_KEY']
    REGISTRY_CONSUMER_SECRET = os.environ['REGISTRY_CONSUMER_SECRET']
    BASE_URL = os.environ['BASE_URL']
    WWW_BASE_URL = os.environ['WWW_BASE_URL']
    REDISCLOUD_URL = os.environ['REDISCLOUD_URL']
    PAYMENT_URL = os.environ['PAYMENT_URL']

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(DevelopmentConfig):
    TESTING = True
