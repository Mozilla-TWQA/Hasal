import os
import re
import web
import json
import time
from datetime import datetime
import shutil
import urlparse
from threading import Lock

from lib.common.outlier import outlier

urls = (
    '/', 'Index',
    '/reset/(.*)', 'Reset',
    '/all_result/', 'AllResult',
    '/hasal/(.*)/(.*)/(.*)', 'HasalServer',
    '/hasal_perf_reg/(.*)/(.*)/(.*)', 'HasalServerPerfherderRegister',
    '/video_profile/(.*)/(.*)/(.*)', 'VideoProfileUpdater'
)


class Formater:

    @staticmethod
    def timestamp_to_date_string(timestamp):
        # For Javascript, 'var d = new Date(timestamp * 1000)' can work.
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


class StorageHandler:
    """
    Please add the 'config.json' file under '~/.hasal_server/'.
    The file content example:
        {"test_times": 30}
    If there is no config file, the default value will be 30 times.
    """
    _storage_mutex = Lock()
    _storage_dir = os.path.expanduser('~/.hasal_server/')
    _storage_path = os.path.join(_storage_dir, 'dump.json')
    _config_path = os.path.join(_storage_dir, 'config.json')
    _register_mutex = Lock()
    _register_path = os.path.join(_storage_dir, 'register.json')

    def __init__(self):
        pass

    def load_config(self):
        """
        Return the config from config.json of '~/.hasal_server/'
        :return: The config json. ex: {"test_times": 30}
        """
        if os.path.isfile(self._config_path):
            with open(self._config_path, 'r') as f:
                return json.load(f)
        return {"test_times": 30}

    def load_register(self):
        """
        Return the info from dump.json from '~/.hasal_server/'
        :return: json if file exists, or {}
        """
        if os.path.isfile(self._register_path):
            with open(self._register_path, 'r') as f:
                return json.load(f)
        return {}

    def save_register(self, json_obj):
        StorageHandler._register_mutex.acquire()
        try:
            if not os.path.exists(self._storage_dir):
                os.makedirs(self._storage_dir)
            if os.path.isdir(self._register_path):
                shutil.rmtree(self._register_path)
            with open(self._register_path, 'w') as f:
                json.dump(json_obj, f)
        finally:
            StorageHandler._register_mutex.release()

    def load(self):
        """
        Return the info from dump.json from '~/.hasal_server/'
        :return: json if file exists, or {}
        """
        if os.path.isfile(self._storage_path):
            with open(self._storage_path, 'r') as f:
                return json.load(f)
        return {}

    def save(self, json_obj):
        StorageHandler._storage_mutex.acquire()
        try:
            if not os.path.exists(self._storage_dir):
                os.makedirs(self._storage_dir)
            if os.path.isdir(self._storage_path):
                shutil.rmtree(self._storage_path)
            with open(self._storage_path, 'w') as f:
                json.dump(json_obj, f)
        finally:
            StorageHandler._storage_mutex.release()

    def remove(self):
        if os.path.isdir(self._storage_path):
            shutil.rmtree(self._storage_path)
        elif os.path.isfile(self._storage_path):
            os.remove(self._storage_path)


