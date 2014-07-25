__author__ = 'escherba'

import unittest
<<<<<<< HEAD
from lsh.unionfind import UnionFind
=======
from pymaptools import UnionFind
>>>>>>> 6d6e0de21b2eee7c2c34d326ff063ec4bc36ad31


class TestUnionFind(unittest.TestCase):
    def test_simple_cluster(self):
        uf = UnionFind()
        uf.union(0, 1)
        uf.union(2, 3)
        uf.union(3, 0)
        self.assertEqual(uf.sets(), [[0, 1, 2, 3]])


if __name__ == '__main__':
    unittest.main()
