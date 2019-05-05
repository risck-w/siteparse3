from selenium import webdriver
from selenium.webdriver import ChromeOptions
import settings as sp


class CreateWebDriver(object):
    def __init__(self):
        self.web_driver = None

    @property
    def get_driver(self):
        if self.web_driver:
            return self.web_driver

        # 设置debug模式
        options = None
        if sp.debug is False:
            options = ChromeOptions()
            options.add_argument("--headless")

        self.web_driver = webdriver.Chrome(chrome_options=options)
        return self.web_driver

