from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

driver.get("https://www.welcometothejungle.com/en/jobs?query=data%20analyst&page=1&aroundQuery=worldwide")
element = driver.find_element(By.ID,'header')
# jobs = element.find_elements(By.TAG_NAME,'href')

print(element.text)
# for job in jobs:
#     print(job.text)
element.click()

print(driver.current_url)

driver.quit()
