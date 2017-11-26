from collections import MutableMapping


class State(MutableMapping, dict):

    _dirty_keys = []

    def __getitem__(self, item):
        return dict.__getitem__(self, item)

    def __setitem__(self, key, value):
        self._dirty_keys.append(key)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, x):
        return dict.__contains__(self, x)

    def set_clean(self):
        self._dirty_keys = []

    @property
    def dirty(self):
        return {k: self[k] for k in self._dirty_keys}