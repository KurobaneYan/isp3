import re
import urllib.request
import urllib.robotparser
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.shortcuts import render

import lab.Crawler


def home_page(request):
    post_result = request.POST
    url = post_result.get('item_text')

    # if url is not None:
    #     crawler = lab.Crawler.Crawler(url, depth=2)
    #     p = Process(target=crawler.crawl())
    #     p.start()
    #     p.join()
    #     links = crawler.get_links()
    #     if crawler.start_url in links:
    #         print('Faund start url!')
    # else:
    #     links = set()

    temp = None
    if url is not None:
        crawler = lab.Crawler.Crawler(url, 1)
        temp = crawler.process_url(url)
        bs = BeautifulSoup(temp[1], 'lxml')
        temp[1] = bs.get_text()
        temp[1] = re.sub(r'[^A-Z a-z0-9]', ' ', temp[1])

    if url is not None:
        url = re.sub(r'[^A-Za-z]', ' ', url)

    return render(request, 'index.html', {
        'url': temp,
        # 'url': request.POST.get('item_text', ''),
        #'links': links,
    })


def pool(request):
    post_result = request.POST
    first_url = post_result.get('first_url')
    second_url = post_result.get('second_url')
    depth = post_result.get('depth')
    print(first_url)
    print(second_url)
    print(depth)
    text = ''
    urls = []
    if depth is None:
        depth = 1
    else:
        depth = int(depth)

    if first_url is not None:
        crawler = lab.Crawler.Crawler(first_url, 1)
        urls = crawler.get_all_links_from_url(first_url)

        # html = crawler.download_url(first_url)
        #
        # soup = BeautifulSoup(html, 'lxml')
        #
        # for script in soup(['script', 'style']):
        #     script.extract()
        #
        # text = soup.get_text()
        #
        # lines = (line.strip() for line in text.splitlines())
        # chunks = (phrase.strip() for line in lines for phrase in line.split(' '))
        # text = '\n'.join(chunk for chunk in chunks if chunk)

    print('Len: {}'.format(len(urls)))
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
