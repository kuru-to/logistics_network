"""拠点数を変化させて最適性と計算時間をcsvファイルに書き込む

書き込む内容:
    * 拠点数
    * レーン数
    * 入力の作成にかかった時間
    * 定数の設定時間
    * 決定変数の設定時間
    * 制約の設定時間
    * 求解時間
    * 最適性
"""
import os
import csv
import time

from tqdm import tqdm

from .utils.config_util import read_config
from .input_data.graph import Graph
from .optimizer.logistics_planner import LogisticsPlanner
from .input_data.input_data_maker import InputDataMaker
from .logger.logger import setup_logger


path_data = read_config().get("PATH_DATA")

# 計算結果を書き込むcsvファイル名
file_name = f"{path_data}result/calc_time.csv"

# 拠点数の入力の設定
lst_num_base = [
    10, 20, 50,
    100,
    # 200,
    # 300,
    # 500
]


def write_result_to_csv(
    num_base: int,
    time_making_input: float,
    time_setting_constants: float,
    time_setting_objective: float,
    time_setting_variables: float,
    time_setting_constraints: float,
    time_optimization: float,
    status_optimize: str
):
    """計算結果をcsvファイルに追記する"""
    with open(file_name, "a") as f:
        # レーン数の取得
        num_lane = num_base**2

        # 改行コード（\n）を指定
        writer = csv.writer(f, lineterminator='\n')
        columns = [
            num_base, num_lane,
            time_making_input, time_setting_constants,
            time_setting_variables, time_setting_objective,
            time_setting_constraints, time_optimization,
            status_optimize
        ]
        writer.writerow(columns)


def main():
    # set up
    logger = setup_logger(os.path.basename(__file__)[:-3])
    # logging の際に表示する文字列
    name_running = "Calculation of making input and optimizing time"

    # 計算開始通知
    str_start = f"{name_running} start."
    logger.info(str_start)

    # 書き込み先のcsvファイルに列を追加しておく
    with open(file_name, "w") as f:
        # 改行コード（\n）を指定
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow([
            "n", "m",
            "time_making_input", "time_setting_constants",
            "time_setting_variables", "time_setting_objective",
            "time_setting_constraints", "time_optimization",
            "result_status"
        ])

    # 各拠点数に対して入力を作成し, 最適化
    for num_base in tqdm(lst_num_base):
        logger.info(f"Num base is {num_base}:")
        # 拠点・レーンの作成
        start = time.time()
        aGraph = InputDataMaker(num_base).run(Graph())
        elapsed_making_input = round(time.time() - start, 2)
        logger.info(f"Time of making input : {elapsed_making_input}s")

        # 定数の設定
        anOptimizer = LogisticsPlanner()
        start = time.time()
        anOptimizer.set_constants(aGraph)
        elapsed_setting_constants = round(time.time() - start, 2)
        logger.info(f"Time of setting constant : {elapsed_setting_constants}s")

        # 決定変数の設定
        start = time.time()
        anOptimizer.set_decision_variables()
        elapsed_setting_variables = round(time.time() - start, 2)
        logger.info(f"Time of setting variable : {elapsed_setting_variables}s")

        # 目的変数の設定
        start = time.time()
        anOptimizer.set_objective_function()
        elapsed_setting_objective = round(time.time() - start, 2)
        logger.info(
            f"Time of setting objective : {elapsed_setting_objective}s"
        )

        # 制約の設定
        start = time.time()
        anOptimizer.set_constraints()
        elapsed_setting_constraint = round(time.time() - start, 2)
        logger.info(
            f"Time of setting constraint : {elapsed_setting_constraint}"
        )

        # 最適化
        start = time.time()
        anOptimizer.solve()
        elapsed_optimization = round(time.time() - start, 2)
        logger.info(f"Time of optimization : {elapsed_optimization}s")

        # 結果を書き込み
        write_result_to_csv(
            num_base, elapsed_making_input, elapsed_setting_constants,
            elapsed_setting_variables, elapsed_setting_variables,
            elapsed_setting_constraint, elapsed_optimization,
            anOptimizer.result_status
        )
        logger.info(f"End of calculation for num base : {num_base}")

    # 終了通知
    str_end = f"{name_running} end."
    logger.info(str_end)


if __name__ == "__main__":
    main()
