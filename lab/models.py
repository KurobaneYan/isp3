from django.db import models


class Word(models.Model):
    word = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.word


class Url(models.Model):
    url = models.URLField(unique=True)
    words_count = models.IntegerField(default=0)

    def __str__(self):
        return 'url:{}; words_count: {};'.format(
            self.url, self.words_count)


class UrlIndex(models.Model):
    count = models.IntegerField()
    url = models.ForeignKey(Url)
    word = models.ForeignKey(Word)

    def url_and_language(self):
        return self.url.url + ' | '

    def __str__(self):
        return '{} word: {}; count: {};'.format(
            self.url, self.word, self.count)