# -*- coding: utf-8 -*-
import unittest as ut 
import datatree as module
import os
from shutil import rmtree
import yaml
import re

# upgrading to Python 3, where all strings are unicode
def unicode(x):
    return str(x)

class TestYAMLLoader(ut.TestCase):
    def setUp(self):
        os.makedirs('testdata/folder1')
        os.makedirs('testdata/folder2')
        doc0 = open('testdata/document.yaml', 'w')
        doc1 = open('testdata/folder1/document.yaml', 'w')
        doc2 = open('testdata/folder2/document.yaml', 'w')
        doc3 = open('testdata/folder2/list.yaml', 'w')
        notadoc = open('testdata/notadoc.txt', 'w')
        excluded = open('testdata/.excluded.yaml', 'w')
        data = dict(title='Test document', content='Test data')
        
        for stream in [doc0, doc1, doc2, notadoc, excluded]:
            yaml.dump(data, stream)
            stream.close()

        stream = doc3
        yaml.dump([dict(id='slug1', content=1), dict(id='slug2', content=2)], stream)
        stream.close()

    def tearDown(self):
        rmtree('testdata')

    def test_doc0_parsed(self):
        root = module.FolderReader('testdata').read()
        self.assertIsInstance(root.document, module.ContainerNode)

    def test_doc1_parsed(self):
        root = module.FolderReader('testdata').read()
        self.assertEqual(unicode(root.folder1.document), '{"content": "Test data", "title": "Test document"}')

    def test_doc2_parsed(self):
        root = module.FolderReader('testdata').read()
        self.assertEqual(unicode(root.folder2.document), '{"content": "Test data", "title": "Test document"}')

    def test_notadoc_notparsed(self):
        root = module.FolderReader('testdata').read()
        self.failIf('notadoc' in [child.__name__ for child in root])

    def test_excluded_notparsed(self):
        root = module.FolderReader('testdata', exclude=[re.compile('^\..*$')]).read()
        self.failIf('_excluded' in [child.__name__ for child in root])

    def test_get_top(self):
        tree = module.DataTree('testdata', exclude=['^\..*$'])
        self.assertEqual(tree.get_by_url('/folder1'), tree.root.folder1)

    def test_get_by_url(self):
        tree = module.DataTree('testdata', exclude=['^\..*$'])
        self.assertEqual(tree.get_by_url('/folder1/document/title'), tree.root.folder1.document.title)

    def test_get_by_unnormalized_url(self):
        tree = module.DataTree('testdata', exclude=['^\..*$'])
        self.assertEqual(tree.get_by_url('/folder1/../folder2/document/title'), tree.root.folder2.document.title)

    def test_trailing_slash(self):
        tree = module.DataTree('testdata', exclude=['^\..*$'])
        self.assertEqual(tree.get_by_url('/folder1/document/title/'), tree.root.folder1.document.title)

    def test_get_by_own_url(self):
        tree = module.DataTree('testdata', exclude=['^\..*$'])
        self.assertEqual(tree.get_by_url(tree.root.folder1.document.title.get_absolute_url()), tree.root.folder1.document.title)

    def test_unknown_url_fails(self):
        tree = module.DataTree('testdata', exclude=['^\..*$'])
        def callable():
            tree.get_by_url('/folder3/document')
        self.assertRaises(LookupError, callable)

    def test_primary_keys_are_passed(self):
        tree = module.DataTree('testdata', primary_keys=['id', 'slug'])
        self.assertIsInstance(tree.root.folder2.list.slug1, module.ContainerNode)

