# Go to homepage
wait("firefox_url_bar.png")
paste("firefox_url_bar.png", "http://www.bbc.com/")
type(Key.ENTER)
wait(5)

current_timeout = getAutoWaitTimeout()
setAutoWaitTimeout(20)

# Wait for search bar
wait("search.png")
click("search.png")
type("This is great!!")

setAutoWaitTimeout(current_timeout)
