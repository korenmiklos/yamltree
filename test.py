# -*- coding: utf-8 -*-
import unittest as ut 
import yamltree as module

class TestURL(ut.TestCase):
    pass

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
        def callable():
            node = module.LiteralNode('1')
        self.assertRaises(NameError, callable)

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

    def test_node_returns_string(self):
        node = module.LiteralNode('test')
        node.set_data(5)
        self.assertEqual(node.get_data(),str(5))

    def test_get_data_and_string(self):
        node = module.LiteralNode('test')
        node.set_data(5)
        self.assertEqual(node.get_data(),unicode(node))

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
        pass

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

class TestLookup(ut.TestCase):
    def test_attribute(self):
        node = module.ContainerNode('test')
        a = module.LiteralNode('a')
        b = module.LiteralNode('b')

        node.add_child(a)
        node.add_child(b)

        self.assertEqual(node.a, a)
        self.assertEqual(node.b, b)

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
