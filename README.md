# sugo

## Main Features

- 発現データセットをgo.oboに対して正規化してストアまたはgrepするPythonコマンドラインユーティリティ。
- go x sampleの発現データをTSVファイルから読み込み、go-basic.obo全長に対してマッピングしたデータを生成しsqliteに保存する。
- 検索キーワードを設定した場合、go-basic.oboにキーワードが含まれる行をgrepしtsvに書き出す。

## Installation

- sugoをgit clone
- ローカルレポジトリに移動し（setup.pyと同じディレクトリに）
- ```pip install -e . ```


## Usage

```
sugo -g phosphorylation -i test_samples
```


###　Options

- ```- i ```:入力サンプルのディレクトリを指定。必須
- ```- g ```:grepする検索キーワードを指定する。このオプションをつけた場合、grepの結果がタブ区切りファイルに書き出される。

## Dependency

Python3.7以上