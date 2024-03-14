""""Optimizer module test"""
import os
import math

from src.utils.config_util import read_config, test_section
from src.optimizer.logistics_planner import LogisticsPlanner
from src.input_data.graph import Graph
from src.data_access.data_access import CsvHandler
from src.logger.logger import setup_logger


path_data = read_config(section=test_section).get("PATH_DATA")

logger = setup_logger(os.path.basename(__file__)[:-3])


def make_CsvHandler():
    return CsvHandler(path_data)


def make_Graph_no_singular():
    aCsvHandler = make_CsvHandler()
    aGraph = aCsvHandler.read_bases(Graph())
    aGraph = aCsvHandler.read_base_supplies(aGraph)
    aGraph = aCsvHandler.read_lanes(aGraph)
    return aGraph


def make_Optimizer():
    return LogisticsPlanner()


def str_opt():
    """最適解であることを表す文字列"""
    return "optimal"


def test_run():
    """コスト変化点が存在しない場合に最適解が出力されることを確認"""
    anOptimizer = make_Optimizer()
    _ = anOptimizer.run(make_Graph_no_singular(), Graph(), logger)
    assert str_opt() in anOptimizer.result_status


def test_run_with_sigularity():
    """コスト変化点が存在する場合に最適解が出力されることを確認

    テスト項目:
        * コスト変化点まで到達するように解が出力されていること
        * レーン0のコスト変化点までの値が上限に達していること
        * レーン0の最後のコスト変化点からレーンの上限値までの物量について, 上限に達していないこと
    """
    aGraph = make_CsvHandler().read_lane_singular_points(
        make_Graph_no_singular()
    )

    # optimize
    anOptimizer = make_Optimizer()
    _ = anOptimizer.run(aGraph, Graph(), logger)
    assert str_opt() in anOptimizer.result_status

    # 解として出力された値の確認
    test_lsp = aGraph.search_lane_singular_point(0, 1)
    test_var = anOptimizer.var_bool_reached_singular_point[test_lsp]
    assert anOptimizer.solution.get_value(test_var) == 1

    # 連続変数にすると上限に達しないことがあるので大体合っていればOK
    dct_var = anOptimizer.var_quantity_flow_by_singular_point

    test_instance = aGraph.search_flow_by_start(0, 0)
    test_sol = anOptimizer.solution.get_value(dct_var[test_instance])
    assert math.isclose(test_sol, test_instance.upper)

    test_instance = aGraph.search_flow_by_start(0, 1)
    test_sol = anOptimizer.solution.get_value(dct_var[test_instance])
    assert math.isclose(test_sol, test_instance.upper)

    test_instance = aGraph.search_flow_by_start(0, 2)
    test_sol = anOptimizer.solution.get_value(dct_var[test_instance])
    assert test_sol < test_instance.upper
