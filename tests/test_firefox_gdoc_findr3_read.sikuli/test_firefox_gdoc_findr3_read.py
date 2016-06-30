# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import gdoc

com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()
keyword = "OLD"

ff.clickBar()
ff.enterLink(sys.argv[3])
sleep(5)
gd.wait_for_loaded()

sleep(5)
type("h", Key.CTRL)
wait(Pattern("FindAndReplace.png").similar(0.50))
click(Pattern("FindReplaceInput.png").similar(0.50).targetOffset(98,-21))
type(keyword)
click(Pattern("FindReplaceInput.png").similar(0.50).targetOffset(98,26))
type("NEW")

for i in range(15):
    wait(Pattern("Replace.png").similar(0.80))
    click(Pattern("Replace.png").similar(0.80))

sleep(2)
gd.deFoucsContentWindow()

