sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
chrome = browser.Chrome()
gd = gdoc.gDoc()

chrome.clickBar()
chrome.enterLink(sys.argv[3])

gd.wait_for_loaded()

for i in range(3):
    wait(0.5)
    type(Key.PAGE_DOWN)

sleep(2)
gd.deFoucsContentWindow()
