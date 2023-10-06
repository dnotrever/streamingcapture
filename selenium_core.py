from time import sleep
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class SeleniumCore:
    
    def __init__(self):
        self.driver = None

    def set_driver(self):
        self.driver = self.get_driver()
    
    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--lang=pt-br')
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver
    
    def get(self, url):
        self.driver.get(url)
        
    def refresh(self):
        self.driver.refresh()
        
    def quit(self):
        self.driver.quit()

    def close(self):
        self.driver.close()
    
    def element(self, by_mode, element, presence='one', driver='', timeout=30):

        by_mode_mapping = {
            'xpath': By.XPATH,
            'selector': By.CSS_SELECTOR,
            'tag': By.TAG_NAME,
            'name': By.NAME,
            'id': By.ID,
            'class': By.CLASS_NAME,
        }
                
        if by_mode in by_mode_mapping:
            by_mode = by_mode_mapping[by_mode]

        presence_mapping = {
            'one': EC.presence_of_element_located((by_mode, element)),
            'all': EC.presence_of_all_elements_located((by_mode, element)),
        }

        if presence in presence_mapping:
            presence = presence_mapping[presence]

        driver = self.driver if not driver else driver

        return WebDriverWait(driver, timeout).until(presence)
    
    def click(self, by_mode, element, option=''):
        
        if type(element) == str:
            if option == 'double':
                return ActionChains(self.driver).double_click(self.element(by_mode, element)).perform()
            else:
                return self.driver.execute_script('arguments[0].click();', self.element(by_mode, element))
        else:
            if option == 'double':
                return ActionChains(self.driver).double_click(element).perform()
            else:
                return self.driver.execute_script('arguments[0].click();', element)
  
    def action(self, key):

        sleep(1)

        key_mapping = {
            'enter': Keys.ENTER,
            'esc': Keys.ESCAPE,
            'tab': Keys.TAB,
            'backspace': Keys.BACKSPACE,
            'end': Keys.END,
        }

        if key in key_mapping:
            key = key_mapping[key]

        return ActionChains(self.driver).send_keys(key).perform()

    def tab(self, index, mode='create'):
        
        if index == 'count':
            return len(self.driver.window_handles)
        
        if mode == 'create':
            self.driver.execute_script('window.open("");')
            
        return self.driver.switch_to.window(self.driver.window_handles[index])

    def alert(self, value):
        alert = self.driver.switch_to.alert
        if value == 'accept':
            return alert.accept()

    def current_url(self):
        return self.driver.current_url

sc = SeleniumCore()