# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in model_generator/__init__.py
from model_generator import __version__ as version

setup(
	name='model_generator',
	version=version,
	description='Generate models to different languages based on Doctype',
	author='Assem Marwan',
	author_email='assem905@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
