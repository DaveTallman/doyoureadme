# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='doyoureadme',
    version='0.0.1',
    description='Scraper in python3 for fan-fiction writers to check reader stats',
    long_description=readme,
    author='C. Dave Tallman',
    author_email='davetallman@msn.com',
    url='https://github.com/DaveTallman/doyoureadme',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