class TestParents(ut.TestCase):
    def test_cannot_have_more_parents(self):
        father = module.ContainerNode('father')
        mother = module.ContainerNode('mother')
        child = module.LiteralNode('child')

        father.add_child(child)
        def callable():
            mother.add_child(child)
        self.assertRaises(ValueError, callable)

    def test_root_url(self):
        father = module.ContainerNode('father')
        self.assertEqual(father.get_absolute_url(), '/')

    def test_child_url(self):
        father = module.ContainerNode('father')
        child = module.LiteralNode('child')
        father.add_child(child)
        self.assertEqual(child.get_absolute_url(), '/child')

    def test_relative_url_down(self):
        father = module.ContainerNode('father')
        child = module.ContainerNode('child')
        grandchild = module.LiteralNode('grandchild')
        father.add_child(child)
        child.add_child(grandchild)
        self.assertEqual(grandchild.get_relative_url(father), 'child/grandchild')

    def test_relative_url_up(self):
        father = module.ContainerNode('father')
        child = module.ContainerNode('child')
        grandchild = module.LiteralNode('grandchild')
        father.add_child(child)
        child.add_child(grandchild)
        self.assertEqual(child.get_relative_url(grandchild), '..')


class TestYAMLReader(ut.TestCase):
    def setUp(self):
        os.makedirs('testdata')
        doc0 = open('testdata/root.yaml', 'w')
        doc1 = open('testdata/multidoc.yaml', 'w')
        doc2 = open('testdata/layered.yaml', 'w')

        doc0.write('')
        doc1.write('''
---
name: The Set of Gauntlets 'Pauraegen'
description: >
    A set of handgear with sparks that crackle
    across its knuckleguards.
---
name: The Set of Gauntlets 'Paurnen'
description: >
   A set of gauntlets that gives off a foul,
   acrid odour yet remains untarnished.
            ''')
        doc2.write('''
            a: 1
            b:
                c: 2
                d: 3
        ''')

        for stream in [doc0, doc1, doc2]:
            stream.close()

    def tearDown(self):
        rmtree('testdata')

    def test_root_node(self):
        node = module.YAMLReader('testdata/root.yaml').read()
        self.assertIsInstance(node, module.ContainerNode)
 
    def test_multi_document(self):
        node = module.YAMLReader('testdata/multidoc.yaml').read()
        self.assertIsInstance(node, module.ContainerNode)
 
    def test_multiple_layers(self):
        root = module.YAMLReader('testdata/layered.yaml').read()
        self.assertListEqual([root.a.get_data(), root.b.c.get_data(), root.b.d.get_data()], [u'1', u'2', u'3'])

class TestJSONReader(ut.TestCase):
    def setUp(self):
        os.makedirs('testdata')
        doc0 = open('testdata/root.json', 'w')
        doc2 = open('testdata/layered.json', 'w')

        doc0.write('')
        doc2.write('{"a": 1, "b": {"c": 2, "d": 3}}')

        for stream in [doc0, doc2]:
            stream.close()

    def tearDown(self):
        rmtree('testdata')

    def test_root_node(self):
        node = module.JSONReader('testdata/root.json').read()
        self.assertIsInstance(node, module.ContainerNode)
 
    def test_multiple_layers(self):
        root = module.JSONReader('testdata/layered.json').read()
        self.assertListEqual([root.a.get_data(), root.b.c.get_data(), root.b.d.get_data()], [u'1', u'2', u'3'])

class TestCSVReader(ut.TestCase):
    def setUp(self):
        os.makedirs('testdata')
        doc0 = open('testdata/root.csv', 'wt', encoding='utf-8')

        doc0.write(u'''a,b,c
1,2,3
4,5,6
ő,ű,á''')
        doc0.close()

    def tearDown(self):
        rmtree('testdata')

    def test_root_node(self):
        node = module.CSVReader('testdata/root.csv').read()
        self.assertDictEqual(node.id0.get_dictionary(), dict(a=u'1', b=u'2', c=u'3'))

    def test_unicode(self):
        node = module.CSVReader('testdata/root.csv').read()
        self.assertDictEqual(node.id2.get_dictionary(), dict(a=u'ő', b=u'ű', c=u'á'))

