"""データの読み込み・書き込みに関するモジュール"""
from __future__ import annotations
import csv

import pandas as pd
from tqdm import tqdm

from src.input_data.graph import GraphComponent


def add_csv_postfix(filename: str):
    """filename に `.csv` と入っていなければ追加"""
    if not filename.endswith(".csv"):
        filename += ".csv"
    return filename


class CsvHandler:
    """csv ファイルの読み込み・書き込みをつかさどるクラス"""
    def __init__(self, path_data: str):
        """初期化

        Attributes:
            path_data: csvファイルを読み込む際のパス
        """
        self.path_data = path_data

    def read(
        self, aGraph: GraphComponent, name: str, factory_method
    ) -> GraphComponent:
        """csvファイルの読み込み

        Args:
            aGraph: グラフ情報が格納されたインスタンス.
                このインスタンスに読み込んだデータを追加
            name: パスまで含めた読み込み先ファイル名
            factory_method: 対象のグラフ要素を作成するファクトリメソッド

        Returns:
            GraphComponent: グラフの要素となるクラスインスタンス.
                出力が想定されるのは, `Graph` class 以外のサブクラス
        """
        filename = add_csv_postfix(name)
        df = pd.read_csv(f"{self.path_data}{filename}")
        # index を抜いて値を抽出
        for _, *values in tqdm(df.itertuples()):
            aGraph.add(factory_method(*values))
        return aGraph

    def read_bases(
        self, aGraph: GraphComponent,
        name: str = "processed/bases.csv",
    ) -> GraphComponent:
        """拠点に関するデータの読み込み"""
        return self.read(aGraph, name, aGraph.base)

    def read_base_supplies(
        self, aGraph: GraphComponent,
        name: str = "processed/base_supplies.csv",
    ) -> GraphComponent:
        """拠点の生産量に関するデータの読み込み"""
        return self.read(aGraph, name, aGraph.base_supply)

    def read_lanes(
        self, aGraph: GraphComponent,
        name: str = "processed/lanes.csv",
    ) -> GraphComponent:
        """レーンに関するデータの読み込み"""
        return self.read(aGraph, name, aGraph.lane)

    def read_lane_singular_points(
        self, aGraph: GraphComponent,
        name: str = "processed/lane_singular_points.csv",
    ) -> GraphComponent:
        """レーンに紐づくコスト変化点に関するデータの読み込み"""
        return self.read(aGraph, name, aGraph.lane_singular_point)

    def read_flows(
        self, aGraph: GraphComponent,
        name: str = "processed/flows.csv",
    ) -> GraphComponent:
        """物量の流れとコストに関するデータの読み込み"""
        return self.read(aGraph, name, aGraph.flow)

    def read_constants(self, aGraph: GraphComponent) -> GraphComponent:
        """読み込みが無くて実行不能になったことがあったため, 今後そうならないようまとめておく"""
        aGraph = self.read_bases(aGraph)
        aGraph = self.read_base_supplies(aGraph)
        aGraph = self.read_lanes(aGraph)
        return aGraph

    def write(
        self, lst_graph_component: list, name: str,
        is_truncate: bool = True
    ):
        """csvファイルに書き込みを行う

        Args:
            lst_graph_component: 書き込む対象となるグラフのうち, 書き込むものに絞ったインスタンスリスト
                拠点, レーン, 物量とコストで分かれる
            name: 書き込む際の名前. ディレクトリも指定する際は入れておく
            is_truncate: 書き込む際に中身を綺麗にするか否か
        """
        filename = add_csv_postfix(name)
        if is_truncate:
            mode = "w"
        else:
            mode = "a"
        with open(f"{self.path_data}{filename}", mode) as f:
            # 改行コード（\n）を指定
            writer = csv.writer(f, lineterminator='\n')
            # 最初の要素から必要な列名を取得し, 書き込み
            columns = lst_graph_component[0].__dict__.keys()
            writer.writerow(columns)
            # 残りの要素の書き込み
            for gp in tqdm(lst_graph_component):
                writer.writerow(gp.to_tuple())

    def write_processed_data(self, aGraph: GraphComponent):
        """作成された処理済みのデータを出力する

        前処理が済んだもの, および乱数により作成されたものを書き込む

        Args:
            aGraph: 最適化の結果出力されるサブグラフ.
                拠点, レーンの情報が書き出される
        """
        path_file = "processed/"
        # 拠点情報
        self.write(aGraph.sorted_bases(), f"{path_file}bases")
        # 拠点の生産情報
        self.write(aGraph.sorted_base_supplies(), f"{path_file}base_supplies")
        # レーン情報
        self.write(aGraph.sorted_lanes(), f"{path_file}lanes")
        # レーンのコスト変化点情報
        self.write(
            aGraph.sorted_lane_singular_points(),
            f"{path_file}lane_singular_points"
        )

    def write_opt_solution(self, aGraph: GraphComponent):
        """最適化の結果を出力する

        Args:
            aGraph: 最適化の結果出力されるサブグラフ.
                拠点, レーン, 物量とコストの情報が書き出される
        """
        path_file = "result/"
        # 開設した拠点
        self.write(aGraph.sorted_bases(), f"{path_file}sol_bases")
        # 生産した物量
        filename = f"{path_file}sol_base_supplies"
        self.write(aGraph.sorted_base_supplies(), filename)
        # 開設したレーン
        self.write(aGraph.sorted_lanes(), f"{path_file}sol_lanes")
        # 流れた物量
        self.write(aGraph.sorted_flows(), f"{path_file}sol_flows")
