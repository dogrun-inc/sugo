import csv
import argparse
from dataclasses import dataclass
import glob
import sqlite3
import re
import os
import requests
from requests.exceptions import HTTPError
from requests import exceptions

parser = argparse.ArgumentParser(description="add filter")
parser.add_argument("-d", help="specify the path of go obo file", required=True)
parser.add_argument(
    "-s", help="database path which store the result dataset", required=True
)
parser.add_argument("-g", help="keyword to grep")
parser.add_argument(
    "-i", help="specify the directory where source tsv file located", required=True
)

args = parser.parse_args()
url = "http://purl.obolibrary.org/obo/go/go-basic.obo"
go_obo = "{}/go-basic.obo".format(args.d)
go_full_list = []
go_filtered_list = []

# Todo: i) 設定しディレクトリにgo-basic.oboが無ければ, ii) 全ての操作前にgo-basic.oboをwget等する処理が必要
# ファイルがあればgo_obo変数にファイルへのパスを保存。
#     ファイルがなければurlからファイルを取得してgo-oboにパスを保存。


def check_dir(path: str) -> bool:
    """
    -d で受け取ったディレクトリがあるか確認して、なければエラーメッセージを出す。
    ディレクトリがあれば、`go-basic.obo`ファイルがあるかの有無を出力。

    Parameters:
    -----------------
    path: str
        -dで受け取ったディレクトリのパス。

    Returns:
    ----------------
    bool
        go-basic.oboがあればTrue、なければFalse
    """
    if not os.path.isdir(path):
        return False

    go_obo = os.path.join(path, "/go-basic.obo")
    return os.path.isfile(go_obo)


def get_basic_obo() -> str:
    """
    Returns:
    --------------
    data: str
        requestsで取得したgo-basic.oboのデータ
    """
    data = requests.get("http://purl.obolibrary.org/obo/go/go-basic.obo").content
    return data


def main():
    # -dで受け取ったディレクトリにgo-basic.oboファイルがあるかを確認。
    if not check_dir(args.d):
        # なければgetdata関数を使ってgo-basic.oboファイルをダウンロード。
        getgobasic = get_basic_obo()
        with open(go_obo, mode="wb") as f:
            f.write(getgobasic)

    create_go_list()
    # 0埋めしたスパースなデータセットをsqliteに保存
    # Todo: コマンドを叩く度に読み込むなら, 全長のsqlite storeする必要無いのでは？？
    cut_tsv(read_tsv_list(args.i))


def read_tsv_list(dir_path: str) -> list:
    """
    オプションとして設定したディレクトリから".tsv"ファイルのリストを取得し返す
    Todo: .tsvだけで無く、tab,txtなども考慮する必要がある
    """
    l = glob.glob(f"{dir_path}/*.tsv")
    return l


# 行の先頭がidのものだけ抽出することで、GO_termのみのリストを作成する。
def extract_unique_ids() -> list:
    go_list = []
    with open(go_obo, "r") as f:
        for line in f:
            if line.startswith("id"):
                go_list.append(line.split(" ")[1].strip())

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
        # Todo: ファイル名からサンプル名を取得する方法が現在のファイル限定すぎるので要改善。
        # 位置指定ではなく、パスを指定しPrefixを定義し、SR\w+的に取得する
        sample_name = re.split("\.|/", filename)[1]
        with open(f"./{filename}", encoding="utf-8", newline="") as f:
            # 1レコードGO: TPMを辞書に追加追加
            for row in csv.reader(f, delimiter="\t"):
                feature_dataset[row[0]] = row[1]

        # go-basic.oboの全長に対してマッピングしたデータセットをsqliteに保存
        # go, tpmの2カラムのデータを保存
        # Todo: 下のブロックのgrepしたリストとこのgo全長のリストを別々に生成するため冗長。要改善
        records = []
        for go in go_full_list:
            # goがfeature_datasetに含まれる場合そのTPM値を渡してリスト（list of tuple）を生成する
            if go in feature_dataset:
                records.append([go, feature_dataset[go]])
            # goがfeature_datasetに含まれない場合TPMカラムを0で埋める
            else:
                records.append((go, 0))

        # テーブル(sample, go, TPM )作成
        create_table(args.s)
        # Todo: store_data()実装
        store_data(args.s, sample_name, records)
        # Todo インデックスの生成するかは検討（grepしたいでけの場合、インデックスは必要が無いが実行時間は掛かるため）

        # grepされた(GO, TPM) listを生成する
        filtered_list = []
        # フィルターされたGOリストでサンプルごとのTPMデータセットを舐め、値の入力もしくは０埋めする
        for go in go_filtered_list:
            if go in feature_dataset:
                filtered_list.append([go, feature_dataset[go]])
            else:
                filtered_list.append([go, 0])

        write_tsv(sample_name, filtered_list)


def create_table(path):
    # テーブルが存在しなかった場合作成
    q = "CREATE TABLE IF NOT EXISTS GO_TPM (Sample TEXT, GO TEXT, TPM NUMBER)"
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute(q)
    con.commit()
    con.close()


def store_data(path, sample_name, dataset_lst):
    dataset_lst = [(sample_name, x[0], x[1]) for x in dataset_lst]
    q = "INSERT INTO GO_TPM (Sample, GO, TPM) VALUES(?, ?, ?)"
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executemany(q, dataset_lst)
    con.commit()


def create_index():
    con = sqlite3.connect(args.s)
    cur = con.cursor()
    # Indexがすでに存在する場合Indexを消す
    q = "CREATE INDEX go_index ON go_tpm(GO)"
    cur.execute(q)
    q = "CREATE INDEX sample_index ON go_tpm(Sample)"
    cur.execute(q)
    con.commit()
    con.close()


def write_tsv(sample_name, lst):
    with open(f"./data/{sample_name}.tsv", "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(lst)


if __name__ == "__main__":
    main()
