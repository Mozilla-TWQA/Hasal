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
sleep(5)
gd.wait_for_loaded()
gd.insert_image_url("https://drive.google.com/open?id=0B9Zi9TqbRWsdTV9JTmZQUXRFTWM")
sleep(5)
com.select_all()
sleep(1)
com.cut()
sleep(1)
com.paste()
sleep(1)
type(Key.ENTER)
type(Key.ENTER)
com.select_all() 
sleep(1)
com.copy()
sleep(1)
type(Key.RIGHT)
sleep(1)
com.paste()
sleep(1)
gd.deFoucsContentWindow()
