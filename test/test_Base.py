""""Base module test"""
import unittest

from src.input_data.graph import Graph


class TestBase(unittest.TestCase):
    def setUp(self):
        self._test_id = 0
        self._test_opening_cost = 1
        self._aBase = Graph.base(self._test_id, self._test_opening_cost, 2)
        self._aGraph = Graph()
        self._aGraph.add(self._aBase)

    def test_init(self):
        self.assertEqual(self._aBase.opening_cost, self._test_opening_cost)
        self.assertEqual(self._aBase.quantity_demand, 0)

    def test_add(self):
        """`add` メソッドによって `Base` クラスの集合に追加されることを確認"""
        test_base = Graph.base(1, 3, 4)
        self._aGraph.add(test_base)
        self.assertEqual(self._aGraph.bases(), {self._aBase, test_base})

    def test_search_base(self):
        """`search_base` メソッドによって `Base` インスタンスを取得できることを確認"""
        demand = 2
        test_id = self._test_id + 1
        self._aGraph.add(Graph.base(test_id, 1, 2, quantity_demand=demand))
        test_obj = self._aGraph.search_base(test_id)
        self.assertEqual(test_obj.quantity_demand, demand)

    def test_factory_method(self):
        """ファクトリメソッドによって `Base` インスタンスが出力されていることを確認"""
        test_obj = Graph.base(*self._aBase.to_tuple())
        self.assertEqual(self._aBase, test_obj)

    def test_sorted(self):
        """ソートされたリストで出力されることを確認"""
        test_base = Graph.base(self._test_id + 1, 3, 4)
        self._aGraph.add(test_base)
        test_lst = self._aGraph.sorted_bases()
        self.assertLess(test_lst[0].id_, test_lst[1].id_)


if __name__ == "__main__":
    unittest.main()
