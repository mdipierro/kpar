#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for kpar
"""

import os
import unittest
from io import StringIO
from kpar import Obj, to_list, clone, override, naive, load


class TestKPar(unittest.TestCase):

    def test_Obj(self):
        root = Obj()
        root.a.b.c = 1
        self.assertEqual(root.a.b.c, 1)
        self.assertEqual(root.a.b['c'], 1)
        self.assertEqual(root.a['b'].c, 1)
        self.assertEqual(root['a'].b.c, 1)
        root.types.type_bool = True
        self.assertEqual(root.types.type_bool, True)
        root.types.type_int = 1
        self.assertEqual(root.types.type_int, 1)
        root.types.type_float = 1.1
        self.assertEqual(root.types.type_float, 1.1)
        root.types.type_string = "1"
        self.assertEqual(root.types.type_string, "1")
    
    def test_Obj_lists(self):
        root = Obj()
        root.a[0] = 1
        self.assertEqual(root.a[0], 1)
        root.b = [2, 3, 4]
        self.assertEqual(root.b[0], 2)
        self.assertEqual(root.b['0'], 2)
        self.assertEqual(root.b[1], 3)
        self.assertEqual(root.b['1'], 3)
        self.assertEqual(root.b[2], 4)
        self.assertEqual(root.b['2'], 4)
        
    def test_override(self):
        root = Obj()
        root.a.b.c = 1
        def func():
            root.a.b.c = 2
        self.assertRaises(ValueError, func)
        root.a.b.c = override(3)
        self.assertEqual(root.a.b.c, 3)

    def test_naive(self):
        root = Obj()
        v = {'x': 1, 'y': 2}
        root.a.b.c = v
        self.assertEqual(root.a.b.c.x, 1)
        self.assertEqual(root.a.b.c.y, 2)
        self.assertFalse(root.a.b.c is v)
        root.a.b.c = override(naive(v))
        self.assertTrue(root.a.b.c is v)
        self.assertEqual(root.a.b.c['x'], 1)
        self.assertEqual(root.a.b.c['y'], 2)
            
    def test_Load(self):
        root = Obj()
        stream = StringIO('{"x": 1, "y": 2}')
        root.a.b.c = load('.json', stream)
        self.assertEqual(root.a.b.c.x, 1)
        self.assertEqual(root.a.b.c.y, 2)

    def test_clone(self):
        root = Obj()
        root.a.b.c = 1
        z = clone(root.a)
        self.assertEqual(root.a, z)
        self.assertFalse(root.a is z)
        z.b.c = override(2)
        self.assertEqual(root.a.b.c, 1)
        self.assertEqual(z.b.c, 2)
        
    def test_to_list(self):
        root = Obj()
        root.a.b = True
        root.a.s = 123
        root.a.s = override("123")
        root.a.v = [4, 5, 6]
        items = to_list(root)
        filename = os.path.basename(__file__)
        self.assertEqual(items[0][0], 'a.b')
        self.assertEqual(items[0][1], True)
        self.assertEqual(items[0][2], bool)
        self.assertEqual(len(items[0][3]), 1)
        self.assertEqual(items[0][3][0][0], filename)
        self.assertEqual(items[1][0], 'a.s')
        self.assertEqual(items[1][1], '123')
        self.assertEqual(items[1][2], str)
        self.assertEqual(len(items[1][3]), 2)
        self.assertEqual(items[1][3][0][0], filename)
        self.assertEqual(items[1][3][1][0], filename)
        self.assertEqual(items[2][0], 'a.v.0')
        self.assertEqual(items[2][1], 4)
        self.assertEqual(items[2][2], int)
        self.assertEqual(len(items[2][3]), 1)
        self.assertEqual(items[2][3][0][0], filename)
        self.assertEqual(items[3][0], 'a.v.1')
        self.assertEqual(items[3][1], 5)
        self.assertEqual(items[3][2], int)
        self.assertEqual(len(items[3][3]), 1)
        self.assertEqual(items[3][3][0][0], filename)
        self.assertEqual(items[4][0], 'a.v.2')
        self.assertEqual(items[4][1], 6)
        self.assertEqual(items[4][2], int)
        self.assertEqual(len(items[4][3]), 1)
        self.assertEqual(items[4][3][0][0], filename)
        
