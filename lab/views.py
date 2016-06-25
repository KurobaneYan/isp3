from django.shortcuts import render

import lab.Crawler
from lab.models import Word, UrlIndex


def home_page(request):
    post_result = request.POST
    search_query = post_result.get('query')
    url_list = []

    if search_query is not None:
        words = search_query.split()

        word_in_db = Word.objects.filter(word__in=words)
        print(word_in_db)
        url_indexes = UrlIndex.objects.filter(word__in=word_in_db).order_by('-count')
        print(url_indexes)
        url_list = [ui.url.url for ui in url_indexes]

    return render(request, 'index.html', {
        'url_list': url_list,
    })



def add(request):
    post_result = request.POST
    url = post_result.get('url')
    depth = post_result.get('depth')
    width = post_result.get('width')
    urls = set()

    # print('{} is {}'.format(depth, type(depth)))
    # print('{} is {}'.format(url, type(url)))
    # print('{} is {}'.format(width, type(width)))

    if depth is None:
        depth = 1

    if width is None:
        width = 2

    if url is not None:
        print('Start crawling!')

        depth = int(depth)
        width = int(width)

        print('{} is {}'.format(depth, type(depth)))
        print('{} is {}'.format(url, type(url)))
        print('{} is {}'.format(width, type(width)))

        crawler = lab.Crawler.Crawler(url, depth=depth, width=width)
        print(crawler)
        urls = crawler.crawl()

    return render(request, 'add.html', {
        'url': url,
        'urls': urls,
    })
