import os
import sys
import time
import psutil
import shutil
import tempfile
import subprocess
from lib.common.logConfig import get_logger
from lib.common.pyDriveUtil import PyDriveUtil
from lib.helper.desktopHelper import close_browser

logger = get_logger(__name__)


class ChromeProfileCreator(object):
    def __init__(self, chrome_profile_path=''):
        self.browser_type = "chrome"
        self.current_platform_name = sys.platform
        if self.current_platform_name == 'darwin':
            self.chrome_cmd = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            self.process_name = "Google Chrome"
        elif self.current_platform_name == "linux2":
            self.chrome_cmd = 'google-chrome'
            self.process_name = "Chrome"
        else:
            self.chrome_cmd = 'chrome'
            self.process_name = "chrome.exe"
        self._chrome_profile_path = chrome_profile_path

    def get_chrome_profile(self, cookies_settings={}):
        if self._chrome_profile_path:
            logger.info('Get Profile: {}'.format(self._chrome_profile_path))
            return self._chrome_profile_path
        else:
            profile_path = self._create_chrome_profile()
            self._download_cookies(cookies_settings=cookies_settings)
            return profile_path

    def _create_chrome_profile(self):
        tmp_profile_dir = tempfile.mkdtemp(prefix='chromeprofile_')
        logger.info('Creating Profile: {}'.format(tmp_profile_dir))
        self._chrome_profile_path = tmp_profile_dir
        if self.current_platform_name == 'darwin':
            launch_cmd = [self.chrome_cmd, '--user-data-dir={}'.format(tmp_profile_dir), '--no-first-run']
            subprocess.Popen(launch_cmd)
            # wait for folder creation
            for _ in range(10):
                chrome_profile_default_folder = os.path.join(self._chrome_profile_path, 'Default')
                if os.path.exists(chrome_profile_default_folder):
                    logger.debug('Profile default folder is created.')
                    time.sleep(0.5)
                    break
                else:
                    time.sleep(0.5)
            # close browser
            close_browser(self.browser_type)
            # wait for process finish
            for _ in range(10):
                p_exist = False
                for p in psutil.process_iter():
                    if self.process_name.lower() in p.name().lower():
                        p_exist = True
                        break
                if p_exist:
                    time.sleep(0.5)
                else:
                    break

        else:
            cmd_str = '{} --no-startup-window --user-data-dir={}'.format(self.chrome_cmd, tmp_profile_dir)
            os.system(cmd_str)
        logger.info('Creating Profile success: {}'.format(self._chrome_profile_path))
        return self._chrome_profile_path

    def _download_cookies(self, cookies_settings={}):
        if cookies_settings:
            folder = cookies_settings.get('folder', '')
            for key in cookies_settings.keys():
                filename = cookies_settings.get(key, '')
                if key != 'folder' and folder and filename:
                    if folder and filename:
                        drive_handler = PyDriveUtil()
                        drive_file_obj = drive_handler.get_file_object(folder_uri=folder, file_name=filename)
                        if drive_file_obj:
                            cookies_target_path = os.path.join(self._chrome_profile_path, 'Default', key)
                            drive_file_obj.GetContentFile(cookies_target_path)
                            logger.info('Download cookies file to {}'.format(cookies_target_path))
                        else:
                            logger.warn('Cannot found file: {}'.format(filename))

    def remove_chrome_profile(self):
        if self._chrome_profile_path and os.path.isdir(self._chrome_profile_path):
            for _ in range(10):
                try:
                    logger.info('Remove Profile: {}'.format(self._chrome_profile_path))
                    shutil.rmtree(self._chrome_profile_path)
                    break
                except Exception as e:
                    logger.warn(e)
                    time.sleep(1)
