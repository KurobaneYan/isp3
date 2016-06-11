from queue import Queue
from threading import Thread
from time import sleep
from urllib import request
from urllib.error import HTTPError, URLError


class UrlFetcherPool(object):
    MAX_READ_SIZE = 1024 * 1024

    def __init__(self, threads=4):
        self._input_queue = Queue()
        self._output_queue = None
        self._threads = threads
        self._is_closed = False
        self._delay = 0

        for _ in range(threads):
            t = Thread(target=self._process_urls)
            t.setDaemon(True)
            t.start()

    def _process_urls(self):
        while True:
            url = self._input_queue.get()
            if self._is_closed:
                break

            html = None
            try:
                html = request.urlopen(url, timeout=10).read(UrlFetcherPool.MAX_READ_SIZE)
            except HTTPError as e:
                print("HTTP error: " + str(e) + url)
            except URLError as e:
                print("URL error: " + str(e) + url)
            except Exception as e:
                print("Exception while fetching: " + str(e) + url)

            self._output_queue.put((url, html))
            self._input_queue.task_done()
            sleep(self._delay)

    def set_output_queue(self, new_queue):
        self._output_queue = new_queue

    def enqueue_urls(self, url_list):
        for url in url_list:
            self._input_queue.put(url)

    def set_delay(self, new_delay):
        self._delay = new_delay if new_delay >= 0 else 0

    def close(self):
        self._input_queue.join()
        self._is_closed = True
        for _ in range(self._threads):
            self._input_queue.put(None)


if __name__ == '__main__':
    uf = UrlFetcherPool(threads=6)
    q = Queue()
    uf.set_output_queue(q)
    uf.enqueue_urls(['https://onliner.by', 'https://catalog.onliner.by',
                     'https://people.onliner.by', 'https://tech.onliner.by',
                     'https://forum.onliner.by', 'http://bsuir.by'])

    for _ in range(6):
        print(q.get()[0])
        if q.get()[1] is not None:
            print('Yes')

        if _ == 3:
            uf.close()