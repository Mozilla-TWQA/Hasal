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


@CommandProvider
class MachCommands():
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

    @Command('test-config',
             description='Run the config files check',
             category='testing')
    def test_configs(self):
        from lib.validator.configValidator import ConfigValidator
        print('Checking config files ...')
        result = ConfigValidator.validate_default_configs()
        return int(0 if result else 1)
