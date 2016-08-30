# Copyright 2013 The Servo Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from __future__ import print_function, unicode_literals

import os

from mach.decorators import (
    CommandArgument,
    CommandProvider,
    Command,
)

from tidy import tidy
from tidy_tests import test_tidy

SCRIPT_PATH = os.path.split(__file__)[0]
PROJECT_TOPLEVEL_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, "..", ".."))
SERVO_TESTS_PATH = os.path.join("tests", "wpt", "mozilla", "tests")


@CommandProvider
class MachCommands():
    DEFAULT_RENDER_MODE = "cpu"
    HELP_RENDER_MODE = "Value can be 'cpu', 'gpu' or 'both' (default " + DEFAULT_RENDER_MODE + ")"

    def __init__(self, context):
        pass

    @Command('test-tidy',
             description='Run the source code tidiness check',
             category='testing')
    @CommandArgument('--all', default=False, action="store_true", dest="all_files",
                     help="Check all files, and run the WPT lint in tidy, "
                          "even if unchanged")
    @CommandArgument('--no-progress', default=False, action="store_true",
                     help="Don't show progress for tidy")
    @CommandArgument('--self-test', default=False, action="store_true",
                     help="Run unit tests for tidy")
    def test_tidy(self, all_files, no_progress, self_test):
        if self_test:
            return test_tidy.do_tests()
        else:
            return tidy.scan(not all_files, not no_progress)
