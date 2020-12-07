from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class SeleniumConnector:

    def __init__(self, url, options=None):
        if options is None:
            options = []

        self.options = options
        self.url = url

    def get_html(self):
        options_obj = Options()
        for option in self.options:
            options_obj.add_argument(option)
        driver = webdriver.Chrome(options=options_obj)
        driver.get(self.url)
        html = driver.page_source
        driver.quit()
        return html
