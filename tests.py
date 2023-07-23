from selenium import webdriver

driver = webdriver.Chrome()

print(driver.session_id)