""""LaneSingularPoint module test"""
import unittest

from src.input_data.graph import Graph


class TestLaneSingularPoint(unittest.TestCase):
    def setUp(self):
        self._lane_id = 0
        self._singular_point = 5
        self._cost = 1
        self._aLaneSingularPoint = Graph.lane_singular_point(
            self._lane_id, self._singular_point, self._cost
        )
        self._aGraph = Graph()
        self._aGraph.add(self._aLaneSingularPoint)

    def test_init(self):
        self.assertEqual(self._aLaneSingularPoint.lane_id, 0)
        self.assertEqual(self._aLaneSingularPoint.cost_by_quantity, 1)

    def test_add_same_id(self):
        """同じレーンIDでもコスト変化点が異なれば追加可能なことを確認"""
        test_aLaneSingularPoint = Graph.lane_singular_point(
            self._lane_id, self._singular_point-1, 3
        )
        self._aGraph.add(test_aLaneSingularPoint)

    def test_lane_singular_points_same_lane(self):
        """同じレーンIDを持つコスト変化点集合が抽出されることを確認"""
        self._aGraph.add(Graph.lane_singular_point(self._lane_id + 1, 1, 1))

        test_set = self._aGraph.lane_singular_points_same_lane(self._lane_id)
        self.assertEqual(test_set, {self._aLaneSingularPoint})


if __name__ == "__main__":
    unittest.main()
