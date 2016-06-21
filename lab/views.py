import urllib.request
import urllib.robotparser
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.shortcuts import render

import lab.Crawler


def home_page(request):
    return render(request, 'index.html', {})


def pool(request):
    post_result = request.POST
    first_url = post_result.get('first_url')
    second_url = post_result.get('second_url')
    depth = post_result.get('depth')
    width = post_result.get('width')
    print(first_url)
    print(second_url)
    print(depth)
    text = ''
    urls = []
    if depth is None:
        depth = 1
    else:
        depth = int(depth)

    if width is None:
        width = 1
    else:
        width = int(width)

    if first_url is not None:
        crawler = lab.Crawler.Crawler(first_url, depth=depth, width=width)
        urls = crawler.crawl()

    print('{} : {}'.format(urls, len(urls)))

    return render(request, 'pool.html', {
        'url': first_url,
        'urls': urls,
        'text': text,
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
