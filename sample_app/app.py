import os, sys
import json
from sugo.sugo import metastanza_response
from bottle import route, run, static_file, request, response


"""
0. index.htmlの表示
1. Web formからsugoのパラメータを入力しsubmit -> sugoを呼ぶ
2. sugoの処理（JSONモード）後、JSONを取得
3. 
"""

@route('/')
def index():
    return static_file('index.html', './static')


@route('/api')
def get_restult_json():
    """
    sugoを呼び出しその戻り値のdictを取得しJSONとして返す
    parameterはフォームより取得
    :return: Metastanza用JSON
    """
    obo_file = request.query["obo"]
    sample_file = request.query["sample"]
    keyword = request.query["keywd"]
    dct = metastanza_response(obo_file, sample_file, keyword)
    #res_test = [{"Sample": "str1","GO": "str_go", "Exp": 1.0 },{"Sample": "str2","GO": "str_go", "Exp": 1.0 }]
    return json.dumps(dct)


if __name__ == "__main__":
    run(host="localhost", port=8000, debug=True, reloader=True)
