import json
import copy
import argparse
from argparse import ArgumentDefaultsHelpFormatter


class ResultMetricGenerator(object):

    def __init__(self, input_result_fp, input_mode):
        self.result_fp = input_result_fp
        self.output_mode = int(input_mode)
        self.DEFAULT_SHORT_VIEW_MODE = 0
        self.DEFAULT_EASY_PASTE_MODE = 1

    def generate_metric(self):
        with open(self.result_fp) as fh:
            obj_json = json.load(fh)
            if self.output_mode == self.DEFAULT_EASY_PASTE_MODE:
                title_format_str = '{s1:<50}\t{s2:<80}\t{s3:<80}'
                content_format_str = '{s1:<50}\t{s2:<15}\t{s3:<15}\t{s4:<15}\t{s5:<15}\t{s6:<15}\t{s7:<15}\t{s8:<15}\t{s9:<15}\t{s10:<15}\t{s11:<15}'
            elif self.output_mode == self.DEFAULT_SHORT_VIEW_MODE:
                content_format_str = '{s1:<50}\t{s2:<15}\t{s3:<15}\t{s4:<15}\t{s5:<15}\t{s6:<15}'

            if self.output_mode == self.DEFAULT_EASY_PASTE_MODE:
                print(title_format_str.format(s1="CASE NAME", s2="CHROME", s3="FIREFOX"))
                print(
                content_format_str.format(s1="CASE NAME", s2="MEDIAN", s3="AVG", s4="STD", s5="SI", s6="PSI", s7="MEDIAN",
                                          s8="AVG", s9="STD", s10="SI", s11="PSI"))
                print(
                    content_format_str.format(s1="##############################",s2="###############",s3="###############",
                                              s4="###############", s5="###############", s6="###############",
                                              s7="###############", s8="###############", s9="###############",
                                              s10="###############", s11="###############"))
            elif self.output_mode == self.DEFAULT_SHORT_VIEW_MODE:
                print(
                    content_format_str.format(s1="CASE NAME", s2="MEDIAN", s3="AVG", s4="STD", s5="SI", s6="PSI"))
                print(
                    content_format_str.format(s1="##############################", s2="###############",
                                              s3="###############",
                                              s4="###############", s5="###############", s6="###############"))


            key_list = copy.deepcopy(obj_json.keys())
            # sort by browser "test_<BROWSER>"_<CASENAME>
            key_list.sort()
            # then sort by case name test_<BROWSER>_"<CASENAME>"
            key_list.sort(key=lambda x: x.split('_', 2)[2])

            handle_data = {}
            if self.output_mode == self.DEFAULT_EASY_PASTE_MODE:
                for c_name in key_list:
                    case_name = "_".join(c_name.split("_")[2:])
                    browser_type = c_name.split("_")[1].lower()
                    if case_name in handle_data:
                        if browser_type not in handle_data[case_name]:
                            handle_data[case_name][browser_type] = copy.deepcopy(obj_json[c_name])
                    else:
                        handle_data[case_name] = {browser_type:obj_json[c_name]}

                for case_name in handle_data:
                    print(content_format_str.format(s1=case_name,
                                                    s2=str(handle_data[case_name]["chrome"].get('med_time', 'na')),
                                                    s3=str(handle_data[case_name]["chrome"].get('avg_time', 'na')),
                                                    s4=str(handle_data[case_name]["chrome"].get('std_dev', 'na')),
                                                    s5=str(handle_data[case_name]["chrome"].get('speed_index', 'na')),
                                                    s6=str(handle_data[case_name]["chrome"].get('perceptual_speed_index',
                                                                                                'na')),
                                                    s7=str(
                                                        handle_data[
                                                            case_name][
                                                            "firefox"].get(
                                                            'med_time',
                                                            'na')),
                                                    s8=str(
                                                        handle_data[
                                                            case_name][
                                                            "firefox"].get(
                                                            'avg_time',
                                                            'na')),
                                                    s9=str(
                                                        handle_data[
                                                            case_name][
                                                            "firefox"].get(
                                                            'std_dev',
                                                            'na')),
                                                    s10=str(
                                                        handle_data[
                                                            case_name][
                                                            "firefox"].get(
                                                            'speed_index',
                                                            'na')),
                                                    s11=str(
                                                        handle_data[
                                                            case_name][
                                                            "firefox"].get(
                                                            'perceptual_speed_index',
                                                            'na'))
                                                    ))
            elif self.output_mode == self.DEFAULT_SHORT_VIEW_MODE:
                for case_name in key_list:
                    print(content_format_str.format(s1=case_name,
                                                    s2=str(obj_json[case_name].get('med_time', 'na')),
                                                    s3=str(obj_json[case_name].get('avg_time', 'na')),
                                                    s4=str(obj_json[case_name].get('std_dev', 'na')),
                                                    s5=str(obj_json[case_name].get('speed_index', 'na')),
                                                    s6=str(obj_json[case_name].get('perceptual_speed_index', 'na'))
                                                    ))


    def run(self):
        self.generate_metric()


def main():
    arg_parser = argparse.ArgumentParser(description='Result Metric Generator',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-i', action='store', dest='input_result_fp', default=False,
                            help='specify the file need to parse', required=True)
    arg_parser.add_argument('-m', action='store', dest='input_mode', default=False,
                            help='specify output mode', required=True)
    args = arg_parser.parse_args()
    run_obj = ResultMetricGenerator(args.input_result_fp, args.input_mode)
    run_obj.run()

if __name__ == '__main__':
    main()