class AllResult:
    render = web.template.render('templates', base='layout')

    def __init__(self):
        HasalServer.storage = HasalServer.storage_handler.load()

    def GET(self):
        md = []

        for os_name in HasalServer.storage.keys():
            md.append('# {}'.format(os_name))

            targets = HasalServer.storage[os_name]
            for target in targets.keys():
                md.append('## {}'.format(target))

                comments = HasalServer.storage[os_name][target]
                for comment in comments.keys():
                    md.append('### {}'.format(comment))

                    tests = HasalServer.storage[os_name][target][comment]
                    for test in sorted(tests.keys(), key=lambda k: re.sub(r'test_[\w]+_', '', k)):
                        md.append('#### {}'.format(test))

                        browsers = HasalServer.storage[os_name][target][comment][test]
                        for browser in browsers.keys():
                            if len(browsers) > 1:
                                md.append('  * {}'.format(browser))
                            data = browsers[browser]
                            if data.get('revision', '') != '':
                                md.append('    * Revision: {}'.format(data.get('revision')))
                            md.append('    * Median: {}'.format(data.get('median_value')))
                            md.append('    * Sigma: {}'.format(data.get('sigma_value')))
                            md.append('    * Mean: {}'.format(data.get('median_value')))
                            md.append('    * SI: {}'.format(data.get('si')))
                            md.append('    * PSI: {}'.format(data.get('psi')))
                            if data.get('webappname', '') != '':
                                md.append('    * Web App: {}'.format(data.get('webappname')))
                            if data.get('video_path', '') != '':
                                md.append('    * Video: {}'.format(data.get('video_path')))
                            if data.get('profile_path', '') != '':
                                md.append('    * Profile: {}'.format(data.get('profile_path')))
                            md.append('\n')
        markdown_str = '\n'.join(md)
        return self.render.all_result(markdown=markdown_str)


class HasalServerPerfherderRegister:
    """
    Hasal Server Register.
    For storing the "os/target/comment" -> tests list [test_foo, test_bar, ...]
    """
    RET_OK = 0
    RET_DROP = 1

    storage_handler = StorageHandler()
    register = {}

    def __init__(self):
        HasalServerPerfherderRegister.register = HasalServerPerfherderRegister.storage_handler.load_register()

    def return_ret(self, status):
        return {'status': status}

    def save_register(self):
        HasalServerPerfherderRegister.storage_handler.save_register(HasalServerPerfherderRegister.register)

    def POST(self, os_name, target, comment):
        """
        The input json example:
            json={"foo_bar_f": ["test_1", "test_2", ...], "foo_bar_c": ["test_1", "test_2", ...]}
        It will convert to two entries:
            os/target/comment/foo_Bar_f: {"name": "foo_bar_f": ["test_1", "test_2", ...]}
            os/target/comment/foo_Bar_c: {"name": "foo_bar_c": ["test_1", "test_2", ...]}
        :param os_name: os. ex: 'linux'
        :param target: target. ex: 'firefox 36'
        :param comment: comment. ex: '2016-01-01'
        :return: status. 0 is okay. 1 is drop.
            ex: {
                "status": 0
                }
        """
        try:
            # check the url, server/hasal_perf_reg/<os>/<target_browser>/<comment>
            assert os_name is not None and os_name != '', '[os] is empty.'
            assert target is not None and target != '', '[target] is empty.'
            assert comment is not None and comment != '', '[comment] is empty.'

            # get the POST data
            data = web.data()
            parameters = urlparse.parse_qs(data)
            # check the POST data contain 'json'
            assert 'json' in parameters, 'Can not get "json" parameter from POST data.'

            # check the input json object
            json_obj = json.loads(parameters['json'][0])

            if isinstance(json_obj, dict):
                for suite_name, suite_tests in json_obj.items():
                    if not isinstance(suite_tests, list):
                        raise Exception('The value of "{}" is not list: {}'.format(suite_name, suite_tests))

                    HasalServerPerfherderRegister.register = HasalServerPerfherderRegister.storage_handler.load_register()
                    # if there is already value in "os_name/target/comment", drop it and return status 1
                    if HasalServerPerfherderRegister.register.get(os_name, {}).get(target, {}).get(comment, {}).get(suite_name, {}):
                        self.return_ret(self.RET_DROP)
                    else:
                        if os_name not in HasalServerPerfherderRegister.register:
                            HasalServerPerfherderRegister.register[os_name] = {}
                        if target not in HasalServerPerfherderRegister.register[os_name]:
                            HasalServerPerfherderRegister.register[os_name][target] = {}
                        if comment not in HasalServerPerfherderRegister.register[os_name][target]:
                            HasalServerPerfherderRegister.register[os_name][target][comment] = {}
                        if suite_name not in HasalServerPerfherderRegister.register[os_name][target][comment]:
                            HasalServerPerfherderRegister.register[os_name][target][comment][suite_name] = suite_tests
                    self.save_register()
                self.return_ret(self.RET_OK)
            else:
                raise Exception('The parameter is not JSON object: {}'.format(parameters['json'][0]))
        except AssertionError as e:
            raise web.badrequest(e.message)


