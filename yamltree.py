#!/usr/bin/env python
# encoding: utf-8

'''
'''


__docformat__ = 'markdown en'
__author__ = "Miklós Koren <miklos.koren@gmail.com>"
__version__ = "0.1.0"

import re

SLUG_REGEX = re.compile('^[A-Za-z_]\w{0,64}$')
RESERVED_WORDS = ['get_tree', 'get_data', 'set_data', 'get_absolute_url'
                            'children_as_dictionary']
RESERVED_WORDS_REGEX = re.compile('^__[A-Za-z]+__$')

try:
    import unidecode
    def slugify(verbose_name):
        return re.sub(r'\W+','_',unidecode.unidecode(verbose_name).lower())
except:
    def slugify(verbose_name):
        return re.sub(r'\W+','_',verbose_name.lower())

def parse_object(name, obj):
    '''
    Parse a python object into a YAML tree.

    >>> root = parse_object('root', {'a': 1, 'b': {'c': 2, 'd': 3}})
    >>> root.__name__
    'root'
    >>> print root.a
    1
    >>> print root.b.c
    2
    >>> print root.b.d
    3
    >>> lst = parse_object('list', [1, 2, 3])
    >>> print lst.id0
    1
    >>> print lst.id1
    2
    >>> print lst.id2
    3

    '''
    if isinstance(obj, dict):
        root = ContainerNode(name)
        for (key, value) in obj.iteritems():
            node = parse_object(key, value)
            root.add_child(node)
        return root
    elif isinstance(obj, list):
        root = ContainerNode(name)
        for (key, value) in zip(range(len(obj)), obj):
            node = parse_object('id%s' % key, value)
            root.add_child(node)
        return root
    else:
        node = LiteralNode(name)
        node.set_data(obj)
        return node

class Node(object):
    '''
    Represents a YAMLTree node. Nodes can be either of two types:
        1. container of other nodes
        2. literal

    Each node has a unique URL (not yet implemented).
    '''

    def __init__(self, name, parent = None):
        slug = slugify(name)
        if (not SLUG_REGEX.match(slug)) or (slug in RESERVED_WORDS) or (RESERVED_WORDS_REGEX.match(slug)):
            raise NameError, '%s is not an admissible name' % slug
        self.__name__ = slug
        self.__url__ = '%s/%s' % ('', name)
        self.__meta__ = dict(verbose_name=name)
        self.__data__ = None
        self.__children__ = None

    def get_absolute_url(self):
        return self.__url__


class YAMLTree(Node):
    def __init__(self, root):
        pass

class LiteralNode(Node):
    def get_data(self):
        return self.__data__

    def set_data(self, value):
        self.__data__ = unicode(value)

    def __unicode__(self):
        return unicode(self.get_data())

    def __str__(self):
        return self.__unicode__()

class ContainerNode(Node):
    '''
    Children of ContainerNode can be addressed as

        node['child']
        node.child

    To add a child, 

        node.add_child(other_node)

    Container nodes are also iterable:

        for child in node:
            pass

    '''
    def __init__(self, name, parent = None):
        super(ContainerNode, self).__init__(name, parent)
        self.__children__ = {}

    def add_child(self, node):
        if node.__name__ in [child.__name__ for child in self]:
            raise NameError, 'Children must have unique names'
        self.__children__[node.__name__] = node

    def __iter__(self):
        return iter(self.__children__.values())

    def __len__(self):
        '''
        Return number of child nodes.
        '''
        return len(self.__children__)

    def children_as_dictionary(self):
        return self.__children__

    def __getattr__(self, name):
        if name in self.__children__:
            return self.__children__[name]
        else:
            raise KeyError

    def __getitem__(self, key):
        if key in self.__children__:
            return self.__children__[key]
        else:
            raise KeyError

    def set_data(self, *args):
        raise TypeError, 'Container nodes cannot handle data directly.'
    def get_data(self, *args):
        raise LookupError, 'Container nodes cannot handle data directly.'

