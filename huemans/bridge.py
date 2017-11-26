from collections import MutableMapping

import time
import requests

from huemans.light import Light
from huemans.group import Group
from huemans.sensor import Sensor


class NamedDict(MutableMapping, dict):

    def __init__(self, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs)
        self.aliases = {}

    def __getitem__(self, item):
        if item not in self:
            item = self.aliases[item]
        return dict.__getitem__(self, item)

    def __setitem__(self, key, value):
        self.aliases[int(key)] = key
        self.aliases[value.name] = key
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, x):
        return dict.__contains__(self, x)


class HueBridge(object):

    def __init__(self, ip_address=None, username=None, autocommit=False):
        if not ip_address:
            raise ValueError('You must supply an ip_address')
        self.ip_address = ip_address
        if username is None:
            self._authenticate()
        else:
            self.username = username
        self.autocommit = autocommit
        self.lights = NamedDict()
        self.groups = NamedDict()
        self.sensors = NamedDict()
        self.schedules = NamedDict()
        self._discover_lights()
        self._discover_groups()
        self._discover_sensors()


    def _authenticate(self):
        authenticated = False
        while not authenticated:
            r = requests.post('http://{}/api'.format(self.ip_address), json={'devicetype': 'huemans#home'}).json()
            if 'error' in r[0]:
                print('Please press the LINK button on your bridge')
                time.sleep(5)
            elif 'success' in r[0]:
                self.username = r[0]['success']['username']
                authenticated = True
                print('Successfully authenticated, keep this username: {}'.format(self.username))

    def _discover_lights(self):
        r = requests.get('http://{}/api/{}/lights'.format(self.ip_address, self.username)).json()
        for k, v in r.items():
            self.lights[k] = Light(self, k, v, self.autocommit)

    def _discover_groups(self):
        r = requests.get('http://{}/api/{}/groups'.format(self.ip_address, self.username)).json()
        for k, v in r.items():
            self.groups[k] = Group(self, k, v, self.autocommit)

    def _discover_sensors(self):
        r = requests.get('http://{}/api/{}/sensors'.format(self.ip_address, self.username)).json()
        for k, v in r.items():
            self.sensors[k] = Sensor(self, k, v, self.autocommit)

