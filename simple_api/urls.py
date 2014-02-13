# coding: utf-8

try:
    from django.conf.urls import url, patterns
except ImportError:
    from django.conf.urls.defaults import url, patterns

import views

urlpatterns = patterns('',
    url(r'^(?:test/)?$', views.test, name="simple_api_test"),
    url(r'^manual/$', views.manual, name="manual"),
    url(r'^(?P<model_class>.*?)__(?P<method>.*?)/$', views.model_action, name="simple_model_methods"),
    url(r'^(?P<method>.*?)/$', views.action, name="simple_api_methods"),
)
