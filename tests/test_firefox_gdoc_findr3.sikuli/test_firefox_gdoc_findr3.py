sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

ff.clickBar()
ff.enterLink(sys.argv[3])

gd.wait_for_loaded()

wait(Pattern("EditDropdown.png").similar(0.85))
wait(5)

keyword = "OLD"
gd.page_text_generate(keyword, 1)

sleep(5)
gd.wait_for_loaded()
gd.insert_image_url("https://drive.google.com/file/d/0B9Zi9TqbRWsdM0owSVlmbkRpUFE/view?usp=sharing")
sleep(5)
type(Key.ENTER)
type(Key.ENTER)
sleep(5)
type(Key.ENTER, Key.CTRL)

gd.page_text_generate(keyword, 1)

sleep(5)
gd.wait_for_loaded()
gd.insert_image_url("https://drive.google.com/file/d/0B9Zi9TqbRWsdM0owSVlmbkRpUFE/view?usp=sharing")
sleep(5)
type(Key.ENTER)
type(Key.ENTER)
sleep(5)
type(Key.ENTER, Key.CTRL)


type("h", Key.CTRL)
wait(Pattern("FindAndReplace.png").similar(0.85))
click(Pattern("FindReplaceInput.png").similar(0.85).targetOffset(98,-21))
type(keyword)
click(Pattern("FindReplaceInput.png").similar(0.85).targetOffset(98,26))
type("NEW")

for i in range(15):
    wait(Pattern("Replace.png").similar(0.90))
    click(Pattern("Replace.png").similar(0.90))
