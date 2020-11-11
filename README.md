# Job Seeker

A scraper to find job listings and their descriptions.

Currently supported websites:
- Indeed Canada

## Setup

#### Scraper Standalone

1. Create a virtual env for the project `python -m venv venv`
2. Install the requirements `pip install -r requirements.txt`
3. Create an env file at the project root using `touch .env` and add variables as per `.env.example` to configure
4. Run `scraper.py`

#### Dash Web App

1. Run `seeker.py`
2. Type in your params (these is a direct representation of the `.env` params) and click search.


## Directory Structure

Running the scraper locally with the following `.env` settings
```text
WEBDRIVER_PATH=utils/chromedriver
ENVIRONMENT=prod
PAGES=2
```
should emit the following directory structure

```shell script
.
├── .env
├── .env.example
├── .gitignore
├── README.md
├── data
│   └── software\ developer-toronto,\ on
│       └── scrape_10-11-2020_06-52-09_2-pgs
├── job.py
├── logs
│   └── run-2020-11-10\ 06:50:20.597174.log
├── scraper.py
├── seeker.py
├── requirements.txt
└── utils
    └── chromedriver
```
#### Notes
**data**: the data folder will contain all the scraped data pickles with each folder within referring to the job title queried along with the location.  
**logs**: the logs folder will contain a log of the run with detail at the info level.  

There is logic implemented to automatically update data pickles for repeat runs if data seems to be outdated and pickles are reused to minimize constant scrapes.

**Sample log file**  
```text
INFO:root:Page 1 done in 56.722583s
INFO:root:Page 2 done in 48.49284s
```

As visible, there are simple optimizations to prevent the scraper from getting blocked/throttled by indeed.  
If a page scrape takes roughly `52s`, a 90 page scrape (most I've run) of `"Software Developer"` jobs in `"Toronto, ON"` will run for roughly `1.32 hrs`.

I don't advise it, but you can play around with [line 99](https://github.com/jobseekr/scraper/blob/cecbcc94a38766f25f57a8c02d5ac3d6ead3819b/main.py#L99) to speed up this process a LOT more by either reducing or completely eliminating `sleep`

#### Author

[Kanisk Chakraborty](https://github.com/chakrakan)
