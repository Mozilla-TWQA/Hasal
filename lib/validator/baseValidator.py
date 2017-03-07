
class BaseValidator(object):

    def __init__(self):
        self.output = None

    def validate(self, validate_data):
        pass

    def get_output(self):
        return self.output
