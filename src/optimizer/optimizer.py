# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 10:15:02 2020

最適化問題を設定する際のインターフェース
パッケージどれ使うかの詳細には触れず, どういった形式で実装すべきかを設定
"""
from abc import ABCMeta, abstractmethod

from ..logger.logger import get_main_logger
from .optimization_parameters import OptimizationParameters
from .optimization_input import OptimizationInput
from .optimization_output import OptimizedOutput

logger = get_main_logger()


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

    @abstractmethod
    def run(self, input: OptimizationInput) -> OptimizedOutput:
        """全てを実行して最適化を行う関数
        """
        pass
