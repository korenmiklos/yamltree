YAML Tree
=========

Reading hierarchical data from the file system through folders and YAML files.

About
-----

YAMLTree is a Python library to load hierarchical data from a collection of YAML files, which are organized in the file system in a tree structure. The key idea is to make the file system transparent to the user and address each piece of data in a unique, intuitive Python object.

Example
-------

Suppose you have a folder with the following structure:

	papers
		published
			paper1.yaml
				title: A Treatise on the Family
				author: Gary Becker
			paper2.yaml
		working_papers
			paper3.yaml

You can access the data in Python easily:

	from yamltree import YAMLTree

	papers = YAMLTree('papers')

	print papers.published[1].author
	print papers.published.paper1.title
	for paper in papers.published:
		print paper.title

Installing YAML Tree
--------------------

Install from source on Github:

	git clone https://github.com/korenmiklos/yamltree.git
	cd yamltree
	python setup.py install

Usage
-----

Each YAMLTree is a tree of nodes. A YAMLTree node can be one of two types:

1. a container of other nodes
2. a literal.

The node may be stored as a folder, as a YAML document, or as a dictionary or list within the YAML document. This is completely transparent to the user, as it does not affect the node's interface.

Containers
~~~~~~~~~~

Containers are iterable:

	for paper in papers.published:
		print paper.title

Containers can also be addressed in a number of ways:

	paper = papers.published.paper1
	for field in paper:
		print field
	print paper["title"]
	print paper.title

Folder and file names are converted to an appropriate slug so that attribute addressing works properly.

	title: A Treatise on Family
	corresponding author: Gary Becker

becomes

	paper.title = "A Treatise on Family"
	paper.corresponding_author = "Gary Becker"

Literals
~~~~~~~~

The leaves of the tree are Python literals, such as strings, integers or floats.
