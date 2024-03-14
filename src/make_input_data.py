"""物流ネットワーク最適化の入力となるデータを乱数により作成する
"""
import os
import sys

from .utils.config_util import read_config
from .input_data.graph import Graph
from .data_access.data_access import CsvHandler
from .input_data.input_data_maker import InputDataMaker
from .logger.logger import setup_logger


path_data = read_config().get("PATH_DATA")


def main():
    # logger set up
    logger = setup_logger(os.path.basename(__file__)[:-3])

    # 開始通知
    str_start = "Start making input data."
    logger.info(str_start)

    aCsvHandler = CsvHandler(path_data)

    # 標準入力から拠点数を取得
    num_base = int(sys.argv[1])

    # 拠点・レーンの作成
    aGraph = InputDataMaker(num_base).run(Graph())

    # 書き込み
    aCsvHandler.write_processed_data(aGraph)

    # 完了通知
    str_end = "End making input data."
    logger.info(str_end)


if __name__ == "__main__":
    main()
