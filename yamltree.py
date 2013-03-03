#!/usr/bin/env python
# encoding: utf-8

'''
'''


__docformat__ = 'markdown en'
__author__ = "Miklós Koren <miklos.koren@gmail.com>"
__version__ = "0.2.0"

import re
import yaml
import json
import fnmatch
import os

SLUG_REGEX = re.compile('^[A-Za-z_]\w{0,64}$')
RESERVED_WORDS = ['get_tree', 'get_data', 'set_data', 'get_absolute_url'
                            'children_as_dictionary']
RESERVED_WORDS_REGEX = re.compile('^__[A-Za-z]+__$')
YAML_FILE = re.compile('^.+\.ya?ml$')
EXCLUDED = re.compile('^\..*$')

try:
    import unidecode
    def slugify(verbose_name):
        slug = re.sub(r'\W+','_',unidecode.unidecode(verbose_name).lower())
        if not SLUG_REGEX.match(slug):
            slug = '_'+slug
        return slug 
except:
    def slugify(verbose_name):
        slug = re.sub(r'\W+','_',verbose_name.lower())
        if not SLUG_REGEX.match(slug):
            slug = '_'+slug
        return slug 

def read_and_parse_yaml_files(parent, path, exclude=[], primary_keys=[]):
    fullpath = os.path.normpath(path)
    for entry in os.listdir(fullpath):
        if not any([pattern.match(entry) for pattern in exclude]): 
            fullname = os.path.join(fullpath, entry)
            if os.path.isdir(fullname):
                node = ContainerNode(entry) 
                read_and_parse_yaml_files(node, fullname, exclude, primary_keys)
                parent.add_child(node)
            elif os.path.isfile(fullname):
                if YAML_FILE.match(entry):
                    shortname, ext = os.path.splitext(entry)
                    node = parse_yaml(shortname, open(fullname, 'r').read(), primary_keys)
                    parent.add_child(node)

def parse_object(name, obj, primary_keys=[]):
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
    if isinstance(primary_keys, basestring):
        primary_keys = [primary_keys]
    if isinstance(obj, dict):
        root = ContainerNode(name)
        for (key, value) in obj.iteritems():
            node = parse_object(key, value, primary_keys)
            root.add_child(node)
        return root
    elif isinstance(obj, list):
        root = ContainerNode(name)
        for (key, value) in zip(range(len(obj)), obj):
            nodename = 'id%s' % key
            for field in primary_keys:
                try:
                    nodename = value[field]
                    break
                except:
                    continue
            node = parse_object(nodename, value, primary_keys)
            root.add_child(node)
        return root
    else:
        node = LiteralNode(name)
        node.set_data(obj)
        return node

def parse_yaml(name, stream, primary_keys=[]):
    '''
    Parse a YAML stream into a YAML tree.
    '''
    doc = list(yaml.load_all(stream))
    if len(doc)==1:
        return parse_object(name, doc[0], primary_keys)
    else:
        return parse_object(name, doc, primary_keys)

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
            raise NameError, '%s is not an admissible name. node = %s' % (slug, name)
        self.__parent__ = parent
        self.__name__ = slug
        self.__meta__ = dict(verbose_name=name)
        self.__data__ = None
        self.__children__ = None

    def __nonzero__(self):
        # default object is True
        return True

    def get_absolute_url(self):
        if self.__parent__ is None:
            return '/'
        elif self.__parent__.get_absolute_url() == '/':
            return '/%s' % self.__name__
        else:
            return '%s/%s' % (self.__parent__.get_absolute_url(), self.__name__)

    def get_relative_url(self, other):
        return os.path.relpath(self.get_absolute_url(), other.get_absolute_url())

    def set_metadata(self, **kwargs):
        for (key, value) in kwargs.iteritems():
            self.__meta__[key] = value

    def get_metadata(self, key):
        return self.__meta__[key]

    def get_verbose_name(self):
        return self.__meta__['verbose_name']


class LiteralNode(Node):
    def __nonzero__(self):
        # literal node is True if has data
        return self.__data__ is not None

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
        # store ordering in __meta__ so that applications can change that if they want
        self.__meta__['ordering'] = []

    def __nonzero__(self):
        # container node is True if has children
        return len(self.__children__)

    def add_child(self, node):
        if node.__name__ in [child.__name__ for child in self]:
            raise NameError, 'Children must have unique names. node = %s' % self.get_absolute_url()
        if node.__parent__ is not None:
            raise ValueError, 'Child cannot have multiple parents. node = %s' % self.get_absolute_url()
        self.__children__[node.__name__] = node
        self.__meta__['ordering'].append(node.__name__)
        node.__parent__ = self

    def __iter__(self):
        return iter([self.__children__[key] for key in self.__meta__['ordering']])

    def __len__(self):
        '''
        Return number of child nodes.
        '''
        return len(self.__children__)

    def children_as_dictionary(self):
        return self.__children__

    def get_dictionary(self):
        output = {}
        for key, value in self.__children__.iteritems():
            try:
                output[key] = value.get_dictionary()
            except:
                output[key] = value.get_data()
        return output

    def __unicode__(self):
        return json.dumps(self.get_dictionary())

    def __str__(self):
        return self.__unicode__()

    def __getattr__(self, name):
        if name.lower() in self.__children__:
            return self.__children__[name.lower()]
        else:
            raise KeyError, '%s is not a child node. node = %s' % (name, self.get_absolute_url())

    def __getitem__(self, key):
        return self.__getattr__(key)

    def set_data(self, *args):
        raise TypeError, 'Container nodes cannot handle data directly. node = %s' % self.get_absolute_url()
    def get_data(self, *args):
        raise LookupError, 'Container nodes cannot handle data directly. node = %s' % self.get_absolute_url()

class YAMLTree(ContainerNode):
    def __init__(self, root, exclude=[], primary_keys=[]):
            self.path = os.path.normpath(root)
            self.exclude = []
            for pattern in exclude:
                self.exclude.append(re.compile(pattern))
            super(YAMLTree, self).__init__('root')
            read_and_parse_yaml_files(self, self.path, self.exclude, primary_keys)

    def get_by_url(self, url):
        url = os.path.normpath(url)
        parts = url.split('/')
        parts = [part for part in parts if not part=='']
        def lookup(node, child):
            return node[child]
        return reduce(lookup, [self]+parts)


