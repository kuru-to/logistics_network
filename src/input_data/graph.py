"""グラフを表すクラス群

グラフの中にもグラフがある（サブグラフ）と考えられるため, Composite パターンを使用.
Composite パターンにより, 拠点, レーン, レーンごとのコスト変化点, レーン・コスト変化点ごとの物量を
まとめたクラスを作成する
"""
from __future__ import annotations
from abc import ABCMeta, abstractmethod
import dataclasses


class GraphAddException(Exception):
    pass


class GraphComponent(metaclass=ABCMeta):
    """グラフを形成する component クラス"""
    def bases(self) -> set['Base']:
        return set()

    def sorted_bases(self) -> list['Base']:
        """出力する際はソートされているほうが見やすいためソート"""
        return sorted(self.bases(), key=lambda x: x.id_)

    def base_supplies(self) -> set['BaseSupply']:
        return set()

    def sorted_base_supplies(self) -> list['BaseSupply']:
        return sorted(self.base_supplies(), key=lambda x: x.base_id)

    def lanes(self) -> set['Lane']:
        return set()

    def sorted_lanes(self) -> list['Lane']:
        return sorted(self.lanes(), key=lambda x: x.id_)

    def lane_singular_points(self) -> set['LaneSingularPoint']:
        return set()

    def sorted_lane_singular_points(self) -> list['LaneSingularPoint']:
        set_sps = self.lane_singular_points()
        return sorted(set_sps, key=lambda x: (x.lane_id, x.singular_point))

    def flows(self) -> set['Flow']:
        return set()

    def sorted_flows(self) -> list['Flow']:
        set_f = self.flows()
        return sorted(set_f, key=lambda x: (x.lane_id, x.start_singular_point))

    def add(self, graph_component: 'GraphComponent'):
        raise GraphAddException

    def to_tuple(self):
        """子クラスが持つ, tuple型への変換
        """
        return dataclasses.astuple(self)

    @abstractmethod
    def costs(self):
        """このグラフにかかっている総コストの取得"""
        pass

    @classmethod
    def base(
        cls, id_: int, opening_cost: int, quantity_upper: int,
        quantity_demand: int = 0
    ) -> 'Base':
        """`Base` class factory method"""
        output = Base(
            id_, opening_cost, quantity_upper,
            quantity_demand
        )
        return output

    def search_base(self, base_id: int) -> 'Base':
        """入力されたIDの `Base` class instance を出力"""
        # base_id をキーにした辞書を作成
        bases_by_id = {base.id_: base for base in self.bases()}
        # base_id をもとにインスタンスを出力
        return bases_by_id[base_id]

    def bases_demand(self) -> set['Base']:
        """需要拠点集合を抽出"""
        return set(base for base in self.bases() if base.quantity_demand)

    @classmethod
    def base_supply(
        cls, base_id, quantity, cost_by_quantity, upper
    ) -> 'BaseSupply':
        return BaseSupply(base_id, quantity, cost_by_quantity, upper)

    @classmethod
    def lane(
        cls, id_: int, start_base_id: int, end_base_id: int,
        cost_by_quantity: int, opening_cost: int, quantity_upper: int
    ) -> 'Lane':
        """`Lane` class factory method"""
        output = Lane(
            id_, start_base_id, end_base_id,
            cost_by_quantity, opening_cost, quantity_upper
        )
        return output

    def search_lane(self, lane_id: int) -> 'Lane':
        """入力されたIDの `Lane` class instance を出力"""
        # lane_id をキーにした辞書を作成
        lanes_by_id = {lane.id_: lane for lane in self.lanes()}
        # lane_id をもとにインスタンスを出力
        return lanes_by_id[lane_id]

    @classmethod
    def lane_singular_point(
        cls, lane_id: int, singular_point: int, cost_by_quantity: int
    ) -> 'LaneSingularPoint':
        """`LaneSingularPoint` class factory method"""
        output = LaneSingularPoint(lane_id, singular_point, cost_by_quantity)
        return output

    def search_lane_singular_point(
        self, lane_id: int, singular_point: int
    ) -> 'LaneSingularPoint':
        """入力されたレーンID, コスト変化点をもつ `LaneSingularPoint` class instance を出力"""
        lsp_by_id_singular_point = {
            (lsp.lane_id, lsp.singular_point): lsp
            for lsp in self.lane_singular_points()
        }
        # id_ をもとにインスタンスを出力
        return lsp_by_id_singular_point[lane_id, singular_point]

    @classmethod
    def flow(
        cls, lane_id: int, start_singular_point: int,
        end_singular_point: int, cost_by_quantity: int, quantity: int = 0
    ) -> 'Flow':
        """`Flow` class factory method"""
        output = Flow(
            lane_id, start_singular_point,
            end_singular_point, cost_by_quantity, quantity
        )
        return output


