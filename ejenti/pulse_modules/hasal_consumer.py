from mozillapulse.consumers import GenericConsumer
from mozillapulse.consumers import PulseConfiguration


class HasalConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        if kwargs.get('user'):
            username = kwargs.get('user')
            super(HasalConsumer, self).__init__(
                PulseConfiguration(**kwargs), 'exchange/{u}/hasal'.format(u=username), **kwargs)
        else:
            raise Exception('No user')
