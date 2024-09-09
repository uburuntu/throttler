"""
Create the Python package
"""

import sys
import os

from setuptools import setup, find_packages

from src.async_flow_control import __version__, __license__

MIN_PYTHON_VERSION = (3, 8)
PKGNAME = 'async-flow-control'
GITHUB_URL = 'https://github.com/paulovn/' + PKGNAME
DESC = '''
Throttle tasks to spread execution across time and implement flow control, in an asyncio environment
'''

# --------------------------------------------------------------------


def requirements(filename='requirements.txt'):
    '''Read the requirements file'''
    pathname = os.path.join(os.path.dirname(__file__), filename)
    with open(pathname, 'r') as f:
        return [line.strip() for line in f if line.strip() and line[0] != '#']


# --------------------------------------------------------------------


if sys.version_info < MIN_PYTHON_VERSION:
    sys.exit('**** Sorry, {} {} needs at least Python {}'.format(
        PKGNAME, __version__, '.'.join(map(str, MIN_PYTHON_VERSION))))


setup_args = dict(
    # Metadata
    name=PKGNAME,
    version=__version__,
    description=DESC.strip(),
    long_description=DESC,
    long_description_content_type="text/markdown",
    license=__license__,
    url=GITHUB_URL,
    download_url=GITHUB_URL + '/tarball/v' + __version__,
    author='Paulo Villegas',
    author_email='paulo.vllgs@gmail.com',

    # Locate packages
    packages=find_packages('src'),  # [ PKGNAME ],
    package_dir={'': 'src'},

    # Optional requirements
    extras_require={
        'test': ['nose', 'coverage', 'pytest', 'pytest-asyncio'],
    },


    include_package_data=False,
    
    # pytest requirements
    tests_require=['pytest', 'pytest-asyncio'],

    # More metadata
    keywords=['throttle', 'throttling', 'rate control', 'asyncio',
              'rate-limit', 'concurrency-limit'],
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries'
    ]
)


if __name__ == '__main__':
    setup(**setup_args)
