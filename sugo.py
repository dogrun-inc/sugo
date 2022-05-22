import csv
import argparse
from dataclasses import dataclass
import glob
import sqlite3
import re

parser = argparse.ArgumentParser(description='add filter')
parser.add_argument('-s')
parser.add_argument('-g', help='keyword to retrieve')
parser.add_argument('-i', help='directory name of tsv files')

args = parser.parse_args()

"""
- go-basicからgo id listを生成する
- 引数を取得し、データを出力する範囲を設定する
- またオプションとして書き出し形式も設定する
- TSVファイルを読み込み必要な部分を整形する。TSVを設置するディレクトリはオプションで設定する。
- データの正規化：取得したGO-basicに合わせてTSVの足りないデータを0で埋める
- ファイルを書き出す 
"""

go_obo = './go-basic.txt'
go_full_list = []
go_filtered_list = []


def main():
    create_go_list()
    # 0埋めしたスパースなデータセットをsqliteに保存
    # Todo: コマンドを叩く度に読み込むなら, 全長のsqlite storeする必要無いのでは？？
    cut_tsv(go_full_list, read_tsv_list(args.i))


    # filterしたgoについてデータセットをCSVで返す


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
        for l in lines:
            if l.startswith("id"):
                go_full_list.append(l[4:])
            if term in l:
                go_filtered_list.append(l[4:])

    go_filtered_list = list(set(go_filtered_list))


# リストを作成してSQLiteへ格納する。
def cut_tsv(go: list, l:list)-> list:
    # サンプルファイルごとにsqliteへの書き込みと
    # tsvファイルへのフィルターしたデータの出力を行う
    for tsv_filename in l:
        tsv_output = []
        with open('./{}'.format(tsv_filename), encoding='utf-8', newline='') as f:
            sample_name = tsv_filename.split(".")[0]
            # 1レコード（GO: TPM）ごとの処理
            for cols in csv.reader(f):
                for x in cols:
                    go = x[0]
                    tpm = x[1]
                    for go_term in go:
                        if go_term == go:
                            tsv_output.append({go_term:tpm})
                        else:
                            tsv_output.append({go_term:0})


if __name__ == "__main__":
    main()
