import urllib.request
import urllib.robotparser
from multiprocessing import Process
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.shortcuts import render

import lab.Crawler


def home_page(request):
    post_result = request.POST
    url = post_result.get('item_text')

    if url is not None:
        crawler = lab.Crawler.Crawler(url, depth=2)
        p = Process(target=crawler.crawl())
        p.start()
        p.join()
        links = crawler.get_links()
        if crawler.start_url in links:
            print('Faund start url!')
    else:
        links = set()

    return render(request, 'index.html', {
        'url': request.POST.get('item_text', ''),
        #'links': links,
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
