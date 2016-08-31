# Go to homepage
wait("chrome_url_bar.png")
paste("chrome_url_bar.png", "http://www.bbc.com/")
type(Key.ENTER)
wait(5)

# Pagedown 10 time
for i in range(10):
    type(Key.PAGE_DOWN)
    wait(1)
