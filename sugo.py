import csv
import argparse
import glob

parser = argparse.ArgumentParser(description='add filter')
parser.add_argument('-s')
parser.add_argument('-g')
parser.add_argument('-i')

args = parser.parse_args()

"""
- 引数を取得し、データを出力する範囲を設定する
- またオプションとして書き出し形式も設定する
- TSVファイルを読み込み必要な部分を整形する。TSVを設置するディレクトリはオプションで設定する。
- データの正規化：取得したGO-basicに合わせてTSVの足りないデータを0で埋める
- ファイルを書き出す 
"""

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
    
    return go_list[1:100]


def cut_tsv(go: list, l:list)-> list:
    i=0

    for tsv_filename in l:
        i = i+1
        list_name = "tsv_output_{}".format(i)
        list_name = []
        with open('./{}'.format(tsv_filename), encoding='utf-8', newline='') as f:
            for cols in csv.reader(f):
                # print(cols)
                for x in cols:
                    go_sample = x[0]
                    tpm = x[1]
                    for go_term in go:
                        if go_term == go_sample:
                            list_name.append({go_term:tpm})
                        else:
                            list_name.append({go_term:0})

        print(list_name)


if __name__ == "__main__":
    # go-basic.txtから、検索するためのdictを作り出す処理
    # 


    l = read_tsv_list(args.i)
    go_list = extract_unique_ids()
    cut_tsv(go_list, l)

