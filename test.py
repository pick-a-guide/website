import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_search(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8080")
        self.assertIn("Pick-a-Guide", driver.title)
        driver.get("http://127.0.0.1:8080/escolhaInicioSessao")
        driver.get("http://127.0.0.1:8080/iniciarSessaoGuia")
        assert "No results found." not in driver.page_source
    
    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
