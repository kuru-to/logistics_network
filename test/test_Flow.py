"""flow module test"""
import unittest

from src.input_data.graph import Graph


class TestFlow(unittest.TestCase):
    def setUp(self):
        self._lane_id = 0
        self._start_singular_point = 1
        self._cost = 2
        self._aFlow = Graph.flow(
            self._lane_id, self._start_singular_point, 2, self._cost
        )
        self._aGraph = Graph()
        self._aGraph.add(self._aFlow)

    def test_init(self):
        """"特に値を指定しなければ物量は0で追加されることを確認"""
        self.assertEqual(self._aFlow.quantity, 0)

    def test_add(self):
        """`Flow` クラスの集合に追加されることを確認"""
        test_flow = Graph.flow(self._lane_id, 1, 4, 3, 2)
        self._aGraph.add(test_flow)
        self.assertEqual(self._aGraph.flows(), {self._aFlow, test_flow})


if __name__ == "__main__":
    unittest.main()
