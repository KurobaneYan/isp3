from time import sleep
from urllib import robotparser
from urllib.parse import urlsplit, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, start_url, depth):
        self.start_url = start_url
        self.depth = depth
        self.links = set()
        print('start url: {} \ndepth = {}'.format(self.start_url, self.depth))

    def get_robots(self, url):
        start_url_parse = urlparse(url)
        robot_parser = robotparser.RobotFileParser()
        robots_url = urljoin(start_url_parse.scheme + '://' + start_url_parse.netloc + '/', 'robots.txt')
        print('robots.txt url is: {}'.format(robots_url))
        robot_parser.set_url(robots_url)
        robot_parser.read()
        return robot_parser

    def download_url(self, url):
        sleep(0.005)
        if url is not None:
            url = self.clear_url(url)
            robot_parser = self.get_robots(url)
            if robot_parser.can_fetch('*', url):
                headers = {
                    'User-Agent': 'SearchBotByMe v0.1.1',
                }
                r = requests.get(url, headers=headers)
                if r.status_code != 200:
                    print('{} status code was {}'.format(r.url, r.status_code))
                return r.text

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

    def prepare_soap(self, html):
        bs = BeautifulSoup(html, 'lxml')
        return bs

    def soap_links(self, url, soup):
        links = set()
        for link in soup.find_all('a'):
            if link.get('href') != self.start_url:
                links.add(urljoin(url, self.clear_url(link.get('href'))))
        links.remove(url)
        return links

    def index(self, soup):
        for script in soup(['script', 'style']):
            script.extract()

        text = soup.get_text()

        lines = list(line.strip() for line in text.splitlines())
        chunks = list(phrase.strip(' «».,;:—↓↑→←*/"?()<>{}[]') for line in lines for phrase in line.split(' '))
        text = list(chunk for chunk in chunks if chunk)
        print(text)


    def process_url(self, url):
        html = self.download_url(url)
        soup = self.prepare_soap(html)

        links = self.soap_links(url, soup)

        # index the soup
        self.index(soup)

        return links

    def get_all_links_from_url(self, url):
        links = self.process_url(url)

        if self.depth < 2:
            return links

        # temp_links = set()
        # with Pool(processes=4) as pool:
        #     # pool_map = pool.map(Crawler, index_pairs)
        #     # pool_map = pool.starmap(Crawler, zip(index_pairs, repeat(self.depth - 1)))
        #     # for i in pool_map:
        #     #     i.crawl()
        #     #     temp_links.update(i.get_links())
        #     pool_map = pool.map(self.process_url, index_pairs)
        #     print(len(pool_map))

        return links