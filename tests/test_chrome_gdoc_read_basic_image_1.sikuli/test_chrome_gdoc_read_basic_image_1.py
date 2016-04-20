# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import gdoc

com = common.General()
chrome = browser.Chrome()
gd = gdoc.gDoc()

chrome.clickBar()
chrome.enterLink(sys.argv[3])

gdoc.deFoucsContentWindow()