
from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import time
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
def extract_posted_date(full_date_string):
    posted_part = full_date_string.split("|")[0]  # Takes "Posted 15 days ago"
    return posted_part.strip()

def parse_relative_date(relative_date):
    """Parse relative date strings into actual dates.
    Handles formats like:
    - "Posted 60+ days ago"
    - "Posted 1 day ago"
    - "Posted 2 weeks ago"
    - "Posted moments ago"
    - "Posted just now"
    """
    # Clean the input string
    relative_date = relative_date.lower().strip()

    # Handle special cases first
    if any(x in relative_date for x in ["moments", "just now", "today", "now"]):
        return datetime.now().date()

    # Extract numeric value (handle "60+" case)
    parts = relative_date.split()
    try:
        num_part = parts[1].replace("+", "")  # Remove '+' if present
        num = int(num_part)
    except (IndexError, ValueError):
        return datetime.now().date()  # Fallback for unexpected formats

    # Get time unit (day/week/hour/etc)
    unit = parts[2] if len(parts) > 2 else ""

    today = datetime.now().date()

    # Calculate date based on unit
    if any(x in unit for x in ["day", "d"]):
        return today - timedelta(days=num)
    elif any(x in unit for x in ["week", "w"]):
        return today - timedelta(weeks=num)
    elif any(x in unit for x in ["month", "m"]):
        return today - timedelta(days=num * 30)  # Approximation
    elif any(x in unit for x in ["year", "y"]):
        return today - timedelta(days=num * 365)  # Approximation
    elif any(x in unit for x in ["hour", "h"]):
        return today
    else:
        return today  # Fallback for unknown units

job_id_lst=[]
title_list=[]
job_link=[]
comp_list = []
location  = []
desc_list = []
date_posted = []
site_lst = []
work_setting_lst = []
salary_lst = []
emp_type_lst = []
skills_lst = []
skills_table = []
# job_description_list = []
salary_list=[]
driver = webdriver.Chrome(options=options)
base_url = "https://www.dice.com/platform/jobs?location=New+York%2C+NY%2C+USA&q=data+engineer&latitude=40.7127753&longitude=-74.0059728&countryCode=US&locationPrecision=City&adminDistrictCode=NY"
driver.get(base_url)
pages = int(driver.find_element(By.CSS_SELECTOR, 'span[class="text-base font-bold leading-normal"]').text)
print(pages)
for page in range(1, pages + 1):
    if page == 1:
        url = base_url
    else:
        url = f"{base_url}&page={page}"
    driver.get(url)
    # continue scraping...

    element = driver.find_element(By.CLASS_NAME,'w-full')
    job_page = element.find_element(By.CSS_SELECTOR, '[class="m-px mx-auto max-w-[1400px] sm:px-6"]')
    jobs = job_page.find_elements(By.CSS_SELECTOR,'[class= "my-4 mx-auto flex h-full w-full items-center"]')
    #print(element.text)
    for job in jobs:
        #Job title
         job_title = job.find_element(By.CLASS_NAME,"self-stretch")
         title_list.append(job_title.text)
        #job link
         job_link.append(job_title.find_element(By.CSS_SELECTOR,"a").get_attribute("href"))



    for i in range(0,2):
        driver.get(job_link[i])
        job_details = driver.find_element(By.ID,"jobdetails")

        comp_list.append(job_details.find_element(By.CSS_SELECTOR,'li[class="job-header_jobDetailFirst__xI_5S job-header_companyName__Mx3ZU text-center font-sans text-base non-italic font-normal md:mr-4 md:text-left md:flex-nowrap"]').text)
        try:
            loc = job_details.find_element(By.CSS_SELECTOR,'li[data-cy="location"]').text
        except:
            loc = None
        location.append(loc)
        # Processing date
        date = job_details.find_element(By.CSS_SELECTOR,'li[data-cy="postedDate"]').text
        date2 = extract_posted_date(date)
        date3 = parse_relative_date(date2)
        date_posted.append(date3)

        #Job overview
        overview = driver.find_element(By.CSS_SELECTOR,'div[class="lg:col-span-8"]')
        # work settings
        try:
            loc_scrap = overview.find_element(By.CSS_SELECTOR,'div[data-cy="locationDetails"]')
            location_modes = loc_scrap.find_elements(By.CSS_SELECTOR,'div[class="chip_chip__cYJs6"]')
            work_setting = ', '.join([mode.text for mode in location_modes])
        except:
            work_setting = None
        work_setting_lst.append(work_setting)
        print(work_setting)
        # Salary
        try:
            pay_scrap = overview.find_element(By.CSS_SELECTOR,'div[data-cy="payDetails"]')
            pay_modes = pay_scrap.find_elements(By.CSS_SELECTOR,'div[class="chip_chip__cYJs6"]')
            pay = ', '.join([mode.text for mode in pay_modes])
            if "Depends" in pay:
                pay = None
        except:
            pay = None
        salary_lst.append(pay)
        print(pay)
        # Employment type
        try:
            emp_scrap = overview.find_element(By.CSS_SELECTOR,'div[data-cy="employmentDetails"]')
            emp_type_modes = emp_scrap.find_elements(By.CSS_SELECTOR,'div[class="chip_chip__cYJs6"]')
            emp_type = ', '.join([mode.text for mode in emp_type_modes])
        except:
            emp_type = None
        print(emp_type)
        emp_type_lst.append(emp_type)
        time.sleep(random.gauss(3, 1))

        # (Optional) Click the "Show N more" button if it exists
        try:
            show_more = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "skillsToggle"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", show_more)
            show_more.click()
            time.sleep(1)  # Allow skills to expand
        except:
            pass  # Button not found — skip gracefully

        # Scrape all skill names

        try:
            skill_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="skillsList"]')
            skills_job_tab = ', '.join([skill_elem.text for skill_elem in skill_elements])
            for elem in skill_elements:
                skills_table.append(elem.text.strip())

        except:
            skills_table = []

        # Example: Print or store
        print(skills_table)
        skills_lst = skills_table


        # (Optional) Click the "Show N more" button if it exists
        try:
            show_more = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "descriptionToggle"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", show_more)
            show_more.click()
            time.sleep(1)  # Allow skills to expand
        except:
            pass  # Button not found — skip gracefully
        desc_html = driver.find_element(By.ID , "jobDescription")
        desc = desc_html.find_element(By.CSS_SELECTOR, 'div[data-testid ="jobDescriptionHtml"]').text
        desc_list.append(desc)
        time.sleep(random.gauss(3, 1))  # Bell curve around 3±1 seconds
    print(desc_list[0])
    time.sleep(random.gauss(3, 1))
driver.quit()