import os
from setuptools import setup, find_packages

NAME = 'django-megamacros'
PACKAGES = find_packages(exclude=["tests"])
DESCRIPTION = "A macro system for Django's template language"
URL = "https://github.com/potatolondon/django-megamacros"
LONG_DESCRIPTION = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
AUTHOR = 'Potato London Ltd.'

setup(
    name=NAME,
    version='0.1 alpha',
    packages=PACKAGES,
    author=AUTHOR,
    author_email='mail@p.ota.to',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=["django", "templating", "macro"],
    url=URL,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
