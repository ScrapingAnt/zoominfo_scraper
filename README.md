# Zoominfo parser using scrapingant.com
This project shows how to use <a href="https://scrapingant.com">ScrapingAnt</a> scraping service to load public data from zoominfo.

ScrapingAnt takes away all the messy work necessary to set up a browser and proxies for crawling. So you can just focus on your data.
## Usage
To run this code you need RapidApi key. Just go to <a href="https://rapidapi.com/okami4kak/api/scrapingant">ScrapingAnt page on Rapidapi</a>, and click "Subscribe to Test" button. After that you have to select plan(there is a free one including 100 requests). After that you can find you api key in "X-RapidAPI-Key" field on <a href="https://rapidapi.com/okami4kak/api/scrapingant/endpoints">endpoints</a> page.
#### With Docker
```shell script
docker build -t zoominfo_parser . && docker run -it zoominfo_parser https://www.zoominfo.com/c/mental-health-america-inc/76809493 --rapidapi_key <RAPID_API_KEY> --email_format first_last
```

#### Without Docker
This code was written for python 3.7+
```shell script
$ git clone https://github.com/ScrapingAnt/zoominfo_scraper.git
$ cd zoominfo_scraper
$ pip install -r requirements.txt
$ python main.py --help
$ python main.py https://www.zoominfo.com/c/mental-health-america-inc/76809493 --rapidapi_key <RAPID_API_KEY> --email_format first_last
```

#### Sample output:
```shell script
name                    job                           location                             email                                         company_name
----------------------  ----------------------------  -----------------------------------  --------------------------------------------  -------------------------
Jewell Gooding          Executive Director            United States, Virginia, Alexandria  jewell_gooding@mentalhealthamerica.net        Mental Health America Inc
Victoria Renard         Vice President, Development   United States, Virginia, Alexandria  victoria_renard@mentalhealthamerica.net       Mental Health America Inc
...
```
