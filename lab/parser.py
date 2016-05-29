import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from urllib.parse import urljoin


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)


parser = MyHTMLParser()


def parseUrl(url):
    robots_url = urljoin(url, 'robots.txt')
    print(robots_url)

    robot_parser = urllib.robotparser.RobotFileParser()
    robot_parser.set_url(url)
    robot_parser.read()