# Job Seeker

A scraper to find job listings and their descriptions.

Currently supported websites:
- Indeed Canada

## Setup

#### Scraper Standalone

1. Create a virtual env for the project `python -m venv venv`
2. Install the requirements `pip install -r requirements.txt`
3. Create an env file at the project root using `touch .env` and add variables as per `.env.example` to configure
4. Run `scraper.py` located within `app` with your own params for the main function.

#### Flask Web App

The web app uses Factory Pattern to encase a Dash App within a Flask app. 

1. `wsgi.py` is the entry point for the Flask app
2. Navigate to `/dashboard/` route to see the Dash app
3. Type in your params (these is a direct representation of the `.env` params) and click search.


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
├── README.md
├── app
│   ├── __init__.py
│   ├── dashapp
│   │   ├── __init__.py
│   │   └── seeker.py
│   ├── job.py
│   ├── routes.py
│   └── scraper.py
├── data
│   └── software\ developer-toronto,\ on
│       ├── scrape_24-11-2020_15-37-16_2-pgs
│       └── scrape_24-11-2020_17-33-36_3-pgs
├── logs
│   └── run-2020-11-24\ 17:30:06.550725.log
├── requirements.txt
├── utils
│   └── chromedriver
└── wsgi.py
```
#### Notes
**data**: the data folder will contain all the scraped data pickles with each folder within referring to the job title queried along with the location.  
**logs**: the logs folder will contain a log of the run with detail at the info level.

Especially if running in headless mode (which would be through the wsgi app), I strongly suggest running large scrapes once in a blue moon and instead opting to keep to a small amount of pages each time (1-20) so that your client doesn't get blocked by Indeed. If that does happen, use a proxy or try again within 3 hours and it should start working again. You might also get captcha walled which the program currently doesn't handle.

There is logic implemented to automatically update data for repeat runs if data seems to be outdated and data is reused to minimize multiple scrapes.

**Sample log file**  
```text
INFO:root:Page 1 done in 56.722583s
INFO:root:Page 2 done in 48.49284s
```

As visible, there are simple optimizations to prevent the scraper from getting blocked/throttled by indeed.  
If a page scrape takes roughly `52s`, a 100 page scrape (most I've run) of `"Software Developer"` jobs in `"Toronto, ON"` will run for roughly `1.32 hrs`.

#### Author

[Kanisk Chakraborty](https://github.com/chakrakan)
