from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--lang=en')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def get_wait(driver, timeout=30):
    wait = WebDriverWait(driver, timeout)
    return wait

def get_actions(driver):
    actions = ActionChains(driver)
    return actions

def clickable(element):
    return EC.element_to_be_clickable(element)

def located(element):
    return EC.presence_of_element_located(element)

def all_located(element):
    return EC.presence_of_all_elements_located(element)