class TestDictParser(ut.TestCase):
    def test_root_node(self):
        node = module.parse_object('root', {})
        self.assertIsInstance(node, module.ContainerNode)

    def test_container_node(self):
        node = module.parse_object('root', dict(a=1))
        self.assertIsInstance(node, module.ContainerNode)

    def test_container_node_child(self):
        node = module.parse_object('root', dict(a=1))
        self.assertIsInstance(node.a, module.LiteralNode)

    def test_list_node(self):
        node = module.parse_object('root', [dict(a=1), dict(b=1)])
        self.assertIsInstance(node, module.ContainerNode)

    def test_primary_key(self):
        node = module.parse_object('root', [1,2, [dict(slug='slug1', content=1), 
            dict(slug='slug2', content=2)]], primary_keys='slug')
        self.assertEqual(node.id2.slug1.content.get_data(), u'1')

    def test_lower_level_primary_key(self):
        node = module.parse_object('root', [dict(slug='slug1', content=1), 
            dict(slug='slug2', content=2)], primary_keys='slug')
        self.assertEqual(node.slug1.content.get_data(), u'1')

    def test_multiple_primary_keys(self):
        node = module.parse_object('root', [dict(slug='slug1', content=1), 
            dict(name='slug2', content=2)], primary_keys=['slug', 'name'])
        self.assertEqual(node.slug1.content.get_data(), u'1')
        self.assertEqual(node.slug2.content.get_data(), u'2')

    def test_missing_key(self):
        node = module.parse_object('root', [1, 2], primary_keys='slug')
        self.assertEqual(node.id0.get_data(), u'1')

    def test_primary_key_is_slugified(self):
        node = module.parse_object('root', [dict(slug='two words', content=1),],
         primary_keys='slug')
        self.assertEqual(node.two_words.content.get_data(), u'1')

    def test_literal_node(self):
        node = module.parse_object('root', 'test')
        self.assertIsInstance(node, module.LiteralNode)
        self.assertEqual(node.get_data(), 'test')

    def test_numeric_node(self):
        node = module.parse_object('root', 5)
        self.assertIsInstance(node, module.LiteralNode)
        self.assertEqual(node.get_data(), '5')

    def test_multiple_layers(self):
        root = module.parse_object('root', {'a': 1, 'b': {'c': 2, 'd': 3}})
        self.assertListEqual([root.a.get_data(), root.b.c.get_data(), root.b.d.get_data()], [u'1', u'2', u'3'])


class TestInterface(ut.TestCase):
    def test_numerical_name(self):
        node = module.LiteralNode('1')
        self.assertEqual(node.__name__, u'_1')

    def test_accented_name(self):
        node = module.LiteralNode(u'árvíztűrő')
        self.assertEqual(node.__name__, u'arvizturo')

    def test_uppercase_name(self):
        node = module.LiteralNode('Alpha')
        self.assertEqual(node.__name__, 'alpha')

    def test_space_name(self):
        node = module.LiteralNode('A &@#$!B')
        self.assertEqual(node.__name__, 'a_b')

    def test_verbose_name(self):
        node = module.LiteralNode(u'árvíztűrő')
        self.assertEqual(node.__meta__['verbose_name'], u'árvíztűrő')

    def test_get_verbose_name(self):
        node = module.LiteralNode(u'árvíztűrő')
        self.assertEqual(node.get_verbose_name(), u'árvíztűrő')

    def test_node_returns_string(self):
        node = module.LiteralNode('test')
        node.set_data(5)
        self.assertEqual(node.get_data(),str(5))

    def test_get_data_and_string(self):
        node = module.LiteralNode('test')
        node.set_data(5)
        self.assertEqual(node.get_data(),unicode(node))

    def test_metadata_accepts_kwargs(self):
        node = module.LiteralNode('test')
        try:
            node.set_metadata(priority=5)
        except:
            self.fail    

    def test_metadata_not_accept_args(self):
        node = module.LiteralNode('test')
        def callable():
            node.set_metadata(5)
        self.assertRaises(Exception, callable)

    def test_set_and_get_metadata(self):
        node = module.LiteralNode('test')
        node.set_metadata(priority=5, language='hu')
        self.assertEqual(node.get_metadata('priority'), 5)
        self.assertEqual(node.get_metadata('language'), 'hu')

