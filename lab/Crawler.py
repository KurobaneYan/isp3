from itertools import repeat
from multiprocessing import Pool
from urllib import robotparser
from urllib.parse import urlsplit, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, start_url, depth):
        self.robot_parser = robotparser.RobotFileParser()
        self.start_url = start_url
        self.start_url_parse = urlparse(self.start_url)
        self.depth = depth
        self.get_robots()
        self.links = set()
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
        if url.startswith('mailto:'):
            return ''
        if url.find('#') != -1:
            url = url[:url.find('#')]
        if url.find('?') != -1:
            url = url[:url.find('?')]
        if len(url) > 0 and url[-1] == '/':
            url = url[:-1]
        return url

    def get_links_on_page(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        links = set()
        for link in bs.find_all('a'):
            if link.get('href') != self.start_url:
                links.add(urljoin(url, self.clear_url(link.get('href'))))
        return links

    def get_all_links_from_url(self, url):
        links = self.get_links_on_page(url, self.download_url(url))

        if self.depth < 2:
            return links

        temp_links = set()
        with Pool(processes=4) as pool:
            # pool_map = pool.map(Crawler, links)
            pool_map = pool.starmap(Crawler.crawl, zip(links, repeat(self.depth - 1)))
            for i in pool_map:
                temp_links.update(i.get_links())


        links.update(temp_links)
        if self.start_url in self.links:
            links.remove(self.start_url)

        return links

    def crawl(self, start_url, depth):
        self.__init__(start_url, depth)
        self.links = self.get_all_links_from_url(self.start_url)

    def get_links(self):
        return self.links
