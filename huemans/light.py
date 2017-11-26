import time

import requests

from huemans.utils import State


class Light(object):

    PROPERTY_ALIASES = {
        'brightness': 'bri',
        'saturation': 'sat',
        'brightness_inc': 'bri_inc'
    }

    MAGIC_ATTRIBUTES = ['on', 'bri', 'hue', 'sat', 'effect', 'xy', 'ct', 'alert', 'colormode', 'bri_inc', 'hue_inc',
                        'sat_inc', 'brightness', 'saturation', 'brightness_inc', 'hue_inc', 'saturation_inc',
                        'transitiontime']

    def __init__(self, bridge, _id, data, autocommit=False):
        self.id = _id
        self.bridge = bridge
        self.autocommit = autocommit
        self._initialize_meta(data)

    def refresh(self):
        r = requests.get('http://{}/api/{}/lights/{}'.format(self.bridge.ip_address,
                                                             self.bridge.username,
                                                             self.id)).json()
        self._initialize_meta(r)

    def strobe(self, n=1, speed=0.1, delay=0):
        autocommit = self.autocommit
        previous_brightness = self.brightness
        self.autocommit = False
        self.on = False
        self.transitiontime = 0
        self.push()
        time.sleep(int(speed * 10 / 2) + delay)
        for i in range(n):
            self.on = True
            self.brightness = 255
            self.transitiontime = 0
            self.push()
            time.sleep(speed / 2)
            self.on = False
            self.transitiontime = 0
            self.push()
            time.sleep(speed / 2 + delay)
        self.on = True
        self.brightness = previous_brightness
        self.autocommit = autocommit
        self.push()

    def push(self):
        if self._state.dirty:
            requests.put('http://{}/api/{}/lights/{}/state'.format(self.bridge.ip_address, self.bridge.username,
                                                                   self.id),
                         json=self._state.dirty)
            self._state.set_clean()

    def _initialize_meta(self, data):
        self._data = data
        self.name = data.get('name', 'No name')
        self.manufacturer = data.get('manufacturername')
        self.model = data.get('modelid')
        self.version = data.get('swversion')
        self.type = data.get('type')
        self.guid = data.get('uniqueid')
        self._set_state(data.get('state'))

    def _set_state(self, state):
        self._state = State(state)
        self._state.set_clean()

    def __repr__(self):
        return 'Light({}: {})'.format(self.id, self.name)

    def __setattr__(self, key, value):
        if key in self.MAGIC_ATTRIBUTES:
            self._state[self.PROPERTY_ALIASES.get(key, key)] = value
            if self.autocommit:
                self.push()
        else:
            super(Light, self).__setattr__(key, value)

    def __getattr__(self, item):
        if item in self.MAGIC_ATTRIBUTES:
            return self._state[self.PROPERTY_ALIASES.get(item, item)]
        else:
            return super(Light, self).__getattr__(item)

    def __dir__(self):
        return super().__dir__() + self.MAGIC_ATTRIBUTES

    def __hash__(self):
        return int(self.id) * 1000 + 1
