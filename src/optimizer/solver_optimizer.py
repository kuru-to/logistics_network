"""ソルバーを用いて最適化する際のインターフェース
"""
from abc import ABCMeta, abstractmethod
import time

from ..logger.logger import get_main_logger
from .optimizer import OptimizerInterface, OptimizationConstants, OptimizedResult

logger = get_main_logger()


class SolverOptimizer(OptimizerInterface, metaclass=ABCMeta):
    """ソルバーを用いて最適化を実行するインターフェース

    主に定式化等を扱う

    Example:
        >>> Optimizer(anOptimizationParameters).run(OptimizationConstants)
            与えられたパラメータと定数により最適化が実行される
    """
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

    @abstractmethod
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
