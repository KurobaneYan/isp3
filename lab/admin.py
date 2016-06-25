from django.contrib import admin

from .models import Word, Url, UrlIndex

admin.site.register(Word)
admin.site.register(Url)
admin.site.register(UrlIndex)
