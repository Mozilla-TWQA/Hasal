import json
import os


current_path = sys.argv[1]
browser = sys.argv[2].lower()
platform = sys.argv[3].lower()

# Set up Super Key
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

tabicon_pic = 'tab_icon.png'

is_found = False
for urlbar_pic in urlbar_pics:
    if exists(Pattern(urlbar_pic), 60):
        is_found = True
        click(Pattern(urlbar_pic).targetOffset(-120,0))
        type("a", S_KEY)
        sleep(1)
        break
if not is_found:
    raise Exception('Cannot found URL bar. Ref images: {}'.format(urlbar_pics))

paste('firefox.com')
type(Key.ENTER)
sleep(10)

json_path = os.path.join(current_path, 'tab_xy.json')

wait(Pattern(tabicon_pic).similar(0.90).targetOffset(-12,-10), 60)
tab_icon = find(Pattern(tabicon_pic).similar(0.90).targetOffset(-12,-10))

x = tab_icon.getTarget().getX()
y = tab_icon.getTarget().getY()

ret = {'x': x, 'y': y}

fs = open(json_path, "w")
fs.write(json.dumps(ret))
fs.close()
