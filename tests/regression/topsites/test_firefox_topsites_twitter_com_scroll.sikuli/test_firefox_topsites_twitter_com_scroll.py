
sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ff = browser.Firefox()

ff.enterLink(sys.argv[3])

sleep(2)
wait(Pattern('twitter_com.png').similar(0.80), 60)

icon_loc = wait(Pattern('twitter_com.png').similar(0.80), 60).getTarget()
x_offset = 0
y_offset = 150
inside_window = Location(icon_loc.getX() + x_offset, icon_loc.getY() + y_offset)

mouseMove(inside_window)
ff.scroll_down(100)
