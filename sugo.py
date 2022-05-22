import csv
import argparse
from dataclasses import dataclass
import glob
import sqlite3
import re

parser = argparse.ArgumentParser(description='add filter')
parser.add_argument('-s')
parser.add_argument('-g')
parser.add_argument('-i')

args = parser.parse_args()

"""
- go-basicからgo id listを生成する
- 引数を取得し、データを出力する範囲を設定する
- またオプションとして書き出し形式も設定する
- TSVファイルを読み込み必要な部分を整形する。TSVを設置するディレクトリはオプションで設定する。
- データの正規化：取得したGO-basicに合わせてTSVの足りないデータを0で埋める
- ファイルを書き出す 
"""

go_full_list = []
go_filtered_list = []


def main():
    print(args.i)


def read_tsv_list(n) -> list:
    """
    オプションとして設定したディレクトリから".tsv"ファイルのリストを取得し返す
    """
    l = glob.glob('{}/*.tsv'.format(n))
    return l


# 行の先頭がidのものだけ抽出することで、GO_termのみのリストを作成する。
def extract_unique_ids() -> list:
    go_list = []
    with open('./go-basic.txt', "r") as f:
        for line in f:
            if line.startswith('id'):
                go_list.append(line.split(' ')[1].strip())
    
    return go_list


# ListをSQLiteへ入れる関数作る。
# def list_into_sqlite():
#     # テーブルがなければテーブルを作る
#     CREATE_TABLE = 
#     # 行がサンプル、列がGO_Term。


# go-basic_セクション分け
# def split_on_empty_lines():
#     # greedily match 2 or more new-lines
#     blank_line_regex = r"(?:\r?\n){2,}"
#     with open('./go-basic.txt', "r") as f:
#         str_f = f.read()
#     print(re.split(blank_line_regex, str_f.strip()))

def split_on_empty_lines() -> list:
    # オントロジーファイルをブロックごと返すgenerator
    # for 処理として利用する
    # greedily match 2 or more new-lines
    blank_line_regex = r"(?:\r?\n){2,}"
    f = open("./go-basic.txt", "r")
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

# def go_basic_sections():
#     with open('./go-basic.txt', "r") as f:
#         str_f = f.read()
#         # print(str_f,type(str_f))
#         print(len(str_f))
#         # iter_matches = re.finditer("[\w|\:|\!|\n]+\n\n", str_f)
#         iter_matches = re.finditer('Term = (.+)$',str_f)
#         for match in iter_matches:
#             print(match.group())
#             break


# ユーザの求めるデータのみにFilterする関数
# def filter



# リストを作成してSQLiteへ格納する。
def cut_tsv(go: list, l:list)-> list:
    for tsv_filename in l:
        tsv_output = []
        with open('./{}'.format(tsv_filename), encoding='utf-8', newline='') as f:
            for cols in csv.reader(f):
                # print(cols)
                for x in cols:
                    go_sample = x[0]
                    tpm = x[1]
                    for go_term in go:
                        if go_term == go_sample:
                            tsv_output.append({go_term:tpm})
                        else:
                            tsv_output.append({go_term:0})


if __name__ == "__main__":
    # go-basic.txtから、検索するためのdictを作り出す処理
    #
    # l = read_tsv_list(args.i)
    # go_list = extract_unique_ids()
    # cut_tsv(go_list, l)

    create_go_list()