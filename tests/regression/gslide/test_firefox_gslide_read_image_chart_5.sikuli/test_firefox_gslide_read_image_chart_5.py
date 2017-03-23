# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import gslide

com = common.General()
ff = browser.Firefox()
gs = gslide.gSlide('ff')

ff.clickBar()
ff.enterLink(sys.argv[3])
setAutoWaitTimeout(10)

sleep(2)
gs.wait_for_loaded()
wait(gs.image_chart_list)

type(Key.PAGE_DOWN)
sleep(1)
wait(gs.image_chart_list_page_2)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.image_chart_list_page_3)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.image_chart_list_page_4)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.image_chart_list_page_end)
