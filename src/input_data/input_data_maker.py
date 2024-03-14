"""物流ネットワーク最適化の入力となるデータを乱数により作成する"""
from __future__ import annotations
import dataclasses
import random
import itertools

from tqdm import tqdm
import numpy as np

from .graph import Graph


@dataclasses.dataclass
class InputDataMaker:
    """物流ネットワークグラフを乱数により作成するクラス

    Attributes:
        num_base: 作成する拠点の数. 完全グラフを作成するためレーンの数は指定しない
        num_supply_demand: 生産拠点の生産上限. 需要拠点の需要量はこの値までの乱数で取得
        max_random: 生成する際にとる乱数の最大値. 0からこの値までが各 Graph の係数となる
        random_seed: 乱数の種. 計算するたびに結果が変わるのも嫌なので種固定
        num_demand_base: 需要拠点の数. 10か, 拠点数の半分以下になるようにする
        num_supply_base: 生産拠点の数. 生産上限が一定なため, 需要拠点数以上にする
    """
    num_base: int
    num_supply_demand: int = 100
    max_random: int = 100
    random_seed: int = 71

    def __post_init__(self):
        # 需要・生産拠点の数指定
        max_supply_demand_base = min([10, int(self.num_base / 2) + 1])
        self.num_demand_base: int = random.randrange(
            1, max_supply_demand_base, self.random_seed
        )
        self.num_supply_base: int = random.randrange(
            self.num_demand_base, max_supply_demand_base, self.random_seed
        )
        # 乱数シード固定
        random.seed(self.random_seed)
        np.random.seed(seed=self.random_seed)

    def decide_id_demand(self) -> set[int]:
        """需要拠点の決定"""
        choiced_id = np.random.choice(self.num_base, self.num_demand_base)
        return set(choiced_id)

    def decide_id_supply(self, set_id_demand: set[int]) -> set[int]:
        """生産拠点の決定. 需要拠点と被らないようにする"""
        set_choice = set(range(self.num_base)) - set_id_demand
        choiced_id = np.random.choice(list(set_choice), self.num_supply_base)
        return set(choiced_id)

    def make_base(
        self, base_id: int, num_upper: int, num_demand: int
    ):
        """ベースクラスの作成"""
        # 開設固定費の設定
        # 開設費は最低でも1ないと解で開いてしまう
        opening_cost = random.randrange(1, self.max_random)

        output = Graph.base(
            base_id, opening_cost, num_upper, num_demand
        )
        return output

    def make_base_supply(
        self, base_id: int, num_supply: int, lower_supply: int
    ):
        """生産拠点の生産量の作成

        Args:
            base_id: 拠点ID
            num_supply: 供給量
            lower_supply: 最低限その拠点が供給する量
        """
        # 生産量単位当りのコスト
        cost = random.randrange(self.max_random)
        output = Graph.base_supply(
            base_id, lower_supply, cost, num_supply
        )
        return output

    def add_bases(
        self, aGraph: Graph,
        set_id_supply: set[int], set_id_demand: set[int]
    ) -> Graph:
        """拠点に関する情報を作成しグラフに追加

        Note:
            * 物量上限は, 生産・需要拠点であればその値に, そうでなければ乱数で設定
            * 開設固定費は乱数で設定
            * 需要量が供給量を超えないよう, 乱数を取った際に
            * 各生産拠点で最低限生産する量は,
                総需要から生産拠点数を割った値を上限に乱数で設定
            * 拠点が扱える物量上限は, 生産 or 需要拠点であればその生産 or 需要量以上になるように,
                そうでなければ0以上になるようにして乱数で設定
        """
        # 需要拠点
        sum_demand = 0
        for id_demand in set_id_demand:
            num_demand = random.randrange(1, self.num_supply_demand)
            sum_demand += num_demand
            aBase = self.make_base(
                id_demand, self.num_supply_demand, num_demand
            )
            aGraph.add(aBase)

        # 生産拠点が最低限生産しなければいけない量を乱数で設定
        lower_supply = int(sum_demand / len(set_id_supply))
        # 生産拠点
        for id_supply in set_id_supply:
            lower_supply_by_base = random.randrange(lower_supply)
            aBase = self.make_base(id_supply, self.num_supply_demand, 0)
            aGraph.add(aBase)
            aBaseSupply = self.make_base_supply(
                id_supply, self.num_supply_demand, lower_supply_by_base
            )
            aGraph.add(aBaseSupply)

        # 上記以外の拠点
        bases = set(range(self.num_base)) - set_id_supply - set_id_demand
        for base_id in tqdm(bases):
            upper = random.randrange(self.max_random)
            aBase = self.make_base(base_id, upper, 0)
            aGraph.add(aBase)
        return aGraph

    def make_lane(
        self, lane_id: int, start_base_id: int, end_base_id: int,
        is_lane_supply_demand: bool
    ):
        """レーンの作成

        Args:
            is_lane_supply_demand: レーンが生産・需要拠点をつなぐレーンかどうか
        """
        # 生産-需要拠点間のレーンは全て最大値を設定
        if is_lane_supply_demand:
            cost_by_quantity = self.max_random
            opening_cost = self.max_random
            quantity_upper = self.max_random
        else:
            cost_by_quantity = random.randrange(self.max_random)
            # 開設費は最低でも1ないと解で開いてしまう
            opening_cost = random.randrange(1, self.max_random)
            quantity_upper = random.randrange(self.max_random)

        aLane = Graph.lane(
            lane_id, start_base_id, end_base_id,
            cost_by_quantity, opening_cost, quantity_upper
        )
        return aLane

    def add_lanes(
        self, aGraph: Graph,
        set_id_supply: set[int], set_id_demand: set[int]
    ) -> Graph:
        """レーンを作成しグラフに追加. 完全グラフになるように作成する

        Note:
            * 物量あたりコスト, 開設固定費, 物量上限は生産-需要拠点を結ぶレーンであれば,
                できるだけ直送レーンを使いたくないが最悪送ることはできる, という設定にするため最大値
                そうでなければ乱数で設定
        """
        lane_id_count = 0

        # 全拠点の集合の直積をとり, 1つの for loop ですます
        iter_base_ids = range(self.num_base)
        iter_comb = itertools.product(iter_base_ids, iter_base_ids)

        for i, (start_base_id, end_base_id) in enumerate(tqdm(iter_comb)):
            # 到着地が出発地と同じであればレーンは作らない
            if start_base_id == end_base_id:
                continue

            aLane = self.make_lane(
                lane_id_count, start_base_id, end_base_id,
                start_base_id in set_id_supply and end_base_id in set_id_demand
            )
            aGraph.add(aLane)
            lane_id_count += 1
        return aGraph

    def add_lane_singular_points(
        self, aGraph: Graph
    ) -> Graph:
        """コスト変化点の追加

        Note:
            * コスト変化点は1レーンにつき0~3個. 個数は乱数で設定
            * レーンのコストがコスト変化点数より小さいと乱数が取得できずエラーを起こすため,
                レーンのコストより小さい範囲でコスト変化点数の乱数を取る
            * レーンの物量上限がコスト変化点数より小さい場合も同様
            * コスト変化点より大きい流量のコストはそれ以前のコストより小さくなるよう乱数で設定
        """
        lanes = aGraph.lanes()
        for aLane in lanes:
            max_num_singular_points = min(
                3, aLane.quantity_upper-1, aLane.cost_by_quantity-1
            )
            # コスト変化点がとれない場合は次のレーンへ
            # 物量上限, コストが0の場合-1になりかねないため, 0以下で判定
            if max_num_singular_points <= 0:
                continue
            num_singular_points = random.randint(0, max_num_singular_points)
            upper_cost = aLane.cost_by_quantity
            lower_singular_point = 1
            # コスト変化点は前の変化点と同じになってはいけない,
            # コストはコスト変化点が残っている時に1になってはいけないため,
            # 後ろから range をかけることで前と同じにならないようにする
            for i in range(num_singular_points, 0, -1):
                cost = random.randint(i, upper_cost)
                singular_point = random.randint(
                    lower_singular_point, aLane.quantity_upper - i
                )
                obj = Graph.lane_singular_point(
                    aLane.id_, singular_point, cost
                )
                aGraph.add(obj)
                # コストの上限値, コスト変化点の下限値の更新
                upper_cost = cost
                lower_singular_point = singular_point + 1
        return aGraph

    def run(self, aGraph: Graph) -> Graph:
        """グラフネットワークを作成して出力"""
        set_id_demand = self.decide_id_demand()
        set_id_supply = self.decide_id_supply(set_id_demand)

        aGraph = self.add_bases(aGraph, set_id_supply, set_id_demand)
        aGraph = self.add_lanes(aGraph, set_id_supply, set_id_demand)
        aGraph = self.add_lane_singular_points(aGraph)
        return aGraph
