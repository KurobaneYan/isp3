import logging
import urllib.request
import urllib.robotparser
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

import lab.Crawler


def download_url(url):
    if url is not None:
        headers = {
            'User-Agent': 'SearchBotByMe v0.1',
        }
        url = clear_url(url)
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            # raise Exception('Status code not 200!, it was: {}'.format(r.status_code))
            logging.info('{} status code was {}'.format(r.url, r.status_code))
        return r.text
    return ''


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


def get_links(url, html):
    bs = BeautifulSoup(html, 'lxml')
    links = set()
    for link in bs.find_all('a'):
        links.add(urljoin(url, clear_url(link.get('href'))))
    return links


def get_links_from_url(url):
    if url is not None:
        return get_links(url, download_url(url))


def get_all_links_from_url(url, depth=1):
    links = get_links(url, download_url(url))
    print(links)

    if depth < 2:
        return links

    temp_links = set()
    for link in links:
        temp_links.update(get_all_links_from_url(link, depth=depth-1))

    links.update(temp_links)

    return links


def home_page(request):
    post_result = request.POST
    url = post_result.get('item_text')

    if url is not None:
        crawler = lab.Crawler.Crawler(url, depth=1)
        links = crawler.crawl()
    else:
        links = set()

    print(links)
    return render(request, 'index.html', {
        'url': request.POST.get('item_text', ''),
        'links': links,
    })


def parse(request):
    post_result = request.POST
    url = post_result.get('url_text')

    robots_url = urljoin(url, 'robots.txt')
    print('trying to parse robots')
    print(robots_url)

    robot_parser = urllib.robotparser.RobotFileParser()
    robot_parser.set_url(url)
    robot_parser.read()
    print('finish parsing robots')

    if url is not None:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            # print(soup.prettify())
            print(url)

            for link in soup.find_all('a'):
                href = link.get('href')
                if robot_parser.can_fetch('*', href):
                    if href[0] == '/':
                        print(urljoin(url, href))
                    else:
                        print(href)

    return render(request, 'parse.html', {
        'new_url': request.POST.get('url_text', ''),
    })
