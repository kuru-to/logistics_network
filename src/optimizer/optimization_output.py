from abc import ABCMeta, abstractmethod

from ..logger.logger import get_main_logger
from .optimization_input import OptimizationInput

logger = get_main_logger()


class OptimizedOutput(metaclass=ABCMeta):
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
    constants: OptimizationInput
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

    @abstractmethod
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
