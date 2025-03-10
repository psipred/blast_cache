"""cache_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rest_framework.urlpatterns import format_suffix_patterns

from blast_cache_app import api

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^blast_cache/', include('blast_cache_app.urls')),
    # url(r'^blast_cache/$',
    #     api.CacheDetails.as_view(),
    #     name="cache"),
    # url(r'^blast_cache/(?P<md5>\S{32})$',
    #     api.CacheDetails.as_view(),
    #     name="cacheDetail"),
    url(r'^blast_cache/entry/$', api.EntryDetail.as_view(), name="entryDetail"),
    url(r'^blast_cache/entry/(?P<md5>\S{32})$', api.EntryDetail.as_view(),
        name="entryDetail"),
    url(r'^blast_cache/list$', api.FullList.as_view(), name="fullList"),
    url(r'^blast_cache/list/(?P<md5>\S{32})$', api.EntryList.as_view(),
        name="entryList"),

    url(r'^login/$', auth_views.LoginView),
    url(r'^logout/$', auth_views.LogoutView),
    url(r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html', ])