@dataclasses.dataclass(frozen=True)
class Base(GraphComponent):
    """拠点を表すクラス

    Args:
        id_: `Base_*` という形の拠点を識別するための ID
        opening_cost: 開設にかかる固定費
        quantity_upper: 拠点が扱うことができる物量上限
        quantity_demand: 拠点需要量. デフォルトは 0
    """
    id_: int
    opening_cost: int
    quantity_upper: int
    quantity_demand: int

    def __eq__(self, other) -> bool:
        return self.id_ == other.id_

    def bases(self):
        return {self}

    def costs(self):
        return self.opening_cost


@dataclasses.dataclass(frozen=True)
class BaseSupply(GraphComponent):
    """各拠点で生産される量

    Args:
        base_id: 拠点ID
        quantity: 生産量. 最適化した後は生産する量を表す
        cost_by_quantity: 生産量単位あたりにかかるコスト
        upper: 生産量上限
    """
    base_id: int
    quantity: int
    cost_by_quantity: int
    upper: int

    def costs(self) -> int:
        return self.quantity * self.cost_by_quantity

    def base_supplies(self) -> set['BaseSupply']:
        return {self}


@dataclasses.dataclass(frozen=True)
class Lane(GraphComponent):
    """レーンを表すクラス

    Args:
        id_: `Lane_*` という形のレーンID
        start_base_id: 出発拠点の ID
        end_base_id: 到着拠点の ID
        cost_by_quantity: 物量単位あたりのコスト. 変動がある場合は他のクラスで制御
        opening_cost: レーンの開設にかかる固定費
        quantity_upper: レーンが扱うことができる物量上限
    """
    id_: int
    start_base_id: int
    end_base_id: int
    cost_by_quantity: int
    opening_cost: int
    quantity_upper: int

    def __eq__(self, other) -> bool:
        """同じIDならば同じレーンとする
        """
        return self.id_ == other.id_

    def lanes(self):
        return {self}

    def costs(self):
        return self.opening_cost


@dataclasses.dataclass(frozen=True)
class LaneSingularPoint(GraphComponent):
    """物量によって変化するレーンのコストを表すクラス

    Attributes:
        id_: `LaneSingularPoint_*` という形のID
        lane_id: レーンID
        singular_point: コストの傾きが変化する点
        cost_by_quantity: コスト変化点以降の物量1単位あたりのコスト
    """
    lane_id: int
    singular_point: int
    cost_by_quantity: int

    def __eq__(self, other) -> bool:
        is_same_lane = self.lane_id == other.lane_id
        is_same_singularity = self.singular_point == other.singular_point
        return is_same_lane and is_same_singularity

    def lane_singular_points(self):
        return {self}

    def costs(self):
        """コスト変化点自体にコストはかからないため 0"""
        return 0


@dataclasses.dataclass(frozen=True)
class Flow(GraphComponent):
    """レーンを流れる物量にかかるコストと, 流れている量を格納するクラス

    Attributes:
        id_: `Flow_*` という形の ID. 他のクラスと区別するために使用
        quantity: レーンを流れている物量. デフォルトは0
    """
    lane_id: int
    start_singular_point: int
    end_singular_point: int
    cost_by_quantity: int
    quantity: int

    def flows(self):
        return {self}

    def costs(self):
        return self.cost_by_quantity * self.quantity

    @property
    def upper(self):
        """コスト変化点間で物量がとれる上限値"""
        return self.end_singular_point - self.start_singular_point


