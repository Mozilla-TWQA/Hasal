sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
chrome = browser.Chrome()
gd = gdoc.gDoc()
keyword = "FORMAT10"

chrome.clickBar()
chrome.enterLink(sys.argv[3])

gd.wait_for_loaded()
wait(5)

for i in range(3):
    # Create 1 page of content with keyword in it & Make the last line bold
    gd.page_text_generate(keyword, 1)
    sleep(0.3)
    type(Key.UP)
    sleep(0.3)
    type(Key.UP, Key.SHIFT)
    sleep(0.3)
    type("b", Key.CTRL)
    sleep(0.3)
    type(Key.END, Key.CTRL)

    # Insert 1 image and go to next page
    sleep(5)
    gd.insert_image_url("https://drive.google.com/file/d/0B9Zi9TqbRWsdM0owSVlmbkRpUFE/view")
    sleep(5)
    type(Key.ENTER)
    type(Key.ENTER)
    sleep(5)
    type(Key.ENTER, Key.CTRL)

    # Create 1 page of content with keyword in it & Make the last line bulleted list
    gd.page_text_generate(keyword, 1)
    sleep(0.3)
    type(Key.UP)
    sleep(0.3)
    type(Key.UP, Key.SHIFT)
    sleep(0.3)
    type("8", Key.CTRL+Key.SHIFT)
    sleep(0.3)
    type(Key.END, Key.CTRL)

    # Create 20*20 table and go to next page
    sleep(1)
    gd.create_table(20,20)
    sleep(6)
    type(Key.END, Key.CTRL)
    sleep(0.3)
    type(Key.ENTER, Key.CTRL)

# Create 1 page of content with keyword in it & Make the last line bold
gd.page_text_generate(keyword, 1)
sleep(0.3)
type(Key.UP)
sleep(0.3)
type(Key.UP, Key.SHIFT)
for i in range(6):
    sleep(0.3)
    type(".", Key.CTRL+Key.SHIFT)
sleep(0.3)
type(Key.END, Key.CTRL)

sleep(2)
gd.deFoucsContentWindow()