class HasalServer:
    """
    Hasal Server handler.
    """
    storage_handler = StorageHandler()
    storage = {}
    _calculator = outlier()
    _config = storage_handler.load_config()
    _config_test_times = _config.get('test_times', 30)
    _keys = ['os', 'target_browser', 'test', 'browser']
    # The "value" is "run_time" from agent, the "si", "psi", and "revision" are optional.
    _checks = ['os', 'target', 'test', 'comment', 'webappname', 'browser', 'version', 'platform', 'value', 'video']
    _count = 0
    _template = {
        'os': '',
        'target': '',
        'test': '',
        'comment': '',
        'webappname': '',
        'browser': '',
        'version': '',
        'revision': '',
        'platform': '',
        'median_value': -1,
        'mean_value': -1,
        'sigma_value': -1,
        'si': -1,
        'psi': -1,
        'origin_values': [],  # the list of (value, video, ip)
        'video_path': '',
        'profile_path': '',
        'timestamp': 0,
    }

    def __init__(self):
        HasalServer.storage = HasalServer.storage_handler.load()

    """
    def __del__(self):
        HasalServer._storage_handler.remove()
    """

    @staticmethod
    def check_input_json(json_obj):
        for item in HasalServer._checks:
            assert item in json_obj, 'The json should have "{}" value.'.format(item)

    @staticmethod
    def remove_tuple_from_values(list_obj, removed_values_list):
        tmp = list_obj[:]
        for v in removed_values_list:
            tmp = [item for item in tmp if item.get('run_time') != v.get('run_time')]
        return tmp

    @staticmethod
    def find_video_ip_by_median(list_obj, median):
        index = min([item[0] for item in list_obj], key=lambda x: abs(x - median))
        return [item for item in list_obj if index in item][0]

    @staticmethod
    def save_to_database(os_name, target, test, comment, json_obj):
        # TODO: store the json_obj under /os/target/test/comment/ path.
        pass

    @staticmethod
    def _generate_current_test_obj(json_obj, ip):
        # "si", "psi", and "revision" are optional
        info = HasalServer._template.copy()
        info['os'] = json_obj.get('os')
        info['target'] = json_obj.get('target')
        info['test'] = json_obj.get('test')
        info['comment'] = json_obj.get('comment')
        info['webappname'] = json_obj.get('webappname')
        info['browser'] = json_obj.get('browser')
        info['version'] = json_obj.get('version')
        info['revision'] = json_obj.get('revision', '')
        info['platform'] = json_obj.get('platform')
        info['origin_values'] = []  # TODO, add new value into it
        info['origin_values'].append([json_obj.get('value'), json_obj.get('si', -1), json_obj.get('psi', -1), json_obj.get('video'), ip])
        return info

    @staticmethod
    def return_json(current_test_obj):
        HasalServer.storage_handler.save(HasalServer.storage)

        values_list = current_test_obj['origin_values']
        median_value = current_test_obj['median_value']
        mean_value = current_test_obj['mean_value']
        sigma_value = current_test_obj['sigma_value']
        timestamp = current_test_obj['timestamp']
        datestring = Formater.timestamp_to_date_string(timestamp) if timestamp else ''

        _, _, _, video, ip = HasalServer.find_video_ip_by_median(values_list, median_value)

        ret = {
            'median_value': median_value,
            'mean_value': mean_value,
            'sigma_value': sigma_value,
            'current_test_times': len(values_list),
            'video': video,
            'ip': ip,
            'config_test_times': HasalServer._config_test_times,
            'timestamp': timestamp,
            'date': datestring
        }
        return json.dumps(ret)

    def GET(self, os_name, target_browser, test):
        # TODO: this it for checking the result of Hasal Server.
        try:
            # check the url, server/hasal/<os>/<target_browser>/<test>
            assert os_name is not None and os_name != '', '[os] is empty.'
            assert target_browser is not None and target_browser != '', '[target_browser] is empty.'

            if test is None or test == '':
                # return all test result of provided target
                return json.dumps(HasalServer.storage[os_name][target_browser], indent=4)

            if os_name not in HasalServer.storage:
                return 'No os: {}'.format(os_name)
            elif target_browser not in HasalServer.storage[os_name]:
                return 'No target: {}'.format(target_browser)
            elif test not in HasalServer.storage[os_name][target_browser]:
                return 'No test: {}'.format(test)
            else:
                return json.dumps(HasalServer.storage[os_name][target_browser][test], indent=4)
        except AssertionError as e:
            raise web.badrequest(e.message)

    def POST(self, os_name, target, test):
        """
        The input json example:
            json={
            "os": "mac",
            "target": "firefox-36.0.1",
            "test": "test_foo",
            "webappname": "WEB_APP",
            "browser": "firefox",
            "version": "36.0.1",
            "platform": "x86_64",
            "value": 500,
            "si": 1000,
            "psi": 1000,
            "video": "20160701_001.avi",
            "comment": "first test"
            }
        :param os_name: os. ex: 'linux'
        :param target: target. ex: 'firefox 36'
        :param test: test name. ex: 'test_foo'
        :return: the json format string.
            ex: {
                "current_test_times": 3,
                "ip": "127.0.0.1",
                "mean_value": -1,
                "median_value": -1,
                "config_test_times": 5,
                "video": "20160701_001.avi",
                "sigma_value": -1
                }
        """
        try:
            # check the url, server/hasal/<os>/<target_browser>/<test>
            assert os_name is not None and os_name != '', '[os] is empty.'
            assert target is not None and target != '', '[target] is empty.'
            assert test is not None and test != '', '[test] is empty.'

            # get the POST data
            ip = web.ctx.ip
            data = web.data()
            parameters = urlparse.parse_qs(data)
            # check the POST data contain 'json'
            assert 'json' in parameters, 'Can not get "json" parameter from POST data.'

            # check the input json object
            json_obj = json.loads(parameters['json'][0])
            HasalServer.check_input_json(json_obj)

            comment_name = json_obj.get('comment')
            browser_name = json_obj.get('browser')

            # add the os/target/test into storage
            if os_name not in HasalServer.storage:
                HasalServer.storage[os_name] = {}
            if target not in HasalServer.storage[os_name]:
                HasalServer.storage[os_name][target] = {}
            if comment_name not in HasalServer.storage[os_name][target]:
                HasalServer.storage[os_name][target][comment_name] = {}
            if test not in HasalServer.storage[os_name][target][comment_name]:
                HasalServer.storage[os_name][target][comment_name][test] = {}

            if browser_name not in HasalServer.storage[os_name][target][comment_name][test]:
                HasalServer.storage[os_name][target][comment_name][test][browser_name] = {}

                # update the os/target/test result
                current_obj = HasalServer._generate_current_test_obj(json_obj, ip)
                HasalServer.storage[os_name][target][comment_name][test][browser_name] = current_obj
                return HasalServer.return_json(current_obj)
            else:
                current_test_obj = HasalServer.storage[os_name][target][comment_name][test][browser_name]

                # check the test times
                values_list = current_test_obj['origin_values']
                median_value = current_test_obj['median_value']

                if median_value > 0:
                    # already have median value, just return to the client
                    return HasalServer.return_json(current_test_obj)
                else:
                    # add new value into values list
                    values_list.append([json_obj.get('value'), json_obj.get('si', -1), json_obj.get('psi', -1), json_obj.get('video'), ip])
                    if len(values_list) >= HasalServer._config_test_times:
                        # more than 30 times, no median, cal the median and outliers
                        origin_seq = [{'run_time': item[0], 'si': item[1], 'psi': item[2]} for item in values_list]

                        # mean, median, sigma, seq, outliers, si, psi = outlier().detect(seq)
                        mean, median, sigma, _, outliers, si, psi = HasalServer._calculator.detect(origin_seq)
                        current_test_obj['origin_values'] = HasalServer.remove_tuple_from_values(values_list, outliers)
                        values_list = current_test_obj['origin_values']

                        if len(values_list) >= HasalServer._config_test_times:
                            # update the median, mean, and sigma
                            current_test_obj['median_value'] = median
                            current_test_obj['mean_value'] = mean
                            current_test_obj['sigma_value'] = sigma
                            # update SI and PSI
                            current_test_obj['si'] = si
                            current_test_obj['psi'] = psi
                            # add timestamp
                            current_test_obj['timestamp'] = time.time()
                            # return the client
                            return HasalServer.return_json(current_test_obj)
                # Keep going and return the client
                return HasalServer.return_json(current_test_obj)

        except AssertionError as e:
            raise web.badrequest(e.message)


