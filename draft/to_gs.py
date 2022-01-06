from datetime import datetime
import pandas as pd


from google.cloud import storage
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('double-genius-331713-53d701549c5b.json', scopes=[
    "https://www.googleapis.com/auth/cloud-platform"])

job_details_list_master = [["data_id", "employer_name", "job_title", "work_location", "job_description", "company_overview_json", "scrapped_date"], ["data_id", "employer_name", "job_title", "work_location", "job_description", "company_overview_json"]]

datetimestr = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_name = "job_details_list_master_" + datetimestr + ".csv"
pd.DataFrame(job_details_list_master).to_csv(csv_name, index=False)

storage_client = storage.Client(credentials=credentials)
bucket = storage_client.bucket("daily-job-details-list-master")
#blob = bucket.blob("job_details_list_master_2.csv")
blob = bucket.blob(csv_name)

#blob.upload_from_filename("job_details_list_master_2.csv")
blob.upload_from_filename(csv_name)