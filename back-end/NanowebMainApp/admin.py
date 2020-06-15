from django.contrib import admin

# NanoWeb models here.

from .models import Query
admin.site.register(Query)
