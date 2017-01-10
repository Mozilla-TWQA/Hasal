import os
import sys
import time
import shutil
import tempfile
from lib.common.logConfig import get_logger

logger = get_logger(__name__)


class FirefoxProfileCreator(object):
    def __init__(self):
        if sys.platform == 'darwin':
            self.firefox_cmd = '/Applications/Firefox.app/Contents/MacOS/firefox'
        else:
            self.firefox_cmd = 'firefox'
        self._firefox_profile_path = ''

    def get_firefox_profile(self, prefs={}, extensions_settings={}):
        if self._firefox_profile_path:
            logger.info('Get Profile: {}'.format(self._firefox_profile_path))
            return self._firefox_profile_path
        else:
            profile_path = self._create_firefox_profile(prefs=prefs)
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

    def _install_profile_extensions(self, extensions_settings={}):
        if extensions_settings:
            # TODO: can install extensions into self._firefox_profile_path
            logger.warn('Not Implemented')
        return

    def remove_firefox_profile(self):
        if os.path.isdir(self._firefox_profile_path):
            for _ in range(10):
                try:
                    logger.info('Remove Profile: {}'.format(self._firefox_profile_path))
                    shutil.rmtree(self._firefox_profile_path)
                    break
                except Exception as e:
                    logger.warn(e)
                    time.sleep(1)
