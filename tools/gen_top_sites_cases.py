import os
import sys
import json
import time
import shutil
from urlparse import urlparse

from lib.sikuli import Sikuli
from lib.browser.chrome import BrowserChrome
from lib.browser.firefox import BrowserFirefox
from lib.helper import desktopHelper


DEFAULT_BROWSER_WIDTH = 1200
DEFAULT_BROWSER_HEIGHT = 980

links = [
    'https://www.google.com/search?q=flowers',
    'https://www.facebook.com/cnn'
]

platform = sys.platform
current_file_path = os.path.dirname(os.path.realpath(__file__))
hasal_path = os.path.abspath(os.path.join(current_file_path, '..'))
sikuli_exec_path = os.path.abspath(os.path.join(current_file_path, '..', 'thirdParty', 'runsikulix'))
top_sites_cases_path = os.path.join(hasal_path, 'tests', 'regression', 'topsites')

print('##################################')
print('#  Generate the Top Sites Cases  #')
print('##################################\n...')

# Create top sites cases folder
if not os.path.exists(top_sites_cases_path):
    os.makedirs(top_sites_cases_path)
with open(os.path.join(top_sites_cases_path, '__init__.py'), 'w') as initf:
    initf.write('')

# init Sikuli runner
runner = Sikuli(sikuli_exec_path, hasal_path)

"""
Firefox Part
"""
# Launch Firefox
browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
browser_obj.launch()

print('##############################')
print('#                            #')
print('#  Please focus on Firefox   #')
print('#                            #')
print('##############################')
raw_input("Press Enter to continue...")
time.sleep(5)
desktopHelper.lock_window_pos(desktopHelper.DEFAULT_BROWSER_TYPE_FIREFOX)

# Get Tab location
print('### [F] Getting the Tab Icon Location ...')
script_path = os.path.join(current_file_path, 'get_tab_icon.sikuli')
params = [current_file_path, 'firefox', platform]
runner.run_sikulix_cmd(script_path, args_list=params)

# Load Tab location from file
xy_json_file = os.path.join(current_file_path, 'tab_xy.json')
xy = {'x': 0, 'y': 0}
with open(xy_json_file) as xy_f:
    xy = json.load(xy_f)
x = xy.get('x')
y = xy.get('y')
os.remove(xy_json_file)
print('### [F] Loading the Tab location X: {} Y: {}'.format(x, y))

# Generate the Firefox cases
script_path = os.path.join(current_file_path, 'create_top_sites_tests.sikuli')
for link in links:
    print('### [F] Generate for: {}'.format(link))

    link_domain = urlparse(link if link.startswith('http') else 'http://{}'.format(link)).netloc
    link_domain_str = link_domain.replace('.', '_').replace(':', '_')
    case_name = 'test_firefox_topsites_{}_launch'.format(link_domain_str)
    case_py_file = os.path.join(top_sites_cases_path, '{}.py'.format(case_name))
    case_sikuli_path = os.path.join(top_sites_cases_path, '{}.sikuli'.format(case_name))
    case_sikuli_file = os.path.join(case_sikuli_path, '{}.py'.format(case_name))

    if not os.path.exists(case_sikuli_path):
        os.makedirs(case_sikuli_path)
    if not os.path.exists(case_sikuli_path):
        os.makedirs(case_sikuli_path)

    # Run script to get the tab pic
    params = [current_file_path, link, 'firefox', str(x), str(y), platform]
    runner.run_sikulix_cmd(script_path, args_list=params)

    # Get the tab pic, from current_file_path to cases' folder
    shutil.move(os.path.join(current_file_path, '{}.png'.format(link_domain_str)), os.path.join(case_sikuli_path, '{}.png'.format(link_domain_str)))

    with open(case_py_file, 'w') as pyf:
        pyf.write("""
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def {}(self):
        self.sikuli_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target="{}", script_dp=self.env.test_script_py_dp)

""".format(case_name, link))

    with open(case_sikuli_file, 'w') as spyf:
        spyf.write("""
sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ff = browser.Firefox()

ff.clickBar()
ff.enterLink(sys.argv[3])

sleep(2)
wait(Pattern('{}.png'), 60)
""".format(link_domain_str))


print('##############################')
print('#                            #')
print('#  Please CLOSE the Firefox  #')
print('#                            #')
print('##############################')
raw_input("Press Enter to continue...")


"""
Chrome Part
"""
#browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
