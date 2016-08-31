# Go to homepage
wait("chrome_url_bar.png")
paste("chrome_url_bar.png", "http://www.bbc.com/")
type(Key.ENTER)
wait(5)

current_timeout = getAutoWaitTimeout()
setAutoWaitTimeout(20)

# Wait for search bar
wait("search.png")
click("search.png")
type("This is great!!")

setAutoWaitTimeout(current_timeout)
