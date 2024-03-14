"""CsvHandler package tests"""
import unittest
import os

from src.utils.config_util import read_config, test_section
from src.input_data.graph import Graph
from src.data_access.data_access import CsvHandler


class TestCsvHandler(unittest.TestCase):
    def setUp(self):
        self._path_data = read_config(section=test_section).get("PATH_DATA")
        self._aCsvHandler = CsvHandler(self._path_data)
        self._aGraph = Graph()

    def test_read_bases(self):
        test_obj = self._aCsvHandler.read_bases(self._aGraph)
        self.assertEqual(test_obj.search_base(0).id_, 0)

    def test_read_lanes(self):
        test_obj = self._aCsvHandler.read_lanes(self._aGraph)
        self.assertEqual(test_obj.search_lane(2).id_, 2)

    def test_read_lane_singular_points(self):
        test_obj = self._aCsvHandler.read_lane_singular_points(self._aGraph)
        self.assertEqual(
            test_obj.search_lane_singular_point(0, 1).cost_by_quantity, 2
        )

    def test_write(self):
        """書き込みのテスト"""
        self._aGraph.add(Graph.flow(0, 0, 1, 1, 1))
        self._aGraph.add(Graph.flow(1, 1, 2, 1, 1))
        file_name = "result/test.csv"
        lst_flows = list(self._aGraph.flows())
        self._aCsvHandler.write(lst_flows, file_name)
        test_obj = self._aCsvHandler.read_flows(Graph(), file_name)
        self.assertEqual(self._aGraph.flows(), test_obj.flows())

        # テストが終わったらファイルを削除しておく
        os.remove(self._path_data + file_name)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
