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
                '{s1:<50}\t{s2:<15}\t{s3:<15}\t{s4:<15}\t{s5:<15}\t{s6:<15}'.format(s1="CASE NAME",
                                                                                    s2="MEDIAN",
                                                                                    s3="AVG",
                                                                                    s4="STD",
                                                                                    s5="SI",
                                                                                    s6="PSI"))
            print(
                '{s1:<50}\t{s2:<15}\t{s3:<15}\t{s4:<15}\t{s5:<15}\t{s6:<15}'.format(s1="##############################",
                                                                                    s2="###############",
                                                                                    s3="###############",
                                                                                    s4="###############",
                                                                                    s5="###############",
                                                                                    s6="###############"))
            key_list = copy.deepcopy(obj_json.keys())
            # sort by browser "test_<BROWSER>"_<CASENAME>
            key_list.sort()
            # then sort by case name test_<BROWSER>_"<CASENAME>"
            key_list.sort(key=lambda x: x.split('_', 2)[2])

            for case_name in key_list:
                print(
                    '{s1:<50}\t{s2:<15}\t{s3:<15}\t{s4:<15}\t{s5:<15}\t{s6:<15}'.format(s1=case_name,
                                                                                        s2=str(obj_json[case_name].get('med_time', 'na')),
                                                                                        s3=str(obj_json[case_name].get('avg_time', 'na')),
                                                                                        s4=str(obj_json[case_name].get('std_dev', 'na')),
                                                                                        s5=str(obj_json[case_name].get('speed_index', 'na')),
                                                                                        s6=str(obj_json[case_name].get('perceptual_speed_index', 'na'))))

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
