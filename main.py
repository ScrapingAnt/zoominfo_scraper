import json
import math
import re

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from tenacity import retry, stop_after_attempt
import click


def make_scrapingant_request(target_url, rapidapi_key):
    print(f'getting page {target_url}')
    headers = {
        'x-rapidapi-host': "scrapingant.p.rapidapi.com",
        'x-rapidapi-key': rapidapi_key,
    }
    r = requests.post(
        'https://scrapingant.p.rapidapi.com/post',
        data=json.dumps({'url': target_url}),
        headers=headers
    )
    return r.text


# Sometimes we cant find table of contacts on the page. Usually it's related to recaptcha.
# In this case we have to retry our request.
@retry(stop=stop_after_attempt(2), retry_error_callback=list)
def get_contacts_from_page(page_url, rapidapi_key):
    page_html = make_scrapingant_request(page_url, rapidapi_key)
    soup = BeautifulSoup(page_html, 'html.parser')
    contacts = []
    table = soup.find('table', attrs={'class': 'page_table'})
    table_body = table.find('tbody')
    for row in table_body.find_all('tr'):
        contacts.append([
            row.find('td', attrs={'data-column': 'Contact Name'}).getText(),
            row.find('td', attrs={'data-column': 'Job Title'}).getText(),
            row.find('td', attrs={'data-column': 'Location'}).getText(),
        ])
    zoom_total_contacts_pattern = re.compile(r'(?P<num_contacts>\d+) results')
    pages_count_text = soup.find('h2', attrs={'class': 'page_searchResults_numberOfResults'}).getText()
    total_contacts = zoom_total_contacts_pattern.search(pages_count_text.replace(',', '')).group('num_contacts')
    pages_count = math.ceil(int(total_contacts) / 25)
    return contacts, pages_count


def get_company_contacts(company_url, rapidapi_key):
    contacts, pages_count = get_contacts_from_page(company_url, rapidapi_key)
    for page_num in range(2, min(5, pages_count) + 1):
        contacts_from_page, _ = get_contacts_from_page(f'{company_url}?pageNum={page_num}', rapidapi_key)
        contacts.extend(contacts_from_page)
    return contacts


def validate_company_url(ctx, param, value):
    if re.match(r'https:\/\/www\.zoominfo\.com\/pic\/(.*)\/\d+', value):
        return value
    else:
        raise click.BadParameter(
            'Invalid url, correct example: https://www.zoominfo.com/pic/mental-health-america-inc/76809493')


@click.command()
@click.argument('company_url', type=str, required=True, callback=validate_company_url)
@click.option("--rapidapi_key", type=str, required=True,
              help="Api key from https://rapidapi.com/okami4kak/api/scrapingant")
def main(company_url, rapidapi_key):
    contacts = get_company_contacts(company_url, rapidapi_key)
    print(tabulate(contacts, headers=['Contact Name', 'Job Title', 'Location']))


if __name__ == '__main__':
    main()
