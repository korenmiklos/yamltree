# encoding: utf-8
from setuptools import setup, find_packages
import sys, os

from yamltree import __version__

setup(
	name='yamltree',
	version=__version__,
	description="Parse a directory of YAML documents into a tree-like Python object.",
	long_description=open("README.markdown").read(),
	classifiers=[
	],
	keywords='yaml',
	author='Miklós Koren',
	author_email='miklos.koren@gmail.com',
	url='https://github.com/korenmiklos/yamltree',
	license='MIT',
	#packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	py_modules=['yamltree'],
	#include_package_data=True,
	zip_safe=False,
	install_requires=[
		'pyyaml'
	],
	extras_require={'Better slugs': 'unidecode'},
)
