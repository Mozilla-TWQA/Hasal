sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
chrome = browser.Chrome()
gd = gdoc.gDoc()

chrome.clickBar()
chrome.enterLink(sys.argv[3])
chrome.focus()

gd.wait_for_loaded()

sleep(3)
type(Key.END, Key.CTRL)

sleep(2)
gd.deFoucsContentWindow()
