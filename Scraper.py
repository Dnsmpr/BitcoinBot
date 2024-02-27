import time

from selenium import webdriver
from selenium.webdriver.common.by import By


class Scaper:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)

    def get_running_nodes(self) -> int:

        self.driver.get("https://luke.dashjr.org/programs/bitcoin/files/charts/software.html")
        time.sleep(5)

        child_divs = self.driver.find_elements(By.XPATH, ".//div")

        text = [child.text for child in child_divs if child.text != ""]
        node_count = sum(set([int(value.split(" ")[0]) for value in text]))

        return node_count
