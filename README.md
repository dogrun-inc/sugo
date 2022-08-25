# sugo

## Main Features

- 発現データセットをgo.oboに対して正規化してストアまたはgrepするPythonコマンドラインユーティリティ。
- go x sampleの発現データをTSVファイルから読み込み、go-basic.obo全長に対してマッピングしたデータを生成しsqliteに保存する。
- 検索キーワードを設定した場合、go-basic.oboにキーワードが含まれる行をgrepしtsvに書き出す。

## Installation

- sugoをgit clone
- ローカルレポジトリに移動し（setup.pyと同じディレクトリに）
- レポジトリ内のパッケージをpip installする
    - ```pip install -e . ```


## Usage

```
sugo -g phosphorylation -i test_samples -s ./data/sugo.db -d ./data/go-basic.obo
```

### sample_appの場合

テストサーバを起動し、例えばフォームに"data", "test_samples", "oxidation"のように記述しsubmitボタンをクリックすると
go-basic.oboのパス。サンプルデータのパス、キーワードがわたされ、メタスタンザが表示される。


###　Options

- -i : 入力サンプルのディレクトリ(実行場所からの相対パス)を指定。必須
- -g : grepする検索キーワードを指定する。このオプションをつけた場合、grepの結果がタブ区切りファイルに書き出される。
- -d : go-basic.oboのパスを指定する。必須
- -s : sqlite dbのパス(データベース名まで)を指定する。必須

## Dependency

Python3.7以上