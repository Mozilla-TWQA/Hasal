import re


class CommonUtil(object):
    @staticmethod
    def atoi(text):
        return int(text) if text.isdigit() else text

    @classmethod
    def natural_keys(cls, text):
        return [cls.atoi(c) for c in re.split('(\d+)', text)]
