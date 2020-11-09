"""
Author: Kanisk Chakraborty - https://github.com/chakrakan/
Indeed Scraper v1.0

Scrape jobs off of Canadian Indeed
"""

from datetime import datetime, timedelta
from os import path, getenv, remove, chdir
import glob

from dotenv import load_dotenv
from selenium import webdriver
from time import sleep, time
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from job import Job
import random

load_dotenv()
start_url = "https://ca.indeed.com/browsejobs"


def set_chrome_options(env: str) -> Options:
    """
    Method to set up Webdriver with Chrome options
    :param env: environment being run in dev/prod etc.
    :return: Options object for Chrome webdriver
    """
    chrome_options = Options()

    if env == "dev":
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--window-size=1920,1080")  # use this for debugging on Windows
    else:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")

    return chrome_options


def search_job(web_driver: WebDriver, what: str, where: str) -> None:
    """
    Searches Indeed for a particular job (what) for a particular location (where).
    :param web_driver: Selenium driver object
    :param what: The job user queries for
    :param where: The location user queries for
    :return:
    """
    try:
        job_title_input = web_driver.find_element_by_id("what")
        location_input = web_driver.find_element_by_id("where")
        job_title_input.send_keys(what)
        location_input.send_keys(where)
        web_driver.find_element_by_id("fj").click()
        web_driver.implicitly_wait(10)
    except Exception as err:
        print(f"Error Searching Job {what} in {where}: " + str(err))


def get_per_page_info(web_driver: WebDriver, search_items: list) -> list:
    """
    Indeed jobs are paginated based on window size. Keeping 1980x1800 driver resolution
    we get roughly 15 items per page. Returns a list of job dicts to be used directly with
    a pandas Data-frame
    :param web_driver: Selenium driver object
    :param search_items: list of web elements found by selenium once a search is performed with user query
    :return: list of job dicts
    """
    try:
        jobs = []
        for title in tqdm(search_items):
            title.find_element_by_xpath('..').click()
            job_container = WebDriverWait(web_driver, 15).until(
                EC.presence_of_element_located((By.ID, "vjs-container"))
            )
            info_container = job_container.find_element_by_id("vjs-jobinfo")
            job_title = info_container.find_element_by_id("vjs-jobtitle").text
            job_cp = info_container.find_element_by_id("vjs-cn").text
            job_loc = info_container.find_element_by_id("vjs-loc").text
            job_desc = job_container.find_element_by_id("vjs-desc").text

            full_chunk = str(info_container.text)

            # create new Job object
            a_job = Job(job_title, job_cp, job_loc, job_desc, full_chunk)
            jobs.append(a_job.as_dict())
            # sleep(random.randint(1, 4))
        return jobs
    except Exception as err:
        print(f"Error retrieving job info: " + str(err))


def has_next(web_driver: WebDriver) -> bool:
    """
    Check to see if next page exists. If it does, navigate to it.
    :param web_driver: Selenium webdriver object
    :return: True/False based on next page condition
    """
    try:
        next_page = web_driver.find_element_by_xpath("//a[@aria-label='Next']")
        if next_page.size != 0:
            next_page.click()
            popup_container = WebDriverWait(web_driver, 10).until(
                EC.presence_of_element_located((By.ID, "popover-foreground"))
            )
            popup_container.find_element_by_xpath("//button[@aria-label='Close']").click()
            return True
    except Exception as err:
        print(f"\nReached end of pagination. " + str(err))
        return False


def save_run_data(total_jobs: list, pages_wanted: int, job: str, location: str) -> str:
    """
    Save scraped jobs from a particular run to minimize repeated scrapes.
    :param location:
    :param job:
    :param total_jobs:
    :param pages_wanted:
    :return:
    """
    # create data folder
    Path(f"data/{job.strip().lower()}-{location.strip().lower()}").mkdir(parents=True, exist_ok=True)
    chdir(f"data/{job.strip().lower()}-{location.strip().lower()}")
    # create df from data
    jobs_df = pd.DataFrame(total_jobs)

    # naming convention
    file_path = "scrape"
    file_path += datetime.now().strftime("_%d-%m-%Y_%H-%M-%S")
    file_path += f"_{pages_wanted}-pgs"

    # save as a serialized pickle file
    jobs_df.to_pickle(file_path)
    print(f"Saved data into {file_path}\n")
    return file_path


def read_last_run(job: str, location: str) -> str:
    """
    Checks the "data" folder to find latest data output from previous runs.
    :return: string path to the latest created file based on recency/optimal needs
    """
    existing_files = glob.glob(f"data/{job.strip().lower()}-{location.strip().lower()}/*")
    latest_file = None
    if existing_files:
        print("Found previous runs, preloading most recent/optimal data...\n")
        # latest arbitrary run
        latest_file = max(existing_files, key=path.getctime)

        # check for a recent full-run
        full_run_files = [s for s in existing_files if '100-pgs' in s.split('_')[3]]
        if full_run_files:
            latest_file = max(full_run_files, key=path.getctime)

        # check to see if all data was recently acquired (~ 5 hours)
        latest_file_datetime = datetime.fromtimestamp(path.getctime(latest_file))
        check_date = datetime.now() - timedelta(hours=5)

        # if date of creation of our data is older than 5 hours from present, get fresh data
        if latest_file_datetime < check_date:
            print("Data is stale, fetching new data...\n")
            latest_file = None

        # also automatically purge older data files
        if len(existing_files) > 5:
            oldest_file = min(existing_files, key=path.getctime)
            remove(oldest_file)

    return latest_file


def load_jobs_from_file(file_path: str) -> pd.DataFrame:
    """
    Read pickle file and create a pandas data-frame to be used
    :param file_path: path to pickle file
    :return:
    """
    job_df = pd.read_pickle(file_path)
    return job_df


def scrape_jobs(job: str, location: str) -> tuple:
    """
    Call the webdriver and start the scraping process for fresh batch of job data
    :return: tuple of list of jobs and total pages to scrape provided by user
    """
    # initialize
    all_jobs = []
    total_pages = int(getenv("PAGES")) or 100
    driver = webdriver.Chrome(getenv("WEBDRIVER_PATH"), options=set_chrome_options(getenv("ENVIRONMENT")))
    driver.get(start_url)

    # Main Search
    search_job(driver, job, location)

    # Every job title in a page
    for curr_page in range(0, total_pages):
        print(f"\nGathering data from page {curr_page + 1} of {total_pages}...\n")
        search_items_per_page = driver.find_elements_by_xpath("//a[@data-tn-element='jobTitle']")
        all_jobs.extend(get_per_page_info(driver, search_items_per_page))
        if not has_next(driver):
            driver.quit()
            break

    return all_jobs, total_pages


def main() -> None:
    """
    Driver function
    """
    # init
    jobs_df = None
    # if prev runs exist, load data instead of scraping
    job, location = "Software Developer", "Toronto, ON"
    latest_file_path = read_last_run(job, location)

    if latest_file_path is not None:
        jobs_df = load_jobs_from_file(latest_file_path)
    else:
        # run scraper and destructure out data for other functions
        all_jobs, total_pages = scrape_jobs(job, location)
        # save all data from a run
        data_file = save_run_data(all_jobs, total_pages, job, location)
        jobs_df = load_jobs_from_file(data_file)

    print(jobs_df)


if __name__ == '__main__':
    main()
