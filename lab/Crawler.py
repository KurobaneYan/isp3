from urllib import robotparser
from urllib.parse import urlsplit, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, start_url, depth=1):
        self.robot_parser = robotparser.RobotFileParser()
        self.start_url = start_url
        self.start_url_parse = urlparse(self.start_url)
        self.depth = depth
        self.get_robots()
        print('start url: {} \ndepth = {}'.format(self.start_url, self.depth))

    def get_robots(self):
        robots_url = urljoin(self.start_url_parse.scheme + '://' + self.start_url_parse.netloc + '/', 'robots.txt')
        print('robots.txt url is: {}'.format(robots_url))
        self.robot_parser.set_url(robots_url)
        self.robot_parser.read()

    def download_url(self, url):
        if url is not None:
            if self.robot_parser.can_fetch('*', url):
                headers = {
                    'User-Agent': 'SearchBotByMe v0.1',
                }
                url = self.clear_url(url)
                r = requests.get(url, headers=headers)
                if r.status_code != 200:
                    # raise Exception('Status code not 200!, it was: {}'.format(r.status_code))
                    print('{} status code was {}'.format(r.url, r.status_code))
                return r.text
            return ''
        return ''

    @staticmethod
    def clear_url(url):
        url = urlsplit(url).geturl()
        if url == b'':
            return ''
        if url.find('#') != -1:
            url = url[:url.find('#')]
        if url.find('?') != -1:
            url = url[:url.find('?')]
        if len(url) > 0 and url[-1] == '/':
            url = url[:-1]
        return url

    def get_links(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        links = set()
        for link in bs.find_all('a'):
            links.add(urljoin(url, self.clear_url(link.get('href'))))
        return links

    def get_links_from_url(self, url):
        if url is not None:
            return self.get_links(url, self.download_url(url))

    def get_all_links_from_url(self, url, depth=1):
        links = self.get_links(url, self.download_url(url))

        if depth < 2:
            return links

        temp_links = set()
        for link in links:
            temp_links.update(self.get_all_links_from_url(link, depth=depth - 1))

        links.update(temp_links)

        return links

    def crawl(self):
        return self.get_all_links_from_url(self.start_url, depth=self.depth)
