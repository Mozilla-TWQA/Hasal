
sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ff = browser.Firefox()

ff.clickBar()
ff.enterLink(sys.argv[3])

sleep(2)
wait(Pattern('www_amazon_com.png').similar(0.80), 60)

icon_loc = wait(Pattern('www_amazon_com.png').similar(0.80), 60).getTarget()
x_offset = 0
y_offset = 150
inside_window = Location(icon_loc.getX() + x_offset, icon_loc.getY() + y_offset)

mouseMove(inside_window)
ff.scroll_down(100)
mouseMove(Location(0, 0))
