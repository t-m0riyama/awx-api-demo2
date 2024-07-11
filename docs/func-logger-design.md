AWX API DEMO 関数実行時のログ出力検討
===========================

トラブルシューティング時などに、処理が正常に実行されていることを確認するため、関数が呼び出された際の開始と終了を記録する機能を検討する。
本機能について、以下のような効果を期待する。

* 意図した処理が正常に実行されていることを、関数の呼び出し関係から把握
* 関数内での処理時間を記録することで、遅延度合いの確認
* 関数に渡された引数を記録することで、意図したデータが授受できているかどうかを確認（ログが増大するため、規定では無効）
* 標準的な機能として、関数から本機能を容易に利用できること

本ドキュメントでは、関数実行時のログ出力機能について検討する。

* 関数実行時のログ出力有効化
1. 環境変数「RMX_FUNC_LOGGER_ENABLED」にTrueをセットする
   下記の環境変数をセットすることで、関数実行時の引数をログ出力

| 環境変数名                        | 設定可能な値   |  概要                    |
| ------------------------------- | ------------ | ------------------------ |
| RMX_FUNC_LOGGER_ENABLED         | True/False   | Trueを指定した場合は関数実行時のログ出力を有効化する。True以外を指定した場合、もしくは本環境変数が存在しない場合は、関数実行時のログを出力しない。 |
| RMX_FUNC_LOGGER_ARGS_OUTPUT     | True/False   | Trueを指定した場合はログ出力に引数を含める。True以外を指定した場合、もしくは本環境変数が存在しない場合は、引数を出力しない。 |
| RMX_FUNC_LOGGER_ARGS_LENGTH_MAX | 整数          | 引数を出力する際に、各変数と値の最大長を指定した文字列長に制限する。 |

2. ログ出力を行いたい関数にデコレータ（@Logging.func_logger）を付加する
```デコレータ付加前
    def on_click_next(self, e):
        self.session.set('request_text', self.tfRequestText.value)
        self.step_change_next(e)
```
→
```デコレータ付加後
    @Logging.func_logger
    def on_click_next(self, e):
        self.session.set('request_text', self.tfRequestText.value)
        self.step_change_next(e)
```


* ログに記録する内容

| フィールド | 必須 | 概要 |
| --------------- | --- | ---------------------------------- |
| 時刻 | ✔︎ | ログが記録された時刻 |
| ログレベル | ✔︎ | 重要度 |
| ログメッセージ | ✔︎ | 操作内容の概要 |

* ログメッセージ中の内容

| フィールド | 必須 | 概要 |
| --------------- | --- | ---------------------------------- |
| ログメッセージ種別 | ✔︎ |  ログメッセージの種別（関数実行時のログについては、FUNC_CALLED） |
| 関数名 | ✔︎ |  モジュール名を含めた関数の名前 |
| start/end | ✔︎ | | 関数の開始/終了 |
| 引数 || 関数実行時に渡される引数（規定では引数のオブジェクトIDのみ出力し、内容は出力しない。） |

* ログの出力例

```log example　引数の出力なし
"2024/07/10 09:09:40"   INFO    FUNC_CALLED / awx_demo.components.forms.latest_request_list_form.get_query_filters: start (args_id=4832436640)
"2024/07/10 09:09:40"   INFO    FUNC_CALLED / awx_demo.db_helper.iaas_request_helper.get_filter_request_text: start (args_id=4833706496)
"2024/07/10 09:09:40"   INFO    FUNC_CALLED / awx_demo.db_helper.iaas_request_helper.get_filter_request_text: end (args_id=4833706496)
"2024/07/10 09:09:40"   INFO    FUNC_CALLED / awx_demo.db_helper.iaas_request_helper.get_filter_request_status: start (args_id=4833706496)
"2024/07/10 09:09:40"   INFO    FUNC_CALLED / awx_demo.db_helper.iaas_request_helper.get_filter_request_status: end (args_id=4833706496)
"2024/07/10 09:09:40"   INFO    FUNC_CALLED / awx_demo.components.forms.latest_request_list_form.get_query_filters: end (args_id=4832436640)
```

```log example　引数の出力あり
"2024/07/10 09:16:58" INFO FUNC_CALLED / awx_demo.db_helper.iaas_request_helper.get_filter_request_status: start (args_id=4416680128, args =
{'0': "['request approved', ~"})
"2024/07/10 09:16:58" INFO FUNC_CALLED / awx_demo.db_helper.iaas_request_helper.get_filter_request_status: end (args_id=4416680128)
```

