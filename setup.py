#!/usr/bin/env python
import codecs
import os
import sys

from setuptools import setup, find_packages


ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

requirements = [
    'requests >= 2.5.2, != 2.11.0',
    'six >= 1.4.0',
    'websocket-client >= 0.32.0',
    'docker-pycreds >= 0.2.1'
]

if sys.platform == 'win32':
    requirements.append('pypiwin32 >= 219')

extras_require = {
    ':python_version < "3.5"': 'backports.ssl_match_hostname >= 3.5',
    # While not imported explicitly, the ipaddress module is required for
    # ssl_match_hostname to verify hosts match with certificates via
    # ServerAltname: https://pypi.python.org/pypi/backports.ssl_match_hostname
    ':python_version < "3.3"': 'ipaddress >= 1.0.16',
}

version = None
exec(open('docker/version.py').read())

with open('./test-requirements.txt') as test_reqs_txt:
    test_requirements = [line for line in test_reqs_txt]


long_description = ''
try:
    with codecs.open('./README.rst', encoding='utf-8') as readme_rst:
        long_description = readme_rst.read()
except IOError:
    # README.rst is only generated on release. Its absence should not prevent
    # setup.py from working properly.
    pass

setup(
    name="docker",
    version=version,
    description="A Python library for the Docker Engine API.",
    long_description=long_description,
    url='https://github.com/docker/docker-py',
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require=extras_require,
    zip_safe=False,
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
    maintainer='Joffrey F',
    maintainer_email='joffrey@docker.com',
)
