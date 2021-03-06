# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

#def read(fname):
#    try:
#        return open(os.path.join(os.path.dirname(__file__), fname)).read()
#    except IOError:
#        return ''

setup(
    name="simple_api",
    version=__import__('simple_api').__version__,
    description=open(os.path.join(os.path.dirname(__file__), "DESCRIPTION")).read(),
    license="The MIT License (MIT)",
    keywords="django, api, simple_api",

    author="Alexander Yudkin",
    author_email="san4ezy@gmail.com",

    maintainer='Alexander Yudkin',
    maintainer_email='san4ezy@gmail.com',

    url="http://yudkin.com.ua",
    packages=find_packages(exclude=["tests.*", "tests"]),
    #package_data=find_package_data("simple_api",only_in_packages=False),
    classifiers=[
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
