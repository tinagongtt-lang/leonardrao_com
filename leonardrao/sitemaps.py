from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import BlogPost


class BlogPostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return BlogPost.objects.select_related('author')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['core:home', 'games:index', 'tools:index', 'guestbook:guestbook',
                'blog:blog_home', 'blog:about_me']

    def location(self, item):
        return reverse(item)
