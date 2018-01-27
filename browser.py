from selenium import webdriver

class Browser():
    def __init__(self):
        print('starting browser')
        self.browser = webdriver.Chrome("chromedriver")

    def closeBrowser(self):
        print('closing browser')
        self.browser.quit()
        print('closed')

    def getPage(self, url):
        print('getting page')
        self.browser.get(url)

    def findByXpath(self, xPath):
        return self.browser.find_elements_by_xpath(xPath)
