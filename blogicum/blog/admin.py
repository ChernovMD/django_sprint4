from django.contrib import admin
from .models import Post, Category, Location

admin.site.site_title = 'Блог'
admin.site.site_header = 'Блог'

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Location)
