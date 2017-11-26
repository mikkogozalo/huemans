import time

import requests

from huemans.utils import State


class Sensor(object):

    PROPERTY_ALIASES = {}

    MAGIC_CONFIG = ['on', 'reachable', 'battery', 'alert', 'url', 'long', 'lat', 'configured',
                    'sunriseoffset', 'sunsetoffset', 'tholddark', 'tholdoffset', 'usertest', 'pending', 'ledindication']

    MAGIC_STATE = ['buttonevent', 'lastupdated', 'presence', 'temperature', 'open', 'humidity', 'daylight',
                   'lightlevel', 'dark', 'daylight', 'flag', 'status']

    MAGIC_ATTRIBUTES = MAGIC_CONFIG + MAGIC_STATE

    def __init__(self, bridge, _id, data, autocommit=False):
        self.id = _id
        self.bridge = bridge
        self._initialize_meta(data)
        self.autocommit = autocommit

    def refresh(self):
        r = requests.get('http://{}/api/{}/sensors/{}'.format(self.bridge.ip_address,
                                                              self.bridge.username,
                                                              self.id)).json()
        self._initialize_meta(r)

    def _initialize_meta(self, data):
        self._data = data
        self.name = data.get('name', 'No name')
        self.manufacturer = data.get('manufacturername')
        self.model = data.get('modelid')
        self.version = data.get('swversion')
        self.type = data.get('type')
        self.guid = data.get('uniqueid')
        self._set_state(data.get('state'))
        self._set_config(data.get('config'))

    def _set_state(self, state):
        self._state = State(state)
        self._state.set_clean()

    def _set_config(self, config):
        self._config = State(config)
        self._config.set_clean()

    def __repr__(self):
        return 'Sensor({}: {})'.format(self.id, self.name)

    def __setattr__(self, key, value):
        if key in self.MAGIC_ATTRIBUTES:
            if key in self.MAGIC_CONFIG:
                self._config[self.PROPERTY_ALIASES.get(key, key)] = value
            elif key in self.MAGIC_STATE:
                self._state[self.PROPERTY_ALIASES.get(key, key)] = value
            if self.autocommit:
                self.push()
        else:
            super(Sensor, self).__setattr__(key, value)

    def __getattr__(self, item):
        if item in self.MAGIC_ATTRIBUTES:
            if item in self.MAGIC_CONFIG:
                self.refresh()
                return self._config[self.PROPERTY_ALIASES.get(item, item)]
            elif item in self.MAGIC_STATE:
                self.refresh()
                return self._state[self.PROPERTY_ALIASES.get(item, item)]
        else:
            return super(Sensor, self).__getattr__(item)

    def __dir__(self):
        return super().__dir__() + self.MAGIC_ATTRIBUTES

    def __hash__(self):
        return int(self.id) * 1000 + 3

    def push(self):
        if self._state.dirty:
            requests.put('http://{}/api/{}/sensors/{}/state'.format(self.bridge.ip_address,
                                                                   self.bridge.username, self.id),
                         json=self._state.dirty)
            self._state.set_clean()

        if self._config.dirty:
            requests.put('http://{}/api/{}/sensors/{}/config'.format(self.bridge.ip_address,
                                                                    self.bridge.username, self.id),
                         json=self._config.dirty)
            self._config.set_clean()
