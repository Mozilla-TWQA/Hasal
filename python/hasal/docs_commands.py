from __future__ import print_function, unicode_literals

import os
import shutil
import subprocess

from mach.decorators import (
    CommandArgument,
    CommandProvider,
    Command,
)

SCRIPT_PATH = os.path.split(__file__)[0]
PROJECT_TOPLEVEL_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, "..", ".."))


@CommandProvider
class MachCommands():

    def __init__(self, context):
        pass

    @Command('docs',
             description='Run the source code tidiness check',
             category='testing')
    @CommandArgument('-a', '--all', default=True, action='store_false', dest='all_docs',
                     help='Generate all documents.')
    @CommandArgument('--api', default=False, action='store_true', dest='api',
                     help='Generate API documents')
    @CommandArgument('--output', default='docs', dest='output',
                     help='Output folder.')
    def generate_docs(self, all_docs, api, output):
        FOLDER_DOCS_PATH = os.path.join(PROJECT_TOPLEVEL_PATH, output)

        FOLDER_API_NAME = 'api'
        FOLDER_API_PATH = os.path.join(FOLDER_DOCS_PATH, FOLDER_API_NAME)

        print('[Docs] Generating docs into {} folder ...'.format(FOLDER_DOCS_PATH))
        if not os.path.exists(FOLDER_DOCS_PATH):
            os.makedirs(FOLDER_DOCS_PATH)
        elif os.path.isdir(FOLDER_DOCS_PATH):
            shutil.rmtree(FOLDER_DOCS_PATH)
            os.makedirs(FOLDER_DOCS_PATH)

        if api or all_docs:
            if not os.path.exists(FOLDER_API_PATH):
                os.makedirs(FOLDER_API_PATH)
            elif os.path.isdir(FOLDER_API_PATH):
                shutil.rmtree(FOLDER_API_PATH)
                os.makedirs(FOLDER_API_PATH)

            print('[docs] Generating API docs ... ', end='')
            try:
                commands = ['epydoc', '--config', 'python/epydoc.cfg', '--output', FOLDER_API_PATH]
                subprocess.check_call(commands)
                print('Done')
            except Exception as e:
                print('Fail')
                print(e)

        print('[Docs] Generating docs done')