class TestTrueism(ut.TestCase):
    def test_true_container(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        node.add_child(a)
        self.failUnless(node)

    def test_false_container(self):
        node = module.ContainerNode('test')
        self.failIf(node)

    def test_true_literal(self):
        node = module.LiteralNode('test')
        node.set_data('a')
        self.failUnless(node)

    def test_false_literal(self):
        node = module.LiteralNode('test')
        self.failIf(node)

    def test_empty_string(self):
        node = module.LiteralNode('test')
        node.set_data("")
        self.failIf(node)

class TestExceptions(ut.TestCase):
    def test_long_name_rejected(self):
        def callable():     
            node = module.LiteralNode('A'*999)
        self.assertRaises(NameError, callable)

    def test_nonunique_name_rejected(self):
        def callable():
            node = module.ContainerNode('test')
            a = module.LiteralNode('a')
            b = module.LiteralNode('a')
            node.add_child(a)
            node.add_child(b)
        self.assertRaises(NameError, callable)

    def test_parent_accepts_no_data(self):
        node = module.ContainerNode('test')
        self.assertRaises(TypeError,node.set_data,5)

    def test_parent_returns_no_data(self):
        node = module.ContainerNode('test')
        self.assertRaises(LookupError,node.get_data)

    def test_cannot_call_node_reserved_word(self):
        RESERVED_WORDS = ['__init__','__data__',
                            'get_tree','get_data','set_data',
                            'children_as_dictionary']
        def callable(word):
            Node(name=word)
        for word in RESERVED_WORDS:
            self.assertRaises(NameError, callable, word)

class TestIteration(ut.TestCase):
    def test_node_is_iterable(self):
        node = module.ContainerNode('test')
        try:
            for point in node:
                pass
        except TypeError:
            self.fail('Node is not iterable.')

    def test_iterates_over_nodes(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')

        node.add_child(a)
        node.add_child(b)

        for subnode in node:
            self.assertIsInstance(subnode,module.Node)

    def test_iteration_respects_order(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')
        c = module.LiteralNode('c')
        node.add_child(c)
        node.add_child(b)
        node.add_child(a)
        self.assertListEqual(list(node), [c, b, a])

    def test_node_returns_all_attributes(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')
        node.add_child(a)
        node.add_child(b)
        halmaz = set([])
        for point in node: 
            halmaz.add(point)
        self.assertSetEqual(set([a,b]),halmaz)

    def test_iterable_does_not_return_self(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')
        node.add_child(a)
        node.add_child(b)
        halmaz = set([])
        for point in node: 
            halmaz.add(point)
        self.assertNotIn(node,halmaz)

    def test_number_of_children(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')
        node.add_child(a)
        node.add_child(b)
        self.assertEqual(len(node),2)

    def test_object_in(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        node.add_child(a)
        self.failUnless(a in node)

    def test_name_in(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        node.add_child(a)
        self.failUnless('a' in node)

    def test_no_child_returns(self):
        node = module.LiteralNode('test')
        def callable():
            for child in node:
                self.fail('this node should not have a child')
        self.assertRaises(TypeError, callable)

    def test_children_as_dictionary(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')
        node.add_child(a)
        node.add_child(b)
        self.assertDictEqual(node.children_as_dictionary(),{'a': a, 'b': b})

    def test_json_representation(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')
        a.set_data(1)
        b.set_data(2)
        node.add_child(a)
        node.add_child(b)
        self.assertEqual(unicode(node), u'{"a": "1", "b": "2"}')

class TestLookup(ut.TestCase):
    def test_attribute(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')

        node.add_child(a)
        node.add_child(b)

        self.assertEqual(node.a, a)
        self.assertEqual(node.b, b)

    def test_mixed_case(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('aLPHa')

        node.add_child(a)

        self.assertEqual(node.AlphA, a)

    def test_dictionary(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')

        node.add_child(a)
        node.add_child(b)

        self.assertEqual(node['a'], a)
        self.assertEqual(node['b'], b)


if __name__=='__main__':
    ut.main()
