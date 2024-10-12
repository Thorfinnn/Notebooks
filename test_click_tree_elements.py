import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class Node:
    def __init__(self, element, text=None, children=None):
        self.tag_name = element.tag_name
        self.text = element.text
        self.children = children if children is not None else []
        self.element = element

    def add_child(self, node):
        self.children.append(node)

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

# define a recursive function to filter the tree based on the specified tags
def filter_tree(node, tags):
    # if the node is a leaf node, return None if its tag is not in the specified tags
    if node.is_leaf():
        if node.tag_name not in tags:
            return None
        else:
            return node

    # filter the children nodes recursively
    children = []
    for child in node.children:
        filtered_child = filter_tree(child, tags)
        if filtered_child is not None:
            children.append(filtered_child)

    # if all children nodes were filtered out, return None
    if not children:
        return None

    # create a new node with the filtered children nodes
    return Node( node.element, children)


# define the test case class
class ClickTreeElementsTestCase(unittest.TestCase):
    def setUp(self):
        # initialize the web driver
        self.driver = webdriver.Chrome()

        # load the web page and wait for it to load completely
        self.driver.get('https://www.lambdatest.com/')
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'header')))

        # get the root node of the DOM tree
        root_element = self.driver.find_element(By.TAG_NAME, 'header')

        # build the tree data structure from the root element
        self.root_node = build_tree(root_element)

        # filter the tree to only preserve the branches with leaf nodes as 'a' and 'button' tags
        # self.root_node = filter_tree(self.root_node, ['a', 'button'])
    def tearDown(self):
        # quit the web driver
        self.driver.quit()

    def test_click_tree_elements(self):
        test_logs = []
        # define a recursive function to click on each element in the tree
        # def click_tree_elements(node):
        #     # if the node is a leaf node, click on it
        #     if node.is_leaf():
        #         # check if the element is hidden
        #         is_hidden = self.driver.execute_script(
        #             'return window.getComputedStyle(arguments[0]).display === "none";',
        #             node.element)
        #         if not is_hidden:
        #             for i in range(100):
        #                 node.element.click()
        #                 print(self.driver.get_log('browser'))
        #                 # do something with the test logs
        #         return
        tree = {'a': [{'a': [{'a': []}]}, {'button': []}]}
        def click_element(element):
            try:
                element.click()
                test_logs.append(self.driver.get_log('browser'))
            except:
                pass
                # click on the children nodes recursively
                for child in node.children:
                    click_tree_elements(child)
        def traverse_tree(tree):
            for tag in tree:
                elements = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, tag)))
                for element in elements:
                    if tag == 'a':
                        link = element.get_attribute('href')
                        if link:
                            self.driver.execute_script("window.open('{}', '_blank');".format(link))
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            click_element(element)
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                        else:
                            click_element(element)
                    else:
                        click_element(element)
                    if tree[tag]:
                        traverse_tree(tree[tag][0])
        # click on each element in the tree
        # click_tree_elements(self.root_node)
        traverse_tree(tree)

        # Write logs to external file
        with open('test_logs.json', 'w') as f:
            json.dump(test_logs, f, indent=4)

        # Calculate and print log statistics
        total_logs = sum([len(logs) for logs in test_logs])
        print('Total logs:', total_logs)

        mime_types = {}
        for logs in test_logs:
            for log in logs:
                mime_type = log['mimeType']
                if mime_type in mime_types:
                    mime_types[mime_type] += 1
                else:
                    mime_types[mime_type] = 1

        print('Logs count by mime-type:')
        for mime_type, count in mime_types.items():
            print('{}: {}'.format(mime_type, count))

        log_levels = {}
        for logs in test_logs:
            for log in logs:
                level = log['level']
                if level in log_levels:
                    log_levels[level] += 1
                else:
                    log_levels[level] = 1

        print('Logs count by log level:')
        for level, count in log_levels.items():
            print('{}: {}'.format(level, count))
            
# run the test case
if __name__ == '__main__':
    unittest.main()