@dataclasses.dataclass(frozen=True)
class GraphComponentTemplate(GraphComponent):
    """グラフに要素を追加する際のテンプレート"""
    id_: int

    def costs(self) -> int:
        return 0


class Graph(GraphComponent):
    """グラフの要素を集めて1つのグラフとしたクラス

    グラフの要素の走査に時間がかかるため, 一度走査した要素はキャッシュして属性として取得しておく

    Attributes:
        prefix_attrb_cached: キャッシュ属性につく前置詞名
    """
    prefix_attrb_cached = "_cache"

    def __init__(self):
        """初期化

        Args:
            graph_components: GraphComponent クラスのインスタンス集合.
                サブグラフの集合がグラフと考える
        """
        self.graph_components: set[GraphComponent] = set()

    def __repr__(self):
        str_components = ", ".join(repr(gp) for gp in self.graph_components)
        return f"{self.__class__.__name__}({str_components})"

    def add(self, aGraphComponent: GraphComponent):
        """グラフの構成要素の追加

        キャッシュ属性を削除してから追加
        """
        # キャッシュ属性の削除. イテレータのままfor文回すとサイズが変更されるためエラー
        lst_cached_attrb = list(
            attrb for attrb in self.__dict__.keys()
            if attrb.startswith(self.prefix_attrb_cached)
        )
        for attrb in lst_cached_attrb:
            delattr(self, attrb)
        self.graph_components.add(aGraphComponent)

    def bases(self):
        """拠点一覧を, キャッシュがあればキャッシュから, そうでなければ走査して出力"""
        attrb_name = f"{self.prefix_attrb_cached}_bases"
        if hasattr(self, attrb_name):
            return getattr(self, attrb_name)

        output = set()
        for gp in self.graph_components:
            output.update(gp.bases())
        setattr(self, attrb_name, output)
        return output

    def base_supplies(self):
        """拠点生産情報一覧を, キャッシュがあればキャッシュから, そうでなければ走査して出力"""
        attrb_name = f"{self.prefix_attrb_cached}_base_supplies"
        if hasattr(self, attrb_name):
            return getattr(self, attrb_name)

        output = set()
        for gp in self.graph_components:
            output.update(gp.base_supplies())
        setattr(self, attrb_name, output)
        return output

    def base_supplies_same_base(self, base_id: int) -> set[BaseSupply]:
        """同じ拠点IDを持つ拠点生産量集合を抽出"""
        output = set(
            base_supply for base_supply in self.base_supplies()
            if base_supply.base_id == base_id
        )
        return output

    def lanes(self):
        """レーン情報一覧を, キャッシュがあればキャッシュから, そうでなければ走査して出力"""
        attrb_name = f"{self.prefix_attrb_cached}_lanes"
        if hasattr(self, attrb_name):
            return getattr(self, attrb_name)

        output = set()
        for gp in self.graph_components:
            output.update(gp.lanes())
        setattr(self, attrb_name, output)
        return output

    def lanes_same_start(self, base_id: int) -> set[Lane]:
        """レーンの出発拠点IDが入力拠点IDと同じレーン集合を出力"""
        return set(ln for ln in self.lanes() if ln.start_base_id == base_id)

    def lanes_same_end(self, base_id: int) -> set[Lane]:
        """レーンの到着拠点IDが入力拠点IDと同じレーン集合を出力"""
        return set(ln for ln in self.lanes() if ln.end_base_id == base_id)

    def lane_singular_points(self):
        """レーンのコスト変化点情報一覧を, キャッシュがあればキャッシュから, そうでなければ走査して出力"""
        attrb_name = f"{self.prefix_attrb_cached}_lane_singular_points"
        if hasattr(self, attrb_name):
            return getattr(self, attrb_name)

        output = set()
        for gp in self.graph_components:
            output.update(gp.lane_singular_points())
        setattr(self, attrb_name, output)
        return output

    def lane_singular_points_same_lane(
        self, lane_id: int
    ) -> set[LaneSingularPoint]:
        """同じレーンIDを持つコスト変化点集合を抽出"""
        output = set(
            lsp for lsp in self.lane_singular_points()
            if lsp.lane_id == lane_id
        )
        return output

    def flows(self):
        """輸送量情報一覧を, キャッシュがあればキャッシュから, そうでなければ走査して出力"""
        attrb_name = f"{self.prefix_attrb_cached}_flows"
        if hasattr(self, attrb_name):
            return getattr(self, attrb_name)

        output = set()
        for gp in self.graph_components:
            output.update(gp.flows())
        setattr(self, attrb_name, output)
        return output

    def flows_same_lane(self, lane_id: int) -> set[Flow]:
        """同じレーンIDを持つコスト変化点ごとの物量の一覧を抽出"""
        output = set(flow for flow in self.flows() if flow.lane_id == lane_id)
        return output

    def search_flow_by_start(
        self, lane_id: int, start_singular_point: int
    ) -> GraphComponent:
        """入力されたレーンID, コスト変化開始点をもつ class instance を出力"""
        flow_by_id_singular_point = {
            (flow.lane_id, flow.start_singular_point): flow
            for flow in self.flows()
        }
        return flow_by_id_singular_point[lane_id, start_singular_point]

    def search_flow_by_end(
        self, lane_id: int, end_singular_point: int
    ) -> GraphComponent:
        """入力されたレーンID, コスト変化終了点をもつ class instance を出力"""
        flow_by_id_singular_point = {
            (flow.lane_id, flow.end_singular_point): flow
            for flow in self.flows()
        }
        return flow_by_id_singular_point[lane_id, end_singular_point]

    def costs(self):
        return sum(gc.costs() for gc in self.graph_components)

    def add_zero_flow_by_lane(
        self, aLane: Lane, lst_lsp: list[LaneSingularPoint]
    ):
        """入力されたレーンについて, コスト変化点区間の輸送量を0としてグラフに追加

        Attributes:
            aLane: 0の輸送量を設定するレーン
            lst_lsp: レーンのコスト変化点のリスト. コスト変化点の昇順に並べられている
        """
        # 対象のレーン情報は頻繁に使用するため, 取っておく
        id_ = aLane.id_
        base_cost = aLane.cost_by_quantity
        upper = aLane.quantity_upper

        # もしコスト変化点がなければ, 0からレーンの上限値までをレーンのコストに紐づけて出力
        if not lst_lsp:
            self.add(GraphComponent.flow(id_, 0, upper, base_cost))
            return

        # コスト変化点が存在するならば, コスト変化区間を積み上げ
        last_singular = 0
        last_cost_by_quantity = base_cost
        for lsp in lst_lsp:
            # 1つ前の変化点から現在の変化点は1つ前の物量あたりコストと設定
            self.add(GraphComponent.flow(
                id_, last_singular, lsp.singular_point, last_cost_by_quantity
            ))
            # 1つ前の変化点の情報を更新
            last_singular = lsp.singular_point
            last_cost_by_quantity = lsp.cost_by_quantity
        else:
            # 全ての変化点まで走査したら最後に, 最後の変化点からレーンの上限までを追加
            # もし最後の変化点が上限を超えていたらエラーを返す
            self.add(GraphComponent.flow(
                id_, last_singular, upper, last_cost_by_quantity
            ))

    def add_zero_flow(self):
        """現在のレーン,　コスト変化点情報をもとに, コスト変化点区間の物量を0としてグラフに追加

        Note:
            * `add` method が実行されるとキャッシュがリセットされるため, レーンに紐づく
                コスト変化点のリストを取得するのに時間がかかる. そのため,
                あらかじめ全てのレーンに対するコスト変化点のリストを取得しておく

        todo:
            * あらかじめ物量が与えられている時にどのように追加するか
        """
        # レーンごとの変化点集合をあらかじめ取得
        dct_lsp = {
            lane.id_: sorted(
                list(self.lane_singular_points_same_lane(lane.id_)),
                key=lambda x: x.singular_point
                )
            for lane in self.lanes()
        }
        # レーンごとに追加される
        for lane in self.lanes():
            self.add_zero_flow_by_lane(lane, dct_lsp[lane.id_])
