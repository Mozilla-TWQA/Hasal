import os
import sys
import time
import json
import shutil
import tempfile
from lib.common.logConfig import get_logger
from lib.common.pyDriveUtil import PyDriveUtil
from ..common.environment import Environment

logger = get_logger(__name__)


class FirefoxProfileCreator(object):
    def __init__(self):
        if sys.platform == 'darwin':
            self.firefox_cmd = '/Applications/Firefox.app/Contents/MacOS/firefox'
        else:
            self.firefox_cmd = 'firefox'
        self._firefox_profile_path = ''

    def get_firefox_profile(self, prefs={}, cookies_settings={}, extensions_settings={}):
        if self._firefox_profile_path:
            logger.info('Get Profile: {}'.format(self._firefox_profile_path))
            return self._firefox_profile_path
        else:
            profile_path = self._create_firefox_profile(prefs=prefs)
            self._download_cookies(cookies_settings=cookies_settings)
            self._install_profile_extensions(extensions_settings=extensions_settings)
            return profile_path

    def _create_firefox_profile(self, prefs={}):
        tmp_profile_dir = tempfile.mkdtemp(prefix='firefoxprofile_')
        logger.info('Creating Profile: {}'.format(tmp_profile_dir))
        logger.info('Profile with prefs: {}'.format(prefs))
        os.system('{} --profile {} -silent'.format(self.firefox_cmd, tmp_profile_dir))

        prefs_list = []
        prefs_js_file = os.path.join(tmp_profile_dir, 'prefs.js')
        for k, v in prefs.items():
            if isinstance(v, bool) or isinstance(v, int):
                prefs_list.append('user_pref("{}", {});'.format(str(k), str(v).lower()))
            elif isinstance(v, str) or isinstance(v, unicode):
                prefs_list.append('user_pref("{}", "{}");'.format(str(k), str(v)))
        # Skip First Run page
        prefs_list.append('user_pref("toolkit.startup.last_success", {});'.format(int(time.time())))
        prefs_list.append('user_pref("browser.startup.homepage_override.mstone", "ignore");')
        prefs_settings = '\n'.join(prefs_list)

        with open(prefs_js_file, 'a') as prefs_f:
            prefs_f.write('\n' + prefs_settings)
        logger.info('[Info] Creating Profile success: {}'.format(tmp_profile_dir))
        self._firefox_profile_path = tmp_profile_dir
        return self._firefox_profile_path

    def _download_cookies(self, cookies_settings={}):
        if cookies_settings:
            folder = cookies_settings.get('folder', '')
            filename = cookies_settings.get('filename', '')
            if folder and filename:
                drive_handler = PyDriveUtil()
                drive_file_obj = drive_handler.get_file_object(folder_uri=folder, file_name=filename)
                if drive_file_obj:
                    cookies_target_path = os.path.join(self._firefox_profile_path, 'cookies.sqlite')
                    drive_file_obj.GetContentFile(cookies_target_path)
                    logger.info('Download cookies file to {}'.format(cookies_target_path))
                else:
                    logger.warn('Cannot found file: {}'.format(filename))

    def _install_profile_extensions(self, extensions_settings={}):
        if extensions_settings:
            extensions_json_file = os.path.join(self._firefox_profile_path, 'extensions.json')
            extensions_folder = os.path.join(self._firefox_profile_path, 'extensions')
            import_extensions_folder = Environment.DEFAULT_EXTENSIONS_DIR

            for name in extensions_settings.keys():
                ext = extensions_settings[name]
                if not ext['enable']:
                    logger.info(name + ' requires no additional add-on installation.')
                    continue

                logger.info('Handling "' + name + '" related profiler now.')
                for xpi in ext['XPI']:
                    logger.info('Installing "' + xpi + '" add-on now.')
                    xpi_loc = os.path.join(import_extensions_folder, xpi, xpi + ".xpi")
                    xpi_json = os.path.join(import_extensions_folder, xpi, "extensions.json")

                    with open(extensions_json_file) as f, open(xpi_json) as a:
                        data = json.load(f)
                        new_data = json.load(a)
                        data['addons'].append(new_data)

                        pos = len(data['addons']) - 1
                        new_xpi_name = data['addons'][pos]['descriptor'].split("/")[-1].split("\\")[-1]
                        data['addons'][pos]['descriptor'] = os.path.join(extensions_folder, new_xpi_name)
                        data['addons'][pos]['sourceURI'] = None

                    with open(extensions_json_file, 'w') as f:
                        json.dump(data, f)

                    shutil.copyfile(os.path.join(xpi_loc, data['addons'][pos]['descriptor']))

    def remove_firefox_profile(self):
        if self._firefox_profile_path and os.path.isdir(self._firefox_profile_path):
            for _ in range(10):
                try:
                    logger.info('Remove Profile: {}'.format(self._firefox_profile_path))
                    shutil.rmtree(self._firefox_profile_path)
                    break
                except Exception as e:
                    logger.warn(e)
                    time.sleep(1)
