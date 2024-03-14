# -*- coding: utf-8 -*-
"""物流ネットワーク最適化のモデルに関するモジュール

@author: EINOSUKEIIDA
"""
from __future__ import annotations
import dataclasses

from docplex.mp.model import Model

from ..input_data.graph import Graph


@dataclasses.dataclass
class OptimizeParameters:
    """最適化の計算に使用するパラメータをまとめた class

    Args:
        max_seconds: 最適化に使用可能な最大秒数
        logger: 最適化の進行を出力するロガー. 基本はこのスクリプトの名前を使用
    """
    max_seconds: int = 1800


class LogisticsPlanner:
    """最適化を実行する class"""
    def __init__(
        self,
        anOptimizeParameters=OptimizeParameters(),
    ):
        """初期化

        Args:
            anOptimizeParameters: 最適化に関するハイパーパラメータ群

        Attributes:
            _model: 物流ネットワーク最小化問題のオブジェクト
            _cache_sum_flow_by_lane: レーンごとの流量を計算した際に格納しておくキャッシュ
        """
        # Setup optimization model
        self._model = Model(name="LogisticsNetworkOptimization")
        self._model.set_time_limit(anOptimizeParameters.max_seconds)

        # Initializing cache dict
        self._cache_sum_flow_by_lane = {}

    # 定数 ####################################################################
    def set_constants(self, aGraph: Graph):
        self._aGraph = aGraph
        self._aGraph.add_zero_flow()

    # 決定変数 ####################################################################
    # def key_x(self, aBase: Base):
    #     """x_i の i に当たるキー"""
    #     return aBase.id_

    # def isOne_x(self, aBase: Base):
    #     """xを定数1としてセットする対象であるか

    #     Notes:
    #         * 変数の次元削減のため, 以下の状況のいずれかにあたる場合は定数 1 とする
    #             * 生産拠点である
    #             * 需要拠点である
    #     """
    #     is_production_base = aBase.production > 0
    #     is_demand_base = aBase.demand > 0
    #     return is_production_base or is_demand_base

    # def isZero_x(self, key):
    #     """xを定数0としてセットする対象であるか

    #     Notes:
    #         * 変数の次元削減のため, 以下の状況のいずれかにあたる場合は定数0とする
    #             * tmp
    #         * x を設定する際, 先に定数1かどうかから設定するため, 定数1か否かをメソッドで判断する必要はない
    #     """
    #     return False

    # def isVariable_x(self, aBase: Base):
    #     """xを変数としてセットする対象であるか"""
    #     is_not_one = not self.isOne_x(aBase)
    #     is_not_zero = not self.isZero_x(aBase)
    #     return is_not_one and is_not_zero

    # def get_x_name(self, key):
    #     """Getter of xの名前"""
    #     return "x({:})".format(key)

    def set_var_bool_open_base(self):
        """拠点を開設するか否かの変数を設定

        Notes:
            * あらかじめ x を辞書型の attribute として設定しておく
            * 変数の対象でなければ定数とする
            * 先に定数1か否かから判定する
        """
        self.var_bool_open_base = self._model.binary_var_dict(
            keys=self._aGraph.bases(), name="bool_open_base"
        )

    def set_var_quantity_base_supply(self):
        """拠点の生産量を表す変数を設定

        Note:
            * 下限は入力として与えられている生産量
            * 上限はコスト変化点の間隔量と一致
        """
        self.var_quantity_base_supply = self._model.continuous_var_dict(
            keys=self._aGraph.base_supplies(),
            lb=lambda x: x.quantity,
            ub=lambda x: x.upper,
            name="quantity_base_supply"
        )

    def set_var_bool_open_lane(self):
        """レーンを開設するか否かの変数を設定"""
        self.var_bool_open_lane = self._model.binary_var_dict(
            keys=self._aGraph.lanes(), name="bool_open_lane"
        )

    def set_var_quantity_flow_by_singular_point(self):
        """コスト変化点ごとの物量単位あたりの物量を表す変数を設定

        Note:
            * 最小値は, 入力として与えられている物量
            * 上限はコスト変化点の間隔量と一致.
                前のコスト変化点まで達していなければ増やせないので制約で反映している
            * 計算結果を見やすくするため整数変数 `integer_var_dict` にしている.
                計算時間が長すぎるようになったら `continuous_var_dict` に変更
        """
        var = self._model.continuous_var_dict(
            keys=self._aGraph.flows(),
            lb=lambda x: x.quantity,
            name="quantity_flow_by_singular_point"
        )
        self.var_quantity_flow_by_singular_point = var

    def set_var_bool_reached_singular_point(self):
        """レーンを流れる物量がコスト変化点に到達したか否かの変数を設定

        Note:
            * レーンを流れる総物量がコスト変化点より大きくなっていれば1
        """
        self.var_bool_reached_singular_point = self._model.binary_var_dict(
            keys=self._aGraph.lane_singular_points(),
            name="bool_reached_singular_point"
        )

    def set_var_template(self):
        """変数を設定する際のテンプレート

        Note:
            * 引数は取らないようにする
            * 変数を追加する際は `set_var_*` という命名規則に従う
        """
        pass

    def set_decision_variables(self):
        """変数の設定

        Note:
            * `Optimizer` class で設定された `set_var_*` というメソッドを全て実行
        """
        for func_name in dir(self):
            if func_name.startswith("set_var_"):
                eval(f"self.{func_name}()")

    def get_sum_flow_by_lane(self, lane_id: int):
        """レーンごとの総物量を取得

        頻繁に計算する上に計算時間がかかるため, 一度計算したらキャッシュから取得するように
        """
        if lane_id not in self._cache_sum_flow_by_lane.keys():
            sum_by_singular_point = self._model.sum(
                self.var_quantity_flow_by_singular_point[flow]
                for flow in self._aGraph.flows_same_lane(lane_id)
            )
            self._cache_sum_flow_by_lane[lane_id] = sum_by_singular_point
        return self._cache_sum_flow_by_lane[lane_id]

    # def get_x(self, key):
    #     return self.var_bool_open_base[self.key_x(key)]

    # def get_x_value(self, key):
    #     """x の値をとる際, 変数を用意しなかった場合にx.value() とするとエラーが発生するので,
    #     変数を設定した場合のみ x.value() を返す
    #     """
    #     if self.isVariable_x(key):
    #         return self.get_x(key).value()
    #     else:
    #         return self.get_x(key)

    # 目的関数 ####################################################################
    def objective_function_base(self):
        """拠点に関する目的関数"""
        sum_cost_open = self._model.sum(
            base.opening_cost * self.var_bool_open_base[base]
            for base in self._aGraph.bases()
        )
        sum_cost_supply = self._model.sum(
            bs.cost_by_quantity * self.var_quantity_base_supply[bs]
            for bs in self._aGraph.base_supplies()
        )
        return sum_cost_open + sum_cost_supply

    def objective_function_lane(self):
        """レーンに関する目的関数"""
        sum_open_cost = self._model.sum(
            lane.opening_cost * self.var_bool_open_lane[lane]
            for lane in self._aGraph.lanes()
        )
        sum_flow_cost_by_singular_point = self._model.sum(
            fl.cost_by_quantity * self.var_quantity_flow_by_singular_point[fl]
            for fl in self._aGraph.flows()
        )
        return sum_open_cost + sum_flow_cost_by_singular_point

    def set_objective_function(self):
        """目的関数の設定

        Note:
            * `Optimizer` class で設定された `objective_function_*` という
                メソッドを全て実行し、出力を累積
        """
        obj = 0
        for func_name in dir(self):
            if func_name.startswith("objective_function_"):
                obj += eval(f"self.{func_name}()")
        self._model.minimize(obj)

    # 制約条件 ####################################################################
    def sum_flow_in(self, base_id: int):
        """拠点に入る物量合計
        """
        sum_flow_in = self._model.sum(
            self.get_sum_flow_by_lane(lane.id_)
            for lane in self._aGraph.lanes_same_end(base_id)
        )
        return sum_flow_in

    def sum_supply_by_base(self, base_id: int):
        """拠点で生産される物量合計"""
        sum_flow_supply = self._model.sum(
            self.var_quantity_base_supply[base_supply]
            for base_supply in self._aGraph.base_supplies_same_base(base_id)
        )
        return sum_flow_supply

    def add_constraints_base_capacity(self):
        """拠点が扱うことができる物量の制約の追加

        Note:
            * 拠点が開設すれば上限まで扱えるが, 開設しない場合上限 0
            * 流量保存制約により入る量 = 出る量なので, 片方のみに絞ってよい
        """
        lst_constraint = [
            self.sum_flow_in(base.id_) + self.sum_supply_by_base(base.id_)
            <= base.quantity_upper * self.var_bool_open_base[base]
            for base in self._aGraph.bases()
        ]
        self._model.add_constraints(lst_constraint)

    def add_constraints_flow_storage(self):
        """各拠点の流量保存に関する制約

        需要拠点の需要を満たす制約もこの中に含まれる
        """
        lst_constraint = [
            self.sum_flow_in(base.id_) + self.sum_supply_by_base(base.id_)
            == self._model.sum(
                self.get_sum_flow_by_lane(lane.id_)
                for lane in self._aGraph.lanes_same_start(base.id_)
            ) + base.quantity_demand
            for base in self._aGraph.bases()
        ]
        self._model.add_constraints(lst_constraint)

    def add_constraints_lane_capacity(self):
        """レーンが流すことができる物量の制約の追加

        Note:
            * レーンが開設すれば上限まで流せるが, 開設しない場合上限 0
        """
        lst_constraint = [
            self.get_sum_flow_by_lane(lane.id_)
            <= lane.quantity_upper * self.var_bool_open_lane[lane]
            for lane in self._aGraph.lanes()
        ]
        self._model.add_constraints(lst_constraint)

    def add_constraints_lane_capacity_by_singular_point(self):
        """コスト変化点間の上限を超えないようにする制約の追加

        Note:
            * 1つ前のコスト変化点まで物量が到達していない場合, そのコスト変化点間の物量は0
        """
        lst_lsp_flow = [
            (
                lane_singular_point,
                self._aGraph.search_flow_by_start(
                    lane.id_, lane_singular_point.singular_point
                )
            )
            for lane in self._aGraph.lanes()
            for lane_singular_point
            in self._aGraph.lane_singular_points_same_lane(lane.id_)
        ]
        lst_constraint = [
            self.var_quantity_flow_by_singular_point[lsp_f[1]]
            <= self.var_bool_reached_singular_point[lsp_f[0]] * lsp_f[1].upper
            for lsp_f in lst_lsp_flow
        ]
        self._model.add_constraints(lst_constraint)

    def add_constraints_filled_singular_point(self):
        """コスト変化点まで物量を流さなければコストが変化してはいけない制約の追加

        Note:
            * コスト変化点までの物量がコスト変化点の間隔と一致すれば変化点まで満ちたと判定
        """
        lst_lsp_flow = [
            (
                lane_singular_point,
                self._aGraph.search_flow_by_end(
                    lane.id_, lane_singular_point.singular_point
                )
            )
            for lane in self._aGraph.lanes()
            for lane_singular_point
            in self._aGraph.lane_singular_points_same_lane(lane.id_)
        ]
        lst_constraint = [
            self.var_bool_reached_singular_point[lsp_f[0]]
            <= (self.var_quantity_flow_by_singular_point[lsp_f[1]]
                / lsp_f[1].upper)
            for lsp_f in lst_lsp_flow
        ]
        self._model.add_constraints(lst_constraint)

    def add_constraints_unchange_cost_unless_reach_singular_point(self):
        """1つ前の特異点まで物量が到達していなければ物量あたりコストは変化しない制約の追加

        Note:
            * レーンごとにコスト変化点が異なるため, コスト変化点が存在するレーンごとに設定
            * 変化点が2つ以上の場合のみ, 次の変化点にまでに今の変化点に到達する必要がある
        """
        dct_lane_lst_lsp = {
            lane: sorted(
                list(self._aGraph.lane_singular_points_same_lane(lane.id_)),
                key=lambda x: x.singular_point
            )
            for lane in self._aGraph.lanes()
        }
        lst_constraint = [
            self.var_bool_reached_singular_point[lsp]
            >= self.var_bool_reached_singular_point[
                dct_lane_lst_lsp[lane][idx+1]
            ]
            for lane in self._aGraph.lanes()
            for idx, lsp in enumerate(dct_lane_lst_lsp[lane][:-1])
        ]
        self._model.add_constraints(lst_constraint)

    def add_constraints_template(self):
        """制約を追加する際のテンプレート

        Note:
            * 引数は取らないようにする
            * 制約を追加する際は `add_constraints_*` という命名規則に従う
            * 制約ごとに for文で回すと遅いと思うので, `add_constraint_*` という関数で
                各変数ごとの制約を入れるようにする
        """
        pass

    def set_constraints(self):
        """制約の設定

        Note:
            * `Optimizer` class で設定された `add_constraints_*` というメソッドを全て実行
        """
        for func_name in dir(self):
            if func_name.startswith("add_constraints_"):
                eval(f"self.{func_name}()")

    # 求解 ####################################################################
    def solve(self):
        """求解してその結果を保持する

        `{実行日付}_{モデルname}.log` というファイルに CPLEX の計算結果が格納される

        Attributes:
            solution: 最適化の結果.
            result_status: 最適化問題を解いた結果、どのような結果になったかを表す変数

        todo:
            * CPLEX へのログ出力綺麗に
        """
        log_file_path = "logs/cplex.log"
        with open(log_file_path, mode="a+") as f:
            self.solution = self._model.solve(log_output=f)
        self.result_status = self._model.solve_details.status

    def is_opt_or_feasible(self):
        """出力された結果が最適解か実行可能解かを出力

        結果の出力の際, 実行不可能であれば出力しない
        """
        is_opt = "optimal" in self.result_status
        is_feasible = "feasible" in self.result_status
        return is_opt or is_feasible

    def make_result_base(self, aGraph: Graph) -> Graph:
        """拠点に関する最適化の結果を出力"""
        # 拠点ごとの生産量表示の際に必要になる辞書
        dct_var = self.var_quantity_base_supply

        # 開設された拠点と, その生産量の追加
        for base in self._aGraph.bases():
            if not self.solution.get_value(self.var_bool_open_base[base]):
                continue

            aGraph.add(base)
            lst_supply = self._aGraph.base_supplies_same_base(base.id_)
            for supply in lst_supply:
                val = self.solution.get_value(dct_var[supply])
                if val:
                    aGraph.add(Graph.base_supply(
                        base.id_, val,
                        supply.cost_by_quantity, supply.upper
                    ))
        return aGraph

    def make_result_lane(self, aGraph: Graph) -> Graph:
        """レーンに関する最適化の結果を出力"""
        # コスト変化点ごとの表示の際に必要になる辞書
        dct_var = self.var_quantity_flow_by_singular_point

        # 開設されたレーンと, コスト変化点ごとに設定された物量単位あたりコストでの物量の追加
        for lane in self._aGraph.lanes():
            if not self.solution.get_value(self.var_bool_open_lane[lane]):
                continue

            aGraph.add(lane)
            lst_flow = self._aGraph.flows_same_lane(lane.id_)
            for flow in lst_flow:
                val = self.solution.get_value(dct_var[flow])
                if val:
                    aGraph.add(Graph.flow(
                        lane.id_, flow.start_singular_point,
                        flow.end_singular_point,
                        flow.cost_by_quantity, val
                    ))
        return aGraph

    def make_result(self, aGraph: Graph) -> Graph:
        """最適化の結果を物量を表すクラスで出力

        Note:
            * 最適解でなければ入力をそのまま返す

        Returns:
            Graph: 最適解となるグラフネットワーク. 開設された拠点・レーンと,
                レーンを流れる物量が物量単位あたりコストごとに設定されている
        """
        if not self.is_opt_or_feasible():
            return aGraph

        aGraph = self.make_result_base(aGraph)
        aGraph = self.make_result_lane(aGraph)
        return aGraph

    def display_basic_information(self, logger):
        """最適解に対する基本的な情報を表示する"""
        logger.info("********")
        logger.info("計算結果 ")
        logger.info("********")
        logger.info(f"最適性 = {self.result_status}")
        if self.is_opt_or_feasible():
            sol_val = self.solution.get_objective_value()
            logger.info(f"Objective value = {sol_val}")
        logger.info("********")

    def display_result_base(self, aGraph: Graph, logger):
        """拠点の開設・生産物量結果表示

        Args:
            aGraph: 最適化により出力された部分グラフ

        Notes:
            * `var_bool_open_base` の値が0より大きければ表示
            * 見やすくするためソートした形で表示する
        """
        # 拠点ごとの生産量表示の際に必要になる辞書
        dct_var = self.var_quantity_base_supply

        def display_result_base_supply(base_id: int):
            """拠点ごとの生産量の表示

            Note:
                * 生産していない拠点の場合,　何も表示しない
            """
            set_supply = self._aGraph.base_supplies_same_base(base_id)
            for supply in sorted(set_supply, key=lambda x: x.base_id):
                if val := self.solution.get_value(dct_var[supply]):
                    logger.info(repr(supply))
                    logger.info(f"Quantity of supply: {val}")

        logger.info("Open bases: ")
        for base in aGraph.sorted_bases():
            logger.info(repr(base))
            display_result_base_supply(base.id_)
        logger.info("********")

    def display_result_lane(self, aGraph: Graph, logger):
        """レーンの開設・流量の結果表示

        Args:
            aGraph: 最適化により出力された部分グラフ

        Notes:
            * `var_bool_open_lane` が0より大きければレーンの情報について表示
            * コスト変化点以上の物量があった場合, どの変化点まで到達したか表示
            * 見やすくするためソートした形で表示する
        """
        # コスト変化点ごとの表示の際に必要になる辞書
        dct_var = self.var_quantity_flow_by_singular_point

        def display_result_lane_by_singular_point(lane_id: int):
            """コスト変化点ごとの物量の表示

            Note:
                * コスト変化点がないレーンの場合,　何も表示しない
            """
            set_flow = self._aGraph.flows_same_lane(lane_id)
            for flow in sorted(set_flow, key=lambda x: x.start_singular_point):
                if val := self.solution.get_value(dct_var[flow]):
                    logger.info(repr(flow))
                    logger.info(f"Quantity by singular point: {val}")

        logger.info("Open lanes: ")
        for lane in aGraph.sorted_lanes():
            logger.info(repr(lane))
            # コスト変化点ごとの表示
            display_result_lane_by_singular_point(lane.id_)
        logger.info("********")

    def display_result_solve(self, aGraph: Graph, logger):
        """最適化による結果を出力する

        Notes:
            * x, yの値が0より大きければ表示するため、0.5など変な値になっていないか確認可能
            * Optimal or Feasible であれば解を表示する
        """
        self.display_basic_information(logger)

        if self.is_opt_or_feasible():
            self.display_result_base(aGraph, logger)
            self.display_result_lane(aGraph, logger)

    def run(self, aGraph_input: Graph, aGraph_output: Graph, logger) -> Graph:
        """全てを実行して最適化を行う関数

        Args:
            aGraph_input: 入力となるグラフ
            aGraph_output: 出力を追加する Graph
            logger: 最適化結果を記述するロガー
        """
        # 定数、変数、目的関数、制約条件のセット
        self.set_constants(aGraph_input)
        logger.info("constants has set")
        self.set_decision_variables()
        logger.info("decision variables has set")
        self.set_objective_function()
        logger.info("objective function has set")
        self.set_constraints()
        logger.info("constraints has set")
        # 求解
        logger.info("Start solving problem.")
        self.solve()
        logger.info("End solving problem.")
        # 解の出力
        output = self.make_result(aGraph_output)
        self.display_result_solve(output, logger)
        return output
