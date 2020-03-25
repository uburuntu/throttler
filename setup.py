import setuptools

import throttler


def read(filename):
    with open(filename) as file:
        return file.read()


setuptools.setup(
    name='throttler',
    version=throttler.__version__,
    author='uburuntu',
    author_email='bekbulatov.ramzan@ya.ru',
    url='https://github.com/uburuntu/throttler',
    description='Zero-dependency Python package for simple throttling with asyncio support',
    long_description=read('readme.md'),
    long_description_content_type="text/markdown",
    download_url='https://github.com/uburuntu/throttler/archive/master.zip',
    packages=['throttler'],
    requires_python='>=3.6',
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
