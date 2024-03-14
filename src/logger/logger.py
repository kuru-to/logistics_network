"""logger module

`config/logging.conf` からロガーに関する情報を読み込む.
ファイルに出力する際は `{日付}_{指定した名前}.log` という形になるよう設定
"""
import os
from datetime import date
import logging
import logging.config
import glob

from ..utils.str_util import add_suffix_log
from ..utils.config_util import read_config

config = read_config(section="DEFAULT")
path_config = config["PATH_CONFIG"]
# disable_existing_loggers=False でないと, 他で設定したloggerを無視してしまう
logging.config.fileConfig(
    f"{config['PATH_CONFIG']}{config['CONFIG_LOGGING']}",
    disable_existing_loggers=False
)
path_log = config["PATH_LOG"]

# 表示を見やすくするためのインデント
indent = "    "


def get_main_logger():
    """`logging.conf` で設定されている MainLogger を出力

    実際に実行しないスクリプト（import されるのみ）であればこのメソッドからloggerを取得する
    ファイルに書き込む場合は `setup_logger` メソッドを使用
    """
    return logging.getLogger("MainLogger")


def setup_logger(
    name: str,
    *,
    batch_date: date = date.today(),
    path_log: str = path_log,
    name_logger: str = "MainLogger"
):
    """logger のセットアップ

    Args:
        name: 出力するlogファイルの名前
        batch_date: バッチ日. default は実行した当日
        path_log: log ファイルの出力先ディレクトリ
        name_logger: もとにする logger の名前. `logging.conf` で設定されていること

    Returns:
        logger: config の MainLogger の設定を受けついだ子ロガー
            logger.info() などでlogファイルに logging
    """
    # logger の取得
    logger = logging.getLogger(name_logger)

    # logファイルの出力名設定
    str_batch_date = batch_date.strftime("%Y%m%d")
    logfile = add_suffix_log(f"{path_log}{str_batch_date}_{name}")

    # create file handler which logs even DEBUG messages
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)
    fh_formatter = logging.Formatter(
        ' %(asctime)s : %(filename)s:%(lineno)s [%(levelname)s] %(message)s'
    )
    fh.setFormatter(fh_formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    return logger


def idx_date_start_end_from_filename(path_log: str):
    """ログファイルまでのパスも含めたファイル名から日付の部分を取り出すために,
    日付部分のインデックスを出力

    日付は `%Y%m%d` の形式のため, 8文字分
    """
    start_date_idx = len(path_log)
    end_date_idx = start_date_idx + 8
    return start_date_idx, end_date_idx


def remove_log_files(
    end_date_to_be_deleted: str,
    path_log: str = path_log
):
    """古くなったログファイルの削除

    Args:
        end_date_to_be_deleted: この日付以前のlogファイルを削除する
        path_log: 削除対象のディレクトリ
    """
    # 存在するログファイルのリスト化
    file_list = glob.glob(f"{path_log}*.log")

    for filename in file_list:
        # 日付は8桁で設定されているため, ファイル名から日付のみ抽出
        start_idx, end_idx = idx_date_start_end_from_filename(path_log)
        file_date = filename[start_idx:end_idx]

        # ファイルの日付が削除対象日以前であれば削除
        if end_date_to_be_deleted >= file_date:
            os.remove(filename)
