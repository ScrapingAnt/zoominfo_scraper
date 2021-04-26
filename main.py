import math
import re

from bs4 import BeautifulSoup
from tabulate import tabulate
from tenacity import retry, stop_after_attempt
import click
import tldextract
from scrapingant_client import ScrapingAntClient


def make_scrapingant_request(target_url, scrapingant_api_token):
    print(f'getting page {target_url}')
    client = ScrapingAntClient(token=scrapingant_api_token)
    result = client.general_request(target_url, proxy_country='us')
    return result.content


# Sometimes we cant find table of contacts on the page. Usually it's related to recaptcha.
# In this case we have to retry our request.
@retry(stop=stop_after_attempt(2), retry_error_callback=lambda _: ([], 0))
def get_contacts_from_page(page_url, scrapingant_api_token):
    page_html = make_scrapingant_request(page_url, scrapingant_api_token)
    soup = BeautifulSoup(page_html, 'html.parser')
    contacts = []
    table = soup.find('table', attrs={'class': 'page_table'})
    table_body = table.find('tbody')
    for row in table_body.find_all('tr'):
        contacts.append({
            'name': row.find('td', attrs={'data-column': 'Contact Name'}).getText(),
            'job': row.find('td', attrs={'data-column': 'Job Title'}).getText(),
            'location': row.find('td', attrs={'data-column': 'Location'}).getText(),
        })
    zoom_total_contacts_pattern = re.compile(r'(?P<num_contacts>\d+) results')
    pages_count_text = soup.find('h2', attrs={'class': 'page_searchResults_numberOfResults'}).getText()
    total_contacts = zoom_total_contacts_pattern.search(pages_count_text.replace(',', '')).group('num_contacts')
    pages_count = math.ceil(int(total_contacts) / 25)
    return contacts, pages_count


@retry(stop=stop_after_attempt(2), retry_error_callback=lambda _: ('', ''))
def get_company_info(company_page_url, scrapingant_api_token):
    page_html = make_scrapingant_request(company_page_url, scrapingant_api_token)
    soup = BeautifulSoup(page_html, 'html.parser')
    company_name = soup.find('h1', attrs={'class': 'company-name'}).getText()
    website_tag = soup.find('p', text="Website:")
    company_site_url = website_tag.parent.find('a').getText()
    parsed_url = tldextract.extract(company_site_url)
    company_domain = f'{parsed_url.domain}.{parsed_url.suffix}'
    return company_name, company_domain


def get_company_contacts(company_url, scrapingant_api_token, email_format):
    company_name, company_domain = get_company_info(company_url, scrapingant_api_token)
    print(f'Company info: {company_name}, {company_domain}')
    company_contacts_url = company_url.replace('https://www.zoominfo.com/c', 'https://www.zoominfo.com/pic')
    contacts, pages_count = get_contacts_from_page(company_contacts_url, scrapingant_api_token)
    for page_num in range(2, min(5, pages_count) + 1):
        contacts_from_page, _ = get_contacts_from_page(
            f'{company_contacts_url}?pageNum={page_num}',
            scrapingant_api_token
        )
        contacts.extend(contacts_from_page)
    if company_name and company_domain:
        for contact in contacts:
            contact['email'] = generate_email(contact, company_domain, email_format)
            contact['company_name'] = company_name
    return contacts


def generate_email(contact, domain, email_format):
    name_parts = contact['name'].replace('.', '').replace('\'', '').split(' ')
    if email_format == 'firstlast':
        username = f'{name_parts[0]}{name_parts[-1]}'
    elif email_format == 'firstmlast':
        if len(name_parts) > 2:
            username = f'{name_parts[0]}{name_parts[1][:1]}{name_parts[-1]}'
        else:
            username = f'{name_parts[0]}{name_parts[-1]}'
    elif email_format == 'flast':
        username = f'{name_parts[0][:1]}{name_parts[-1]}'
    elif email_format == 'lastf':
        username = f'{name_parts[-1]}{name_parts[0][:1]}'
    elif email_format == 'first.last':
        username = f'{name_parts[0]}.{name_parts[-1]}'
    elif email_format == 'first_last':
        username = f'{name_parts[0]}_{name_parts[-1]}'
    elif email_format == 'fmlast':
        if len(name_parts) > 2:
            username = f'{name_parts[0][:1]}{name_parts[1][:1]}{name_parts[-1]}'
        else:
            username = f'{name_parts[0][:1]}{name_parts[-1]}'
    else:
        # default to 'full'
        username = ''.join(name_parts)
    return f'{username.lower()}@{domain}'


def validate_company_url(ctx, param, value):
    if re.match(r'https:\/\/www\.zoominfo\.com\/c\/.*/\d+', value):
        return value
    else:
        raise click.BadParameter(
            'Invalid url, correct example: https://www.zoominfo.com/c/mental-health-america-inc/76809493')


@click.command()
@click.argument('company_url', type=str, required=True, callback=validate_company_url)
@click.option("--scrapingant_api_token", type=str, required=True,
              help="Api key from https://app.scrapingant.com/dashboard")
@click.option('--email_format',
              type=click.Choice([
                  'firstlast', 'firstmlast', 'flast', 'first.last', 'first_last', 'fmlast', 'lastf', 'full'
              ]),
              default='full')
def main(company_url, scrapingant_api_token, email_format):
    contacts = get_company_contacts(company_url, scrapingant_api_token, email_format)
    if contacts:
        header = contacts[0].keys()
        rows = [x.values() for x in contacts]
        print(tabulate(rows, header))
    else:
        print('no contacts found')


if __name__ == '__main__':
    main()
