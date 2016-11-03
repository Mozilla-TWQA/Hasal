import shutil
from urlparse import urlparse


current_path = sys.argv[1]
link = sys.argv[2]
browser = sys.argv[3].lower()
x = int(sys.argv[4])
y = int(sys.argv[5])
platform = sys.argv[6].lower()

S_KEY = Key.CTRL
if 'darwin' == platform:
    S_KEY = Key.CMD
elif 'win32' == platform or 'linux2' == platform:
    S_KEY == Key.CTRL

urlbar_pic = 'ff_urlbar.png'
if 'firefox' == browser:
    urlbar_pic = 'ff_urlbar.png'
elif 'chrome' == browser:
    urlbar_pic = 'ch_urlbar.png'

hasal_path = os.path.abspath(os.path.join(current_path, '..'))
hasal_lib_path = os.path.abspath(os.path.join(hasal_path, 'lib', 'sikuli'))

link_domain = urlparse(link if link.startswith('http') else 'http://{}'.format(link)).netloc
link_domain_str = link_domain.replace('.', '_').replace(':', '_')

sys.path.append(hasal_lib_path)

import common

com = common.General()

wait(Pattern(urlbar_pic), 60)
click(Pattern(urlbar_pic).targetOffset(-120,0))
type("a", S_KEY)
sleep(1)

paste(link)
type(Key.ENTER)
sleep(20)

pic_path = capture(x, y, 25, 25)
shutil.move(pic_path, os.path.join(current_path, '{}.png'.format(link_domain_str)))
