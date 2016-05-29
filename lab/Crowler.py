import logging
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


def download_url(url):
    headers = {
        'User-Agent': 'SearchBotByMe v0.1',
    }
    url = urlsplit(url).geturl()
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception('Status code not 200!, it was: {}', format(r.status_code))
    return r.text


def clear_url(url):
    url = urlsplit(url).geturl()
    if url.find('#') != -1:
        url = url[:url.find('#')]
    if len(url) > 0 and url[-1] == '/':
        url = url[:-1]
    return url


def get_links(url, html):
    bs = BeautifulSoup(html, 'lxml')
    links = set()
    for link in bs.find_all('a'):
        links.add(urljoin(url, clear_url(link.get('href'))))
    return links


def get_links_from_url(url):
    if url is not None:
        return get_links(url, download_url(url))


class Crawler(object):
    def __init__(self, start_url):
        self.start_url = start_url

    def crawl(self):
        current_page = self.start_url
        logging.info('current_page: {}', format(current_page))
