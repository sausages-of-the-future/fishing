import json
from dateutil.relativedelta import relativedelta
from datetime import datetime

class Order():

    _date_of_birth = None
    _existing_licences = []
    _disabled = False
    _base_url = None
    licence_type = None
    starts_at = None
    duration = None

    def __init__(self, date_of_birth, existing_licences, disabled, base_url):

        #set user details
        self._date_of_birth = date_of_birth
        self._existing_licences = existing_licences
        self._disabled = disabled
        self._base_url = base_url

    def to_dict(self):
        result = {}
        result['_existing_licences'] = self._existing_licences
        result['_date_of_birth'] = self._date_of_birth
        result['_disabled'] = self._disabled
        result['_base_url'] = self._base_url
        result['licence_type'] = self.licence_type
        result['duration'] = self.duration
        result['starts_at'] = self.starts_at
        return result

    @classmethod
    def from_dict(cls, data):
        order = Order(data['_date_of_birth'], data['_existing_licences'], data['_disabled'], data['_base_url'])
        order.licence_type = data['licence_type']
        order.duration = data['duration']
        order.starts_at = data['starts_at']
        return order

    @property
    def live_licence_count(self):
        return 1
        # return len(self._existing_licences)

    @property
    def concession_type(self):
        age = relativedelta(datetime.now(), self._date_of_birth)
        if age.years >= 12 and age.years <= 16:
            return 'junior'
        elif age.years >= 65:
            return 'senior'
        elif self._disabled:
            return 'disabled'
        else:
            return 'adult'

    def licence_name(self):
        prices = json.loads(open('prices.json').read())
        return prices[self.licence_type]['name']

    def licence_type_uri(self):
        prices = json.loads(open('prices.json').read())
        return prices[self.licence_type]['uri'].replace('%s', self._base_url)

    def calculate_total(self):
        prices = json.loads(open('prices.json').read())
        return prices[self.licence_type]['prices'][self.duration]['concessions'][self.concession_type]




