from django.shortcuts import render

import lab.Crawler


def home_page(request):
    return render(request, 'index.html', {})


def add(request):
    post_result = request.POST
    url = post_result.get('url')
    depth = post_result.get('depth')
    width = post_result.get('width')
    text = ''
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
        'text': text,
    })
