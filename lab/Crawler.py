from collections import Counter
from multiprocessing.pool import Pool
from time import sleep
from urllib import robotparser
from urllib.parse import urlsplit, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from lab.models import Url, Word, UrlIndex


class Crawler:
    def __init__(self, start_url, depth=1, width=10, workers=4):
        self.start_url = self.clear_url(start_url)
        self.depth = depth
        self.width = width
        self.workers = workers
        self.links = set()
        self.processed_links = set()
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
        return url.replace('https', 'http')

    def prepare_soap(self, html):
        bs = BeautifulSoup(html, 'lxml')
        return bs

    def soap_links(self, url, soup):
        links = set()
        for link in soup.find_all('a'):
            if link.get('href') not in self.processed_links:
                if len(links) < self.width:
                    if link.get('href') != self.start_url:
                        links.add(urljoin(url, self.clear_url(link.get('href'))))

        return links

    def index(self, url, soup):
        new_url = False

        for script in soup(['script', 'style']):
            script.extract()

        text = soup.get_text()

        lines = list(line.strip() for line in text.splitlines())
        chunks = list(phrase.strip(' «».,;:—↓↑→←*/"?()<>{}[]|') for line in lines for phrase in line.split(' '))
        text = list(chunk for chunk in chunks if chunk)

        words_count = len(text)
        word_occurrences = dict(Counter(text))

        existed_words = Word.objects.filter(word__in=list(word_occurrences.keys()))
        new_words = set(word_occurrences.keys()).difference_update(set(existed_words))
        print(new_words)

        try:
            model_url = Url.objects.get(url=url)
            model_url.words_count = words_count
            model_url.save()
        except Url.DoesNotExist:
            model_url = Url(url=url, words_count=words_count)
            model_url.save()
            new_url = True

        model_words = []
        model_url_indexes = []
        for w in new_words:
            word = Word(word=w)
            model_words.append(word)
            model_url_indexes.append(UrlIndex(url=model_url, word=word, count=word_occurrences[w]))

        Word.objects.bulk_create(model_words)
        UrlIndex.objects.bulk_create(model_url_indexes)

        if new_url:
            model_extra_url_indexes = []
            for w in existed_words:
                model_extra_url_indexes.append(UrlIndex(url=model_url, word=w, count=word_occurrences[w.word]))
            UrlIndex.objects.bulk_create(model_extra_url_indexes)

        existed_url_indexes = UrlIndex.objects.filter(word__in=existed_words, url=model_url)
        for ui in existed_url_indexes:
            ui.count = word_occurrences[ui.word.word]
            ui.save()

    def process_url(self, url):
        if url is not None:
            html = self.download_url(url)
            soup = self.prepare_soap(html)

            links = self.soap_links(url, soup)

            # index the soup
            self.index(url, soup)
            # print('indexing {}'.format(url))

            return links

    def crawl(self):
        links = self.process_url(self.start_url)

        if self.depth < 2:
            return links


        while self.depth > 0:
            print(links)
            print(self.depth)
            with Pool(self.workers) as pool:
                pool_map = pool.map(self.process_url, links)

            self.processed_links.update(links)

            links.clear()

            for i in pool_map:
                links.update(i)

            self.depth -= 1

        return links