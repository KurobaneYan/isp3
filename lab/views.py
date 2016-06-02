import urllib.request
import urllib.robotparser
from itertools import repeat
from multiprocessing import Pool
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


def f(x):
    return x * x


def pool(request):
    post_result = request.POST
    first_url = post_result.get('first_url')
    second_url = post_result.get('second_url')
    depth = post_result.get('depth')
    print(first_url)
    print(second_url)
    print(depth)
    urls = set()
    if depth is None:
        depth = 1
    else:
        depth = int(depth)
    if first_url is not None and second_url is not None:
        with Pool(processes=2) as pool:
            pool_map = pool.starmap(lab.Crawler.Crawler, zip([first_url, second_url], repeat(depth)))
            print(pool_map)
            print(type(pool_map))
            for i in pool_map:
                i.crawl()
                urls.update(i.get_links())

    print('Len: {}'.format(len(urls)))
    return render(request, 'pool.html', {
        'url_1': first_url,
        'url_2': second_url,
        'urls': urls,
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
