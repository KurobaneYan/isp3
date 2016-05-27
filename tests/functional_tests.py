import unittest

from selenium import webdriver


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_open_main_page(self):
        self.browser.get('http://localhost:8000')
        self.assertIn('Lab', self.browser.title)
        self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main()
