# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read_file(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='django-cachedpaginator',
    version=__import__('django_cachedpaginator').__version__,
    description="Paginator that caches pages automatically.",
    long_description=read_file('README.md'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Environment :: Web Environment',
    ],
    keywords=['paginator', 'django', 'cache'],
    include_package_data=True,
    platforms=['OS Independen'],
    author='Arsham Shirvani',
    author_email='arshamshirvani@gmail.com',
    url='http://github.com/arsham/django-cachedpaginator',
    license='BSD',
    packages=find_packages(),
    zip_safe=False,
)
