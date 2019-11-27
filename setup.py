# -*- coding: utf-8 -*-

from codecs import open

from setuptools import find_packages, setup

with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='divebomb',
    version='1.1.2',
    description='divebomb dive classification algorithm',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Alex Nunes',
    include_package_data=True,
    author_email='alex.et.nunes@gmail.com',
    url='https://github.com/ocean-tracking-network/divebomb',
    download_url='https://github.com/ocean-tracking-network/divebomb',
    license='GPLv2',
    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'pandas',
        'numpy',
        'plotly',
        'netcdf4',
        'peakutils',
        'scikit-learn',
        'xarray'
    ],
    packages=find_packages(exclude=('tests', 'docs'))
)
