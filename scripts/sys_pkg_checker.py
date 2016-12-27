#!/usr/bin/env python
"""
For Checking Python CV2 Module
"""

from __future__ import print_function
import os
import sys
import json
import subprocess


class SysPkgChecker(object):
    """
    CI_SKIP: true or false
    PLATFORM: 'ALL', 'darwin', 'linux2', or 'win32'
    PKG_NAME: the package's name
    CMD: the array which contains the command and arguments
    """
    _SYS_PKG_LIST_FILE_NAME = 'system_packages_list.json'

    _CI_SKIP = 'CI_SKIP'

    _PLATFORM = 'PLATFORM'
    _PLATFORM_ALL = 'ALL'
    _PLATFORM_MAC = 'darwin'
    _PLATFORM_LINUX = 'linux2'
    _PLATFORM_WIN = 'win32'

    _PKG_NAME = 'PKG_NAME'

    _CMD = 'CMD'
    _CMD_SUCCESS = 0

    def __init__(self):
        self.current_file_dir = os.path.dirname(os.path.realpath(__file__))
        self.current_platform = sys.platform
        self.is_ci = False
        try:
            sys_pkg_list_file = os.path.join(self.current_file_dir, SysPkgChecker._SYS_PKG_LIST_FILE_NAME)
            with open(sys_pkg_list_file, 'r') as fp:
                print('[INFO] Loading packages list from {} ...'.format(sys_pkg_list_file), end='\n')
                self.sys_pkg_info_list = json.load(fp)
        except Exception as e:
            print(e)
            print('[WARN] Loading default packages list ...', end='\n')
            self.sys_pkg_info_list = [
                {'CI_SKIP': True, 'PLATFORM': 'darwin', 'PKG_NAME': 'ffmpeg', 'CMD': ['ffmpeg', '-h']},
                {'CI_SKIP': False, 'PLATFORM': 'ALL', 'PKG_NAME': 'imagemagick', 'CMD': ['convert', '-version']},
                {'CI_SKIP': False, 'PLATFORM': 'ALL', 'PKG_NAME': 'imagemagick', 'CMD': ['compare', '-version']},
                {'CI_SKIP': False, 'PLATFORM': 'ALL', 'PKG_NAME': 'mitmproxy', 'CMD': ['mitmdump', '-h']},
                {'CI_SKIP': True, 'PLATFORM': 'ALL', 'PKG_NAME': 'sikulix', 'CMD': ['./thirdParty/runsikulix', '-h']}]

    def setup_ci(self, is_ci=False):
        self.is_ci = is_ci

    def check(self):
        error_pkg_list = []
        for sys_pkg_info in self.sys_pkg_info_list:
            ci_skip = sys_pkg_info.get(SysPkgChecker._CI_SKIP, False)
            platform = sys_pkg_info.get(SysPkgChecker._PLATFORM, SysPkgChecker._PLATFORM_ALL)
            pkg_name = sys_pkg_info.get(SysPkgChecker._PKG_NAME, '')
            cmd = sys_pkg_info.get(SysPkgChecker._CMD, [])

            # raise error message if there is no command
            if not cmd:
                raise Exception('[ERROR] No command. Raw data: {}'.format(sys_pkg_info))

            print('[INFO] Check {} ... '.format(pkg_name), end='')
            # skip when Env is CI, and this package have to skip in CI.
            if self.is_ci and ci_skip:
                print('CI Skip'.format(pkg_name))
                continue
            elif platform != SysPkgChecker._PLATFORM_ALL and platform != self.current_platform:
                print('Skip, current platform is {}, not {}'.format(self.current_platform, platform), end='\n')
                continue
            else:
                with open(os.devnull) as fp:
                    try:
                        #ret_code = subprocess.call(cmd, stdout=fp, stderr=fp)
                        ret_code = subprocess.call(cmd)
                        if ret_code == SysPkgChecker._CMD_SUCCESS:
                            print('OK', end='\n')
                        else:
                            print('Fail, return code {}'.format(ret_code), end='\n')
                            error_pkg_list.append(pkg_name)
                    except Exception as e:
                        print(e)
                        print('Fail', end='\n')
                        error_pkg_list.append(pkg_name)
        return error_pkg_list


def main():
    try:
        checker = SysPkgChecker()
        if os.getenv('TRAVIS', False):
            print('[INFO] The environment variable "TRAVIS" is True, enable CI mode.', end='\n')
            checker.setup_ci(True)
        error_pkg_list = checker.check()
        if not error_pkg_list:
            print('[INFO] Check system packages passed.', end='\n')
        else:
            print('[Error] Some system packages failed.', end='\n')
            for pkg in error_pkg_list:
                print('\t{}'.format(pkg))
            exit(1)
    except Exception as e:
        print('[Error] Check system packages failed.', end='\n')
        print(e)
        exit(1)


if __name__ == '__main__':
    main()
