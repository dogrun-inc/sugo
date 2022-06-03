import csv
import argparse
from dataclasses import dataclass
import glob
import sqlite3
import re

parser = argparse.ArgumentParser(description='add filter')
parser.add_argument('-d', help='specify the directory where go.obo is located ')
parser.add_argument('-g', help='keyword to grep')
parser.add_argument('-i', help='specify the directory where source tsv file located')

args = parser.parse_args()

"""
- go-basicからgo id listを生成
- 引数を取得し、データを出力する範囲を設定する
- データの正規化：取得したGO-basicに合わせてTSVの足りないデータを0で埋める
- ファイルを書き出す 
"""

go_obo = './data/go-basic.obo'
go_full_list = []
go_filtered_list = []


def main():
    # Todo: go-basic.oboをwgetするコマンドが必要（githubだと完全長は共有できないかも？）
    create_go_list()
    # 0埋めしたスパースなデータセットをsqliteに保存
    # Todo: コマンドを叩く度に読み込むなら, 全長のsqlite storeする必要無いのでは？？
    cut_tsv(read_tsv_list(args.i))


def read_tsv_list(dir_path:str) -> list:
    """
    オプションとして設定したディレクトリから".tsv"ファイルのリストを取得し返す
    Todo: .tsvだけで無く、tab,txtなども考慮する必要がある
    """
    l = glob.glob('{}/*.tsv'.format(dir_path))
    return l


# 行の先頭がidのものだけ抽出することで、GO_termのみのリストを作成する。
def extract_unique_ids() -> list:
    go_list = []
    with open(go_obo, "r") as f:
        for line in f:
            if line.startswith('id'):
                go_list.append(line.split(' ')[1].strip())
    
    return go_list


def split_on_empty_lines() -> list:
    # oboファイルをオントロジーのブロックごと返すgenerator
    # 呼び出し側でfor ブロックで利用する
    blank_line_regex = r"(?:\r?\n){2,}"
    f = open(go_obo, "r")
    str_f = f.read()
    iter_matches = re.split(blank_line_regex, str_f.strip())
    for match in iter_matches:
        yield match


def create_go_list():
    """
    全長およびオプション条件でfilterしたGO IDのリストを生成する
    リストはグローバル
    :return:
    """
    global go_full_list
    global go_filtered_list

    term = args.g

    for t in split_on_empty_lines():
        lines = t.split("\n")
        go_id = ""
        for l in lines:
            # id行があった場合go idリストに追加
            if l.startswith("id"):
                go_id = l[4:]
                go_full_list.append(go_id.lower())
            # 一致するキーワードが見つかった場合filtered_listに追加
            if term in l:
                go_filtered_list.append(go_id.lower())
    go_filtered_list = list(set(go_filtered_list))


# リストを作成してSQLiteへ格納する。
def cut_tsv(l: list):
    # 以下ブロックでサンプルファイルごとにsqliteへの書き込みと
    # tsvファイルへのフィルターしたデータの出力を行う
    for filename in l:
        # 全GOを含むデータセット
        feature_dataset = {}
        sample_name = re.split('\.|/', filename)[1]
        with open('./{}'.format(filename), encoding='utf-8', newline='') as f:
            # 1レコードGO: TPMを辞書に追加追加
            for row in csv.reader(f, delimiter='\t'):
                feature_dataset[row[0]] = row[1]

        """        
        dataset_lst = []
        for go in go_full_list:
            # goがfeature_datasetに含まれる場合そのTPM値を渡してリスト（list of tuple）を生成する
            if go in feature_dataset:
                dataset_lst.append(go, feature_dataset[go])
            # goがfeature_datasetに含まれない場合TPMカラムを0で埋める
            else:
                dataset_lst.append((go, 0))

        create_table(sample_name)
        store_data()
        """

        # filtered_listのみの(GO, TPM) listを生成する
        filtered_list = []
        # フィルターされたGOリストでサンプルごとのTPMデータセットを舐め、値の入力もしくは０埋めする
        for go in go_filtered_list:

            if go in feature_dataset:
                filtered_list.append([go, feature_dataset[go]])
            else:
                filtered_list.append([go, 0])

        write_tsv(sample_name, filtered_list)


def create_table(sample_name):
    pass


def store_data(sample_name, dataset_lst):
    pass


def write_tsv(sample_name, lst):
    with open("./data/{}.tsv".format(sample_name), "w") as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(lst)


if __name__ == "__main__":
    main()
