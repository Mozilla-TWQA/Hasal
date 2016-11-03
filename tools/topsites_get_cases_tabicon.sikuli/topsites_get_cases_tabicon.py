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

# Set up URL bar pic
urlbar_pics = ['ff_urlbar.png']
if 'firefox' == browser:
    urlbar_pics = ['ff_urlbar.png']
elif 'chrome' == browser:
    urlbar_pics = ['ch_urlbar.png', 'ch_urlbar_52.png']

hasal_path = os.path.abspath(os.path.join(current_path, '..'))
hasal_lib_path = os.path.abspath(os.path.join(hasal_path, 'lib', 'sikuli'))

link_domain = urlparse(link if link.startswith('http') else 'http://{}'.format(link)).netloc
link_domain_str = link_domain.replace('.', '_').replace(':', '_')

sys.path.append(hasal_lib_path)

import common

com = common.General()

is_found = False
for urlbar_pic in urlbar_pics:
    if exists(Pattern(urlbar_pic).similar(0.70), 60):
        is_found = True
        click(Pattern(urlbar_pic).similar(0.70).targetOffset(-120,0))
        type("a", S_KEY)
        sleep(1)
        break
if not is_found:
    raise Exception('Cannot found URL bar. Ref images: {}'.format(urlbar_pics))

paste(link)
type(Key.ENTER)
sleep(20)

pic_path = capture(x, y, 25, 25)
shutil.move(pic_path, os.path.join(current_path, '{}.png'.format(link_domain_str)))
