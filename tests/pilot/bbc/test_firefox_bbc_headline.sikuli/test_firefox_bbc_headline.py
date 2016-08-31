# Go to homepage
wait("firefox_url_bar.png")
paste("firefox_url_bar.png", "http://www.bbc.com/")
type(Key.ENTER)
wait(2)

# Click the headline
wait("BBC.png")
click(Pattern("BBC.png").targetOffset(144,218))
wait(2)
