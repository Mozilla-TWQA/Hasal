import json
import copy
import argparse
from argparse import ArgumentDefaultsHelpFormatter


class ResultMetricGenerator(object):

    def __init__(self, input_result_fp):
        self.result_fp = input_result_fp

    def generate_metric(self):
        with open(self.result_fp) as fh:
            obj_json = json.load(fh)
            print(
                '{s1:<45} {s2:<18} {s3:<18} {s4:<18}'.format(s1="Case Name",
                                                             s2="Median time",
                                                             s3="Average Time",
                                                             s4="Standard deviation"
                                                             ))
            print('{s1:{c}^{n1}}'.format(s1="", c="=", n1=99))
            key_list = copy.deepcopy(obj_json.keys())
            key_list.sort()

            for case_name in key_list:
                key_count = 0
                for key_name in ['med_time', 'avg_time', 'std_dev']:
                    if key_name in obj_json[case_name]:
                        key_count += 1

                if key_count == len(['med_time', 'avg_time', 'std_dev']):
                    print(
                        '{s1:<45} {s2:<18} {s3:<18} {s4:<18}'.format(s1=case_name,
                                                                     s2=obj_json[case_name]['med_time'],
                                                                     s3=obj_json[case_name]['avg_time'],
                                                                     s4=obj_json[case_name]['std_dev']))
                else:
                    print(
                        '{s1:<45} {s2:<18} {s3:<18} {s4:<18}'.format(s1=case_name,
                                                                     s2="Something wrong",
                                                                     s3="Something wrong",
                                                                     s4="Something wrong"))

    def run(self):
        self.generate_metric()


def main():
    arg_parser = argparse.ArgumentParser(description='Result Metric Generator',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-i', action='store', dest='input_result_fp', default=False,
                            help='specify the file need to parse', required=True)
    args = arg_parser.parse_args()
    run_obj = ResultMetricGenerator(args.input_result_fp)
    run_obj.run()

if __name__ == '__main__':
    main()
