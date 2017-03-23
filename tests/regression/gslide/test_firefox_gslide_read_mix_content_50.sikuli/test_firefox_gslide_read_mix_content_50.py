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
wait(gs.mix_content_50_list_original)

type(Key.PAGE_DOWN)
sleep(1)
wait(gs.list_page_2)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.list_page_3)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.list_page_4)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.list_page_5)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.list_page_6)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.list_page_7)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.list_page_8)
type(Key.PAGE_DOWN)
sleep(1)
wait(gs.list_page_9)
type(Key.END)
sleep(1)
wait(gs.mix_content_50_list_final)