class VideoProfileUpdater:
    """
    Update the video and profile to Hasal server storage.
    """
    _checks = ['os', 'target', 'test', 'browser', 'version', 'comment']
    _keys = ['video_path', 'profile_path']

    def __init__(self):
        HasalServer.storage = HasalServer.storage_handler.load()

    @staticmethod
    def check_input_json(json_obj):
        for item in VideoProfileUpdater._checks:
            assert item in json_obj, 'The json should have "{}" value.'.format(item)

    def POST(self, os_name, target_browser, test):
        """
        The input json example:
            json={
            "os": "mac",
            "target": "firefox-36.0.1",
            "test": "test_foo",
            "comment": "first test",
            "browser": "firefox",
            "version": "36.0.1",
            "video_path": "http://foo.bar/video",
            "profile_path": "http://foo.bar/profile"
            }
        :param os_name: os. ex: 'linux'
        :param target_browser: target. ex: 'firefox 36'
        :param test: test name. ex: 'test_foo'
        :return: OK with 200 code.
        """
        HasalServer.storage = HasalServer.storage_handler.load()
        try:
            # check the url, server/hasal/<os>/<target_browser>/<test>
            assert os_name is not None and os_name != '', '[os] is empty.'
            assert target_browser is not None and target_browser != '', '[target_browser] is empty.'
            assert test is not None and test != '', '[test] is empty.'

            # get the POST data
            # ip = web.ctx.ip
            data = web.data()
            parameters = urlparse.parse_qs(data)
            # check the POST data contain 'json'
            assert 'json' in parameters, 'Can not get "json" parameter from POST data.'

            # check the input json object
            json_obj = json.loads(parameters['json'][0])
            VideoProfileUpdater.check_input_json(json_obj)

            comment_name = json_obj.get('comment')
            browser_name = json_obj.get('browser')

            # check the storage
            assert os_name in HasalServer.storage, \
                'No os [{}] in storage'.format(os_name)
            assert target_browser in HasalServer.storage[os_name], \
                'No target [{}] under os [{}]'.format(target_browser, os_name)
            assert comment_name in HasalServer.storage[os_name][target_browser], \
                'No comment_name [{}] under os [{}], target [{}]'.format(comment_name, os_name, target_browser)
            assert test in HasalServer.storage[os_name][target_browser][comment_name], \
                'No test [{}] under os [{}], target [{}], comment [{}]'.format(test, os_name, target_browser, comment_name)
            assert browser_name in HasalServer.storage[os_name][target_browser][comment_name][test], \
                'No browser [{}] under os [{}], target [{}], comment [{}], test [{}]'.format(
                    browser_name, os_name, target_browser, comment_name, test)

            # Update Video and Profile
            for key in VideoProfileUpdater._keys:
                value = json_obj.get(key, None)
                if value:
                    HasalServer.storage[os_name][target_browser][comment_name][test][browser_name][key] = value

            # Save
            HasalServer.storage_handler.save(HasalServer.storage)

            return 'OK'
        except AssertionError as e:
            raise web.badrequest(e.message)


class Index:
    render = web.template.render('templates', base='layout')

    def GET(self):
        return self.render.readme()


class Reset:
    def GET(self, id):
        StorageHandler().remove()
        return 'Done.'


if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
