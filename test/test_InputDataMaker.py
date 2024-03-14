"""make_input_data module tests"""
import pytest

from src.input_data.graph import Graph
from src.input_data.input_data_maker import InputDataMaker


num_base = 3
anInputDataMaker = InputDataMaker(num_base)
set_id_demand = anInputDataMaker.decide_id_demand()
set_id_supply = anInputDataMaker.decide_id_supply(set_id_demand)


@pytest.fixture
def aGraph() -> Graph:
    """テストに使用する `Graph` クラスの作成"""
    aGraph = Graph()
    aGraph = anInputDataMaker.add_bases(
        aGraph, set_id_supply, set_id_demand
    )
    aGraph = anInputDataMaker.add_lanes(
        aGraph, set_id_supply, set_id_demand
    )
    aGraph = anInputDataMaker.add_lane_singular_points(aGraph)
    return aGraph


def test_add_bases(aGraph):
    """拠点が期待通りに作成されているか確認

    テスト項目:
        * 拠点は指定した数だけ出力されている
        * 生産拠点, 需要拠点はそれぞれ1つ以上, かつ被ることがない
        * 総生産量が総需要量以上
        * 需要拠点の物量上限は需要量以上(生産上限が物量上限を上回らなくても問題ない)
        * 各生産拠点で生産しなければいけない量が0より大きく（総需要量 / 需要拠点）以下になっている
    """
    assert len(aGraph.bases()) == num_base

    base_supplies = aGraph.base_supplies()
    assert len(base_supplies) == 1

    demand_bases = {
        base for base in aGraph.bases() if base.quantity_demand
    }
    assert len(demand_bases) == 1

    supply_base_ids = {bs.base_id for bs in base_supplies}
    demand_base_ids = {base.id_ for base in demand_bases}
    assert len(supply_base_ids & demand_base_ids) == 0

    sum_supply = sum(bs.upper for bs in base_supplies)
    sum_demand = sum(base.quantity_demand for base in demand_bases)
    assert sum_supply >= sum_demand

    for base in demand_bases:
        demand = base.quantity_demand
        assert base.quantity_upper >= demand

    lower_supply = int(sum_demand / len(demand_bases))
    for base_supply in base_supplies:
        assert base_supply.quantity > 0
        assert base_supply.quantity <= lower_supply


def test_add_lanes(aGraph):
    """レーンが期待通りに出力されているか

    テスト項目:
        * ネットワークは完全グラフになっている
        * 生産拠点から需要拠点までのレーンは物量あたりコスト, 開設固定費, 物量上限が最大
    """
    assert len(aGraph.lanes()) == num_base * (num_base-1)


def test_add_lane_singular_points(aGraph):
    """レーンごとのコスト変化点が期待通りに出力されているか

    テスト項目:
        * コスト変化点が少なくとも1つ作成されていること
    """
    assert len(aGraph.lane_singular_points())
