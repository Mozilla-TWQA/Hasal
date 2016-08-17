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

sleep(3)
for i in range(3):
    type("n", Key.CTRL+Key.ALT)
    sleep(0.3)
    type("h", Key.CTRL+Key.ALT)
    sleep(0.3)
    type(Key.DOWN, Key.SHIFT)
    sleep(0.3)
    type("b", Key.CTRL)
    sleep(0.3)
    type("n", Key.CTRL+Key.ALT)
    sleep(0.3)
    type("h", Key.CTRL+Key.ALT)
    sleep(0.3)
    type(Key.DOWN, Key.SHIFT)
    sleep(0.3)
    type("8", Key.CTRL+Key.SHIFT)
    sleep(0.3)

type("n", Key.CTRL+Key.ALT)
sleep(0.3)
type("h", Key.CTRL+Key.ALT)
sleep(0.3)
type(Key.DOWN, Key.SHIFT)
sleep(0.3)
type(".", Key.CTRL+Key.SHIFT)
sleep(0.3)

sleep(2)
gd.deFoucsContentWindow()

