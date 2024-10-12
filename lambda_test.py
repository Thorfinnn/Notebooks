import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Node:
    def __init__(self, element, text=None, children=None):
        self.tag_name = element.tag_name
        self.text = element.text
        self.children = children if children is not None else []
        self.element = element
        self.link = element.get_attribute('href') if self.tag_name == 'a' else None
        self.parent = False

    def add_child(self, node):
        self.children.append(node)
        if node.tag_name == 'a':
            self.parent = True

    def is_leaf(self):
        return not self.children

    def to_dict(self):
        return {
            'tag_name': self.tag_name,
            'text': self.text,
            'children': [child.to_dict() for child in self.children]
        }
    
def build_tree(element):
    # create a node for the current element
    node = Node(element)

    # get the children elements of the current element
    children = element.find_elements(By.XPATH, '*')

    # recursively build the tree for each child element
    for child in children:
        child_node = build_tree(child)
        node.add_child(child_node)

    return node

def update_tree(driver, node):
    if node.tag_name == 'a':
        node.element = driver.find_element(By.LINK_TEXT, node.link)
    if node.tag_name == 'button':
        node.element = driver.find_element(By.XPATH, f"//button[text()='{node.text}']")
    for child in node.children:
        update_tree(driver, child)

class LambdaTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.maximize_window()

    def test_lambda_test(self):
        self.driver.get("https://www.lambdatest.com/")
        time.sleep(5)
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'header')))

        # get the root node of the DOM tree
        headers = self.driver.find_element(By.TAG_NAME, 'header')
        headers_tree = build_tree(headers)
        def click_element(node):
                    # def click_element(element):
            try:
                print(node.tag_name)
                if node.tag_name == 'button' or node.parent:
                    # if node.element.get_attribute('href')!= None:
                    self.driver.execute_script("arguments[0].target = '_blank'",node.element)
                    node.element.click()
                    # headers = self.driver.find_element(By.TAG_NAME, 'header')
                    headers_tree = update_tree(self.driver,headers)                    
                    
                    # node.element.click()
                    self.driver.switch_to.window(self.driver.window_handles[-1])

                    # do something in the new tab, e.g. record network logs
                    logs = self.driver.get_log("browser")
                    # log_count = len(logs)
                    # log_types = {}
                    # log_levels = {}
                    # for log in logs:
                    #     log_type = log['mimeType']
                    #     log_level = log['level']
                    #     if log_type in log_types:
                    #         log_types[log_type] += 1
                    #     else:
                    #         log_types[log_type] = 1
                    #     if log_level in log_levels:
                    #         log_levels[log_level] += 1
                    #     else:
                    #         log_levels[log_level] = 1
                    # store network logs to local machine
                    with open("network_logs.txt", "a") as f:
                        f.write(str(logs) + "\n")
                    # close the new tab
                    self.driver.close()

                    # switch back to the original tab
                    self.driver.switch_to.window(self.driver.window_handles[0])
                # node.element.click()
                # # test_logs.append(self.driver.get_log('browser'))
                # logs = self.driver.get_log("browser")

            except Exception as e:
                print(e)
                # click on the children nodes recursively
            for child in node.children:
                click_element(child)
             
        click_element(headers_tree)
        # try:
        #     headers_tree.element.click()
        # except:
        #     pass
        # # headers = self.driver.find_elements(By.XPATH,"//nav[@class='navbar navbar-expand-lg navbar-light']/ul/li/a")
        # print(headers)
        # for header in headers_tree.children:
        #     try:
        #         test
        #     except:
        #         pass


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(LambdaTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
