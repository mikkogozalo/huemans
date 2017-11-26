class Condition(object):
    def json(self):
        raise NotImplementedError('json is not implemented')

    def __repr__(self):
        return 'Condition({})'.format(self)


class LightCondition(Condition):

    def __str__(self):
        return '{} is turned {}'.format(self.light, 'on' if self.eq else 'off')

    def json(self):
        return {
            'address': '/lights/{}/state/on'.format(self.light.id),
            'operator': 'eq',
            'value': self.eq
        }


class IsLightTurnedOn(LightCondition):
    eq = True

    def __init__(self, light):
        self.light = light


class IsLightTurnedOff(LightCondition):
    eq = False

    def __init__(self, light):
        self.light = light


class TemperatureIs(Condition):

    MAPPING = {
        'eq': 'equal to',
        'gt': 'greater than',
        'lt': 'less than'
    }

    def __init__(self, sensor, value, operator='eq'):
        self.sensor = sensor
        self.value = int(value)
        self.operator = operator

    def __str__(self):
        return '{} is {} {}'.format(
            self.sensor,
            self.MAPPING[self.operator],
            self.value
        )

    def json(self):
        return {
            'address': '/sensors/{}/state/temperature',
            'operator': self.operator,
            'value': self.value
        }


class TemperatureChanged(Condition):

    def __init__(self, sensor):
        self.sensor

    def __str__(self):
        return '{} has changed'.format(self.sensor)

    def json(self):
        return {
            'address': '/sensors/{}/state/lastupdated',
            'operator': 'dx'
        }

