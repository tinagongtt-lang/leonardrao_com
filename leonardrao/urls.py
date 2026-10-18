"""
URL configuration for leonardrao project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core import views as core_views
from leonardrao.sitemaps import BlogPostSitemap, StaticViewSitemap

sitemaps = {
    'blog': BlogPostSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('game/', include('games.urls')),
    path('tools/', include('tools.urls')),
    path('guestbook/', include('guestbook.urls')),
    path('blog/', include('blog.urls')),
    path('chat/', include('chat.urls')),
    prefix_default_language=False,
) + [
    path('i18n/', include('django.conf.urls.i18n')),
    path('captcha/', include('captcha.urls')),
    path('service-worker.js', core_views.service_worker, name='service_worker'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', core_views.robots_txt, name='robots_txt'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
