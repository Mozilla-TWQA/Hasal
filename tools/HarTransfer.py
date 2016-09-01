import json
import argparse
from argparse import ArgumentDefaultsHelpFormatter


class HarParser(object):
    def __init__(self, input_har):
        self.old_har = input_har

    def parse(self, method=""):
        with open(self.old_har, "r") as f:
            self.har_dict = json.load(f)

        self.har_dict["log"]["version"] = "1.2"

        entries = self.har_dict["log"]["entries"]
        if method == "remove":
            for i in range(len(entries)):
                if self.har_dict["log"]["entries"][i]['time'] is None:
                    del self.har_dict["log"]["entries"][i]
                    break
                if self.har_dict["log"]["entries"][i]['timings']['send'] is None:
                    del self.har_dict["log"]["entries"][i]
                    break
                if self.har_dict["log"]["entries"][i]['timings']['wait'] is None:
                    del self.har_dict["log"]["entries"][i]
                    break
                if self.har_dict["log"]["entries"][i]['timings']['receive'] is None:
                    del self.har_dict["log"]["entries"][i]
                    break
                if 'mimeType' not in self.har_dict["log"]["entries"][i]['response']['content']:
                    del self.har_dict["log"]["entries"][i]
                    break
        elif method == "putzero":
            for i in range(len(entries)):
                if self.har_dict["log"]["entries"][i]['time'] is None:
                    self.har_dict["log"]["entries"][i]['time'] = 0
                if self.har_dict["log"]["entries"][i]['timings']['send'] is None:
                    self.har_dict["log"]["entries"][i]['timings']['send'] = 0
                if self.har_dict["log"]["entries"][i]['timings']['wait'] is None:
                    self.har_dict["log"]["entries"][i]['timings']['wait'] = 0
                if self.har_dict["log"]["entries"][i]['timings']['receive'] is None:
                    self.har_dict["log"]["entries"][i]['timings']['receive'] = 0
                if 'mimeType' not in self.har_dict["log"]["entries"][i]['response']['content']:
                    self.har_dict["log"]["entries"][i]['response']['content']['mimeType'] = 'None'

    def output(self, filename="output.har"):
        with open(filename, "w+") as f:
            json.dump(self.har_dict, f, indent=4)


def main():
    arg_parser = argparse.ArgumentParser(description='HAR Parser to HAR version 1.2',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-i', action='store', dest='input_har', default=False,
                            help='specify the file need to parse', required=True)
    args = arg_parser.parse_args()
    obj = HarParser(args.input_har)
    obj.parse("remove")
    obj.output()


if __name__ == '__main__':
    main()
