# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import gdoc

com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

ff.clickBar()
ff.enterLink(sys.argv[3])
sleep(5)
gd.wait_for_loaded()
gd.insert_image_url("https://drive.google.com/file/d/0B9Zi9TqbRWsdM0owSVlmbkRpUFE/view?usp=sharing")
sleep(5)
type(Key.ENTER)
type(Key.ENTER)
sleep(3)
gd.insert_image_url("https://drive.google.com/file/d/0B9Zi9TqbRWsdd2k4aFNreWFKaFU/view?usp=sharing")
sleep(5)
type(Key.ENTER)
type(Key.ENTER)
sleep(5)