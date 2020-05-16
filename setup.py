import os
from importlib.machinery import SourceFileLoader

import setuptools
from pkg_resources import parse_requirements

module_name = 'throttler'

module = SourceFileLoader(
    module_name, os.path.join(module_name, '__init__.py')
).load_module()


def read(filename):
    with open(filename) as file:
        return file.read()


def load_requirements(filename: str) -> list:
    requirements = []
    for req in parse_requirements(read(filename)):
        extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
        requirements.append(
            '{}{}{}'.format(req.name, extras, req.specifier)
        )
    return requirements


setuptools.setup(
    name=module_name,
    version=module.__version__,
    author=module.__author__,
    author_email=module.__email__,
    license=module.__license__,
    description=module.__doc__,
    platforms='all',
    long_description=read('readme.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/uburuntu/throttler',
    download_url='https://github.com/uburuntu/throttler/archive/master.zip',
    packages=['throttler'],
    requires_python='>=3.6',
    install_requires=[],
    extras_require={'dev': load_requirements('requirements-dev.txt')},
    keywords=['throttle', 'rate limit'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Typing :: Typed',
    ],
)
