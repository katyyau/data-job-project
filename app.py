import pandas as pd
from datetime import date
from datetime import datetime
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from google.cloud import storage
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('double-genius-331713-53d701549c5b.json',
    scopes=["https://www.googleapis.com/auth/cloud-platform"])

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage')

s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=chrome_options)

# Land the first page
driver.get("https://www.glassdoor.com/Job/data-jobs-SRCH_KO0,4.htm")

job_details_list_master = []
# Scrape the job details as a function
def scrape_data():

    data_id = driver.find_element(By.CSS_SELECTOR, ".css-1ctl34j[data-id]").get_attribute("data-id")
    employer_name = driver.find_element(By.CSS_SELECTOR, ".css-xuk5ye").get_attribute("textContent").split(".")[0]
    job_title = driver.find_element(By.CSS_SELECTOR, ".css-1j389vi").get_attribute("textContent")
    work_location = driver.find_element(By.CSS_SELECTOR, ".css-56kyx5").get_attribute("textContent")
    job_description = driver.find_element(By.CSS_SELECTOR, ".jobDescriptionContent").get_attribute("textContent")

    company_overview_dict = {}
    for company_overview_item in driver.find_elements(By.CSS_SELECTOR, "#EmpBasicInfo .css-daag8o"):
        spans = company_overview_item.find_elements(By.CSS_SELECTOR, "span")
        key = spans[0].get_attribute("textContent")
        value = spans[1].get_attribute("textContent")
        company_overview_dict[key] = value
    company_overview_json = json.dumps(company_overview_dict)

    scrapped_date = date.today()

    return [data_id, employer_name, job_title, work_location, job_description, company_overview_json, scrapped_date]

i = 1
while True:
    # Get the job list
    job_list = driver.find_elements(By.CSS_SELECTOR, "ul[data-test='jlGrid'] li")

    # Scrape a page
    for job in job_list:

        # To close the button if exists
        close_buttons = driver.find_elements(By.CSS_SELECTOR, "[alt='Close']")
        for close_button in close_buttons:
            close_button.click()

        # Click job card
        job.click()
        time.sleep(2)
        try:
            job_details_list = scrape_data()
            # Append new list to summary list
            job_details_list_master.append(job_details_list)
        except:
            print('Failed to scrape')

    # Check if it is at the last page
    last_page = driver.find_element(By.CSS_SELECTOR, "#FooterPageNav li:last-child")
    last_page_att = last_page.get_attribute("disabled")
    if type(last_page_att) == str:
        break
    else:
        current_page_number = driver.find_element(By.CSS_SELECTOR, "[data-test='page-x-of-y']").text.split(" ")[1]
        next_page_button = driver.find_element(By.CSS_SELECTOR, "[data-test='pagination-next']")
        next_page_button.click()

        # Check if really jumped to next page
        while True:
            current_page_number_update = driver.find_element(By.CSS_SELECTOR, "[data-test='page-x-of-y']").text.split(" ")[1]

            if current_page_number != current_page_number_update:
                break
            else:
                time.sleep(1)

    # Create a dataframe and save as csv
    datetimestr = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_name = "job_details_list_master_" + datetimestr + "_p" + str(i) + ".csv"
    pd.DataFrame(job_details_list_master).to_csv(csv_name, index=False)

    # Upload csv to cloud storage
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket("daily-job-details-list-master")
    blob = bucket.blob("daily-job-details-list-master/"+ csv_name)
    blob.upload_from_filename(csv_name)

    i += 1
