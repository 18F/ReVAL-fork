import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="ReVal",
    version="v0.7.0",
    packages=find_packages(),
    include_package_data=True,
    license="CC0-1.0",
    description="Django app to upload, validate, review, and accept data files",
    long_description=README,
    url="https://github.com/18F/ReVAL",
    author="18F",
    author_email="data-federation@gsa.gov",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",  # example license
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: Public Domain",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    ],
    install_requires=[
        "django >3.2, <=3.3",
        "djangorestframework",
        "dj-database-url",
        "goodtables",
        "json_logic_qubit",
        "psycopg2-binary",
        "pyyaml",
        "requests",
    ],
)
