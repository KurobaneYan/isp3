from collections import Counter
from multiprocessing.pool import Pool
from time import sleep
from urllib import robotparser
from urllib.parse import urlsplit, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from django.db import transaction

from lab.models import Url, Word, UrlIndex


class Crawler:
    def __init__(self, start_url, depth=1, width=10, workers=4):
        self.start_url = self.clear_url(start_url)
        self.depth = depth
        self.width = width
        self.workers = workers
        self.links = set()
        self.processed_links = set()

    def get_robots(self, url):
        start_url_parse = urlparse(url)
        robot_parser = robotparser.RobotFileParser()
        robots_url = urljoin(start_url_parse.scheme + '://' + start_url_parse.netloc + '/', 'robots.txt')
        print('robots.txt url is: {}'.format(robots_url))
        robot_parser.set_url(robots_url)
        robot_parser.read()
        return robot_parser

    def download_url(self, url):
        sleep(0.02)
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
        if url.startswith('irc:'):
            return ''
        if url.find('#') != -1:
            url = url[:url.find('#')]
        if url.find('?') != -1:
            url = url[:url.find('?')]
        if len(url) > 0 and url[-1] == '/':
            url = url[:-1]
        return url.replace('https', 'http')

    def prepare_soap(self, html):
        if html is not None:
            bs = BeautifulSoup(html, 'lxml')
            return bs

    def soap_links(self, url, soup):
        if soup is not None:
            links = set()
            for link in soup.find_all('a'):
                if urljoin(url, self.clear_url(link.get('href'))) not in self.processed_links:
                    if len(links) < self.width:
                        # print(urljoin(url, self.clear_url(link.get('href'))))
                        links.add(urljoin(url, self.clear_url(link.get('href'))))
            return links

    @transaction.atomic
    def index(self, url, soup):
        for script in soup(['script', 'style']):
            script.extract()

        text = soup.get_text()

        lines = list(line.strip() for line in text.splitlines())
        chunks = list(phrase.strip(' «».,;:—↓↑→←*/"?()<>{}[]|') for line in lines for phrase in line.split(' '))
        text = list(chunk for chunk in chunks if chunk)

        url_model, is_created = Url.objects.get_or_create(url=url)
        url_model.urlindex_set.all().delete() # ???

        counter_dict = Counter(text)

        url_model.words_count = sum(counter_dict.values())

        all_words_to_add = set(counter_dict.keys())
        words_in_db = set(
            Word.objects.filter(word__in=counter_dict.keys()).values_list('word', flat=True)
        )
        words_to_create = all_words_to_add - words_in_db

        url_model.save()
        Word.objects.bulk_create(Word(word=word) for word in words_to_create)
        indices = (UrlIndex(url=url_model, count=count, word=Word.objects.get(word=word))
                   for word, count in counter_dict.items())
        UrlIndex.objects.bulk_create(indices)

    def process_url(self, url):
        if url is not None:
            html = self.download_url(url)
            soup = self.prepare_soap(html)

            links = self.soap_links(url, soup)

            self.index(url, soup)

            return links

    def crawl(self):
        links = self.process_url(self.start_url)
        self.processed_links.add(self.clear_url(self.start_url))
        links = links - self.processed_links

        print('F {} links {}'.format(len(links), links))
        print('F {} processed links {}'.format(len(self.processed_links), self.processed_links))

        if self.depth < 2:
            return links

        while self.depth > 1:
            print('{} links {}'.format(len(links), links))
            print('{} processed links {}'.format(len(self.processed_links), self.processed_links))
            with Pool(self.workers) as pool:
                pool_map = pool.map(self.process_url, links)

            self.processed_links = self.processed_links | links

            links.clear()

            if pool_map is not None:
                for i in pool_map:
                    if i is not None:
                        links = links | i

            self.depth -= 1

        print('R {} links {}'.format(len(links), links))
        print('R {} processed links {}'.format(len(self.processed_links), self.processed_links))
        print('B {} links {}'.format(len(links | self.processed_links), links | self.processed_links))

        return links | self.processed_links

    def __str__(self):
        return 'start url {} \nwidth {} \ndepth {}'.format(self.start_url, self.width, self.depth)