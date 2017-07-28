from mozillapulse.publishers import GenericPublisher
from mozillapulse.publishers import PulseConfiguration


class HasalPublisher(GenericPublisher):

    def __init__(self, **kwargs):
        if kwargs.get('user'):
            username = kwargs.get('user')
            super(HasalPublisher, self).__init__(
                PulseConfiguration(**kwargs), 'exchange/{u}/hasal'.format(u=username), **kwargs)
        else:
            raise Exception('No user')
