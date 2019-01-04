import os
from setuptools import setup, find_packages


def get_version():
    with open(os.path.join('elasticmagic', 'version.py'), 'rt') as version_file:
        return version_file.readline().split('=')[1].strip().strip("'\"")


setup(
    name="elasticmagic",
    version=get_version(),
    author="Alexander Koval",
    author_email="kovalidis@gmail.com",
    description=("Python orm for elasticsearch."),
    license="Apache License 2.0",
    keywords="elasticsearch dsl",
    url="https://github.com/anti-social/elasticmagic",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "elasticsearch",
        "python-dateutil",
    ],
    extras_require={
        "geo": [
            "python-geohash",
        ],
        "async": [
            "elasticsearch-py-async",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
