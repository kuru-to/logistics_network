""""Lane module test"""
from src.input_data.graph import Graph


def test_init():
    id_ = 0
    start_base_id = 1
    end_base_id = 2
    quantity = 1
    aLane = Graph.lane(
        id_, start_base_id, end_base_id, quantity, 2, 3
    )
    aGraph = Graph()
    aGraph.add(aLane)
    assert aLane.start_base_id == start_base_id
    assert aLane.cost_by_quantity == 1


def test_lanes_same_start():
    """レーンの出発拠点IDが入力拠点IDと同じレーンの集合が出力されることを確認"""
    start_base_id = 1
    aLane_1 = Graph.lane(
        0, start_base_id, 2, 1, 2, 3
    )
    aLane_2 = Graph.lane(
        0, start_base_id, 3, 1, 2, 3
    )
    aGraph = Graph()
    aGraph.add(aLane_1)
    aGraph.add(aLane_2)
    test_set = aGraph.lanes_same_start(start_base_id)
    assert len(test_set) == 2
