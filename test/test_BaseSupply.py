"""flow module test"""
import unittest

from src.input_data.graph import Graph


class TestFlow(unittest.TestCase):
    def setUp(self):
        self._base_id = 0
        self._aBaseSupply = Graph.base_supply(
            self._base_id, 0, 1, 1
        )
        self._aGraph = Graph()
        self._aGraph.add(self._aBaseSupply)

    def test_add(self):
        """`GraphComponent` クラスの集合に追加されることを確認"""
        self.assertEqual(self._aGraph.base_supplies(), {self._aBaseSupply})

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
