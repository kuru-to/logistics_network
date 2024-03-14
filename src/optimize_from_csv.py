"""csvファイルを読み込んで最適化の実行"""
import os

from .utils.config_util import read_config
from .input_data.graph import Graph
from .optimizer.logistics_planner import LogisticsPlanner
from .data_access.data_access import CsvHandler
from .logger.logger import setup_logger


path_data = read_config().get("PATH_DATA")


def main():
    # set up
    logger = setup_logger(os.path.basename(__file__)[:-3])

    # 計算開始通知
    str_start = "Network optimization start."
    logger.info(str_start)

    # csvファイルの入出力先指定
    aCsvHandler = CsvHandler(path_data)

    # データの読み込み
    aGraph = aCsvHandler.read_constants(Graph())

    # 最適化し結果を出力
    anOptimizer = LogisticsPlanner()
    sol_aGraph = anOptimizer.run(aGraph, Graph(), logger)

    # 最適であれば最適化結果の書き込み
    if anOptimizer.is_opt_or_feasible():
        aCsvHandler.write_opt_solution(sol_aGraph)

    # 終了通知
    str_end = "Network optimization end."
    logger.info(str_end)


if __name__ == "__main__":
    main()
