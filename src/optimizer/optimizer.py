# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 10:15:02 2020

最適化問題を設定する際のインターフェース
パッケージどれ使うかの詳細には触れず, どういった形式で実装すべきかを設定
"""
from __future__ import annotations
import dataclasses
from abc import ABCMeta, abstractmethod
import time

from ..utils.config_util import read_config, default_section
from ..logger.logger import get_main_logger


# logger の設定
logger = get_main_logger()

# 表示を見やすくするためのインデント
indent = "    "


@dataclasses.dataclass
class OptimizationParameters:
    """最適化の計算に使用するパラメータをまとめた class

    Args:
        NUM_THREADS: 最適化実行時のスレッド数
        MAX_SECONDS: 最適化に使用可能な最大秒数
    """
    NUM_THREADS: int = 4
    MAX_SECONDS: int = 1800

    @classmethod
    def read_from_config(
        cls,
        file_name: str = "config_optimizer.ini",
        section: str = default_section
    ) -> 'OptimizationParameters':
        """config_optimizer ファイルから設定を読み込む

        Returns:
            OptimizationParameters: config をもとにしたクラス
        """
        config = read_config(file_name, section)

        # cls.__annotations__ から各型を取り出し, 変換を行う
        for arg_name, arg_expected_type in cls.__annotations__.items():
            config[arg_name] = arg_expected_type(config[arg_name])
        return cls(**config)


@dataclasses.dataclass
class OptimizationConstants:
    """最適化に導入する定数についてまとめたクラス

    作成する問題によって内容が異なるので, 都度作成すること
    """
    pass


@dataclasses.dataclass
class OptimizedResult:
    """最適化によって出力される結果についてまとめたクラス

    作成する問題によって解となるクラスインスタンスが異なるので, 都度作成すること
    最適化の結果がおかしなことになっていないか確認する責務も持つ

    Attributes:
        result_status: 最適化の結果を表す文字列
        is_opt: 最適解であるか否か
        elapsed_time: 最適化にかかった時間
        constants: 最適化の際に使用した定数群
        sol_objective: 解いた結果の目的関数値
        result_objects: 書き込みを行うなどする際に使用するクラスのリスト
    """
    result_status: str
    is_opt: bool
    elapsed_time: float
    constants: OptimizationConstants
    sol_objective: float
    result_objects: list

    def display_basic_information(self):
        """最適解に対する基本的な情報を表示する"""
        logger.info("********")
        logger.info("計算結果 ")
        logger.info("********")
        logger.info(f"最適性 = {self.result_status}")
        logger.info(f"Objective value = {self.sol_objective}")
        logger.info("********")

    def display_result_detail(self):
        """最適解に関する詳細について情報を表示する"""
        pass

    def display_result_solve(self):
        """最適化による結果を出力する

        Args:
            result: 最適解に関する情報. 既に出力されていると考えてよい
        """
        self.display_basic_information()

        if self.is_opt:
            self.display_result_detail()


class OptimizerInterface(metaclass=ABCMeta):
    """最適化を実行するインターフェース

    実装する際は使用パッケージ, 定式化によってやることが異なるが, 大枠で見れば同じ挙動をする

    Example:
        >>> Optimizer(anOptimizationParameters).run(OptimizationConstants)
            与えられたパラメータと定数により最適化が実行される
    """
    def __init__(
        self,
        parameters: OptimizationParameters = OptimizationParameters()
    ):
        """初期化

        Args:
            _model: 最適化のモデル
            _parameters: パラメータ
        """
        self._parameters = parameters

    # 定数 ####################################################################
    def set_constants(self, constants: OptimizationConstants):
        """定数の設定"""
        self._constants = constants

    # 決定変数 ####################################################################
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

    # 目的関数 ####################################################################
    def objective_function_template(self):
        """目的関数を出力する際のテンプレート

        Note:
            * 引数は取らないようにする
            * 目的関数を追加する際は `objective_function_*` という命名規則に従う

        Returns:
            係数まで含めた計算式. パッケージによって型が異なるので指定はしない
        """
        return 0

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
        # モデルに目的関数を追加
        self._model.minimize(obj)

    # 制約条件 ####################################################################
    def add_constraints_template(self):
        """制約を追加する際のテンプレート

        Note:
            * 引数は取らないようにする
            * 制約を追加する際は `add_constraints_*` という命名規則に従う
            * 制約ごとに for文で回すと遅いと思うので, `add_constraint_*` という関数で
                各変数ごとの制約を入れるようにする
            * `constraints` はイテレータで実装したほうが早い
        """
        constraints = ()
        self._model.add_constraints(constraints)

    def set_constraints(self):
        """制約の設定

        Note:
            * `Optimizer` class で設定された `add_constraints_*` というメソッドを全て実行
        """
        for func_name in dir(self):
            if func_name.startswith("add_constraints_"):
                eval(f"self.{func_name}()")

    # 求解 ####################################################################
    @abstractmethod
    def result_status(self) -> str:
        """最適化の結果出力された状態

        使用するパッケージによって異なるため, 都度実装する
        """
        pass

    @abstractmethod
    def is_opt(self) -> bool:
        """出力された結果が最適解かを出力"""
        pass

    @abstractmethod
    def sol_objective(self) -> float:
        """最適化の結果の目的関数値"""
        pass

    @abstractmethod
    def make_result_objects(self) -> list:
        """最適化の結果からクラスインスタンスのリストを作成し, 解とする"""
        pass

    def make_result(self, elapsed_time: float) -> OptimizedResult:
        """最適化の結果を出力

        最適解でなければ出力しない. 実行可能解でも出力したい場合は変更する

        Args:
            elapsed_time: 計算にかかった時間
        """
        if is_opt := self.is_opt():
            result_objects = self.make_result_objects()
        else:
            result_objects = []

        output = OptimizedResult(
            self.result_status(),
            is_opt,
            elapsed_time,
            self._constants,
            self.sol_objective(),
            result_objects
        )
        return output

    @abstractmethod
    def solve(self):
        """求解してその結果を保持する

        モデルによって行うことがことなるので `abstractmethod`. 必ず実装する
        """
        pass

    def run(self, constants: OptimizationConstants) -> OptimizedResult:
        """全てを実行して最適化を行う関数

        あらかじめインスタンスの初期化を行い, パラメータを設定しておく必要がある
        測定する計算時間は, 定数の設定開始~求解完了まで
        """
        start_time = time.time()
        # 定数, 変数, 目的関数, 制約条件のセット
        self.set_constants(constants)
        logger.info("Constants are set")
        self.set_decision_variables()
        logger.info("Decision variables are set")
        self.set_objective_function()
        logger.info("Objective function is set")
        self.set_constraints()
        logger.info("Constraints are set")
        # 求解
        logger.info("Start solving problem.")
        self.solve()
        logger.info("End solving problem.")
        # 解の出力
        output = self.make_result(time.time() - start_time)
        output.display_result_solve()
        return output
