# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
import browser
import common


com = common.General()
ff = browser.Firefox()

ff.clickBar()
ff.enterLink("https://goo.gl/SEpp2A?hl=en")