# encoding: utf-8
from setuptools import setup, find_packages
import sys, os

from datatree import __version__

setup(
	name='datatree',
	version=__version__,
	description="Parse a directory of structured documents (YAML, JSON, CSV) into a tree-like Python object.",
	long_description=open("README.markdown").read(),
	classifiers=[
	],
	keywords='yaml',
	author='Miklós Koren',
	author_email='miklos.koren@gmail.com',
	url='https://github.com/korenmiklos/datatree',
	license='MIT',
	#packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	py_modules=['datatree'],
	#include_package_data=True,
	zip_safe=False,
	install_requires=[
		'pyyaml'
	],
	extras_require={'Better slugs': 'unidecode'},
)
