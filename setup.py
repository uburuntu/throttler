import importlib.util
import os
import sys

import setuptools
from pkg_resources import parse_requirements


def read(filename: str) -> str:
    with open(filename, encoding='utf-8') as file:
        return file.read()


def get_module(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(name, '__init__.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_requirements(filename: str) -> list:
    requirements = []
    for req in parse_requirements(read(filename)):
        extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
        requirements.append(
            '{}{}{}'.format(req.name, extras, req.specifier)
        )
    return requirements


module_name = 'throttler'
module = get_module(module_name)

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
    url='https://github.com/uburuntu/{}'.format(module_name),
    download_url='https://github.com/uburuntu/{}/archive/master.zip'.format(module_name),
    packages=setuptools.find_packages(exclude=['examples', 'tests']),
    include_package_data=True,
    install_requires=[],
    extras_require={'dev': load_requirements('requirements-dev.txt')},
    keywords=['asyncio', 'aio-throttle', 'aiothrottle', 'aiothrottler', 'aiothrottling',
              'asyncio-throttle', 'rate-limit', 'rate-limiter', 'throttling', 'throttle', 'throttler'],
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
