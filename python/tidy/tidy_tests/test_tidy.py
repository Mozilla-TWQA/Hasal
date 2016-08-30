# Copyright 2013 The Servo Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import os
import unittest
from tidy import tidy

base_path = 'tidy_tests/' if os.path.exists('tidy_tests/') else 'python/tidy/tidy_tests/'


def iterFile(name):
    return iter([os.path.join(base_path, name)])


class CheckTidiness(unittest.TestCase):
    def assertNoMoreErrors(self, errors):
        with self.assertRaises(StopIteration):
            errors.next()

    def test_spaces_correctnes(self):
        errors = tidy.collect_errors_for_files(iterFile('wrong_space.rs'), [], [tidy.check_by_line], print_text=False)
        self.assertEqual('trailing whitespace', errors.next()[2])
        self.assertEqual('no newline at EOF', errors.next()[2])
        self.assertEqual('tab on line', errors.next()[2])
        self.assertEqual('CR on line', errors.next()[2])
        self.assertEqual('no newline at EOF', errors.next()[2])
        self.assertNoMoreErrors(errors)

    def test_hasal_testname(self):
        webappname = 'webFOO'
        filename='./tests/pilot/{}/nothing/test_firefox_BAR_launch.py'.format(webappname)
        errors = tidy.check_hasal_testname(filename, '')
        self.assertEqual("the file name should starts with 'test_<BROWSER>_{}_".format(webappname), errors.next()[2])
        self.assertNoMoreErrors(errors)

    def test_file_list(self):
        base_path='./python/tidy/tidy_tests/test_ignored'
        file_list = tidy.get_file_list(base_path, only_changed_files=False,
                                       exclude_dirs=[])
        lst = list(file_list)
        self.assertEqual([os.path.join(base_path, 'whee', 'test.rs')], lst)
        file_list = tidy.get_file_list(base_path, only_changed_files=False,
                                       exclude_dirs=[os.path.join(base_path,'whee')])
        lst = list(file_list)
        self.assertEqual([], lst)

def do_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(CheckTidiness)
    unittest.TextTestRunner(verbosity=2).run(suite)
