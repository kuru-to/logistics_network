""""Graph module test"""
from src.utils.config_util import read_config, test_section
from src.input_data.graph import Graph
from src.data_access.data_access import CsvHandler


# config ファイルから設定
path_data = read_config(section=test_section).get("PATH_DATA")


def test_add_zero_flow():
    """レーン,　コスト変化点情報をもとに物量情報がグラフに追加されることを確認"""
    lane_id = 0
    lane_upper = 2
    base_cost = 3
    aLane = Graph.lane(lane_id, 0, 1, base_cost, 0, lane_upper)
    aGraph = CsvHandler(path_data).read_constants(Graph())
    aGraph.add(aLane)
    singular_point = 1
    changed_cost = 2
    aLaneSingularPoint = Graph.lane_singular_point(
        lane_id, singular_point, changed_cost
    )
    aGraph.add(aLaneSingularPoint)
    aGraph.add_zero_flow()

    test_aFlow = aGraph.search_flow_by_end(
        lane_id, singular_point
    )
    assert test_aFlow.cost_by_quantity == base_cost
    test_aFlow = aGraph.search_flow_by_end(
        lane_id, lane_upper
    )
    assert test_aFlow.cost_by_quantity == changed_cost
