*********
SimpleAPI
*********

SimpleAPI is a Python package for making application programm interface. Everyone can make the API methods just like the Django Models.

`Github repo <https://github.com/san4ezy/simple_api>`_

Installation
============

Install using pip::

    pip install simple_api

...or clone the project from github::

    https://github.com/san4ezy/simple_api.git

1. Add ``simple_api`` application to ``INSTALLED_APPS`` settings::

    INSTALLED_APPS = (
        ...
        'simple_api',
    )

2. Import package to "urls.py" and connect SimpleAPI to your project::

    import simple_api
    simple_api.connect()

3. Add the SimpleAPI pattern to your ``urlpatterns``::

    url(r'api/', include(simple_api.urls)),

4. Make file with name ``api_models.py`` into your application, import the SimpleAPI package and make custom classes for your API

Example
=======

Let's take a look at a quick example how to use SimpleAPI.

We'll create some classes, which makes methods for your project`s API using SimpleAPI.

Let`s edit "api_models.py"::

    import simple_api
    from main.models import *

    # This class makes a url http://your-domain/api/getprojects/
    class GetProjects(simple_api.SimpleAPI):
        filter = simple_api.CharVariable(blank=True, default='active', choices=['all', 'active', 'not_active', ])
        mode = simple_api.CharVariable(blank=True, default='object', choices=['object', 'name', ])
        description = u"Getting projects data"

        def method(self):
            queryset = None
            if self.filter.case(0):
                queryset = Project.objects.all()
            elif self.filter.case(1):
                queryset = Project.objects.filter(active=True)
            elif self.filter.case(2):
                queryset = Project.objects.filter(active=False)
            if self.mode.case(0):
                return queryset
            elif self.mode.case(1):
                return [(x.pk, x.name, ) for x in queryset]

    # This class makes a url: http://your-domain/api/projects__<method>/ , where "method" should be "get", "make", "edit" or "delete".
    class Projects(simple_api.ModelAPI):
        model = Project
