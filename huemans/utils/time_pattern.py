class TimePattern(object):

    def __str__(self):
        raise NotImplementedError('Please implement __str__ function')


class SimpleTimer(TimePattern):

    def __init__(self, seconds=0, minutes=0, hours=0):
        self.seconds = seconds
        self.minutes = minutes
        self.hours = hours

    def __str__(self):
        total_seconds = self.hours * 3600 + self.minutes * 60 + self.seconds
        return 'PT{0:0>2}:{1:0>2}:{2:0>2}'.format(total_seconds // 3600, total_seconds % 3600 // 60, total_seconds % 60)
