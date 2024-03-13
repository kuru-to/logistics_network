"""zipping に関する便利なツールをまとめたスクリプト"""
from __future__ import annotations
import os
import zipfile

from .file_util import create_dir_if_not_exists
from .str_util import add_suffix_zip


def write_zip(lst_file_or_dir: list[str], zipped_file_name: str, path: str, keep_directory: bool = True):
    """ファイルをzip化して書き出し. ディレクトリ構造は入力にて対応

    Args:
        lst_file_or_dir (list[str]): 書き出し対象のファイル, もしくはディレクトリのリスト
        zipped_file_name (str): 書き出した後のzipファイル名. パス含まない
        path (str): zipファイルを置くディレクトリ
        keep_directory (bool): ディレクトリ構造を保つか否か
    """
    # ディレクトリがないとエラーになるので作る
    create_dir_if_not_exists(path)

    fullfile_name = f"{path}{zipped_file_name}"
    with zipfile.ZipFile(add_suffix_zip(fullfile_name), 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in lst_file_or_dir:
            # もしファイルであればそのまま書き込み
            if os.path.isfile(path):
                if keep_directory:
                    zf.write(path)
                else:
                    zf.write(path, os.path.basename(path))
            # もしディレクトリであれば配下のディレクトリ内のファイルもすべてzippingするようにする
            if os.path.isdir(path):
                for dirname, _, filenames in os.walk(path):
                    for fn in filenames:
                        # ディレクトリ構造を保つのであればそのままzipに書き込む
                        if keep_directory:
                            zf.write(os.path.join(dirname, fn))
                        else:
                            zf.write(os.path.join(dirname, fn), fn)


def extract_zip(zip_file_name: str, extract_path: str) -> list[str]:
    """zip ファイルの展開

    Args:
        zip_file_name (str): zipファイル名. `.zip` で終わらなくても問題ない. パス含む
        extract_path (str): zipファイルを展開する先のフォルダ名

    Returns:
        list[str]: zipファイルに存在したファイルの名前リスト
    """
    with zipfile.ZipFile(add_suffix_zip(zip_file_name), "r") as zf:
        output = zf.namelist()
        zf.extractall(path=extract_path)
    return output


def is_exist_in_zip(target_file: str, zip_file_name: str) -> bool:
    """zipファイルの中に対象のファイル名が存在するか確認

    Args:
        target_file (str): 対象ファイルの名前, パス含む
        zip_file_name (str): 検索対象のzipファイル名, パス含む

    Returns:
        bool: 存在すれば True, しなければ False
    """
    with zipfile.ZipFile(zip_file_name, "r") as zf:
        file_list = zf.namelist()
    return target_file in file_list
