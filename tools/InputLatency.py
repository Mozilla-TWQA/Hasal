#!/usr/bin/env python

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import argparse
from argparse import ArgumentDefaultsHelpFormatter


class InputLatencyGenerator(object):

    """
    class InputLatencyGenerator
    """

    def __init__(self, input_result_fp, output_mode=0):
        """
        __init__
        """
        self.result_fp = input_result_fp
        self.output_mode = int(output_mode)
        self.DEFAULT_SHORT_VIEW_MODE = 0
        self.DEFAULT_EASY_PASTE_MODE = 1

    def generate_metric(self):
        DEFAULT_PRINT_KEY_INDEX = ['avg_time',
                                   'max_time',
                                   'med_time',
                                   'min_time',
                                   'std_dev']
        """
        generate_metric
        """

        with open(self.result_fp) as data_file:
            # Setup pandas display options
            pd.options.display.float_format = '{:10,.2f}'.format
            pd.set_option('display.width', 999)

            # Loading input file
            data = json.load(data_file)
            d = pd.DataFrame(data)

            # Analyze input latency
            runtime = pd.DataFrame(
                [pd.DataFrame(d[c]['time_list'])['run_time'] for c in d]).T
            runtime.columns = d.columns
            print '===== Input Latency Summary ===='
            print d.loc[DEFAULT_PRINT_KEY_INDEX, :]
            print '\n\n===== Input Latency Raw runtime ===='
            print runtime
            print '\n\n===== Input Latency runtime Percentile===='
            print runtime.quantile([0.01, 0.99], interpolation='nearest')
            print '\n\n===== Input Latency runtime Table===='
            print runtime.describe()
            print '\n\n===== Input Latency runtime Plots===='
            runtime.plot.hist(bins=20, histtype='bar',
                              color=['green', 'orange', 'red', 'blue'])
            runtime.plot.box()
            plt.show()

    def run(self):
        """
        run()
        """
        self.generate_metric()


def main():
    """ 
    function main() as entry point 
    """

    arg_parser = argparse.ArgumentParser(description='Input Latency Report',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-i', action='store', dest='input_result_fp', default=None,
                            help='specify the file need to parse', required=True)
    args = arg_parser.parse_args()
    run_obj = InputLatencyGenerator(args.input_result_fp)
    run_obj.run()


if __name__ == '__main__':
    main()
