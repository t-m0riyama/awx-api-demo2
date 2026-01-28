AWX API DEMO キーボードショートカット一覧
====================================

* 申請一覧画面
  - 'F': 'shift':True,'ctrl':False,'alt':True		コントロールフォーカスの初期化
  - 'N': 'shift':True,'ctrl':False,'alt':True		申請の新規作成
  - 'Enter': 'shift':False,'ctrl':True,'alt':False		申請の検索
  - 'R': 'shift':False,'ctrl':True,'alt':True		申請の再読み込み
  - 'ArrowRight': 'shift':True,'ctrl':False,'alt'		次のページへ
  - 'ArrowLeft': 'shift':True,'ctrl':False,'alt'		前のページへ
  - 'I': 'shift':True,'ctrl':False,'alt':False		申請の状態変更（申請中）
  - 'P': 'shift':True,'ctrl':False,'alt':False		申請の状態変更（承認済み）
  - 'E': 'shift':True,'ctrl':False,'alt':False		申請の状態変更（完了）
  - 'R': 'shift':True,'ctrl':False,'alt':True		申請の削除
  - '0'-'9': 'shift':True,'ctrl':False,'alt':False		申請の編集
  - '0'-'9': 'shift':True,'ctrl':False,'alt':True		申請の選択・選択解除
  - 'L': 'shift':True,'ctrl':False,'alt':True		申請メニュー（最新）
  - 'D': 'shift':True,'ctrl':False,'alt':True		申請メニュー（リリース希望日）
  - 'M': 'shift':True,'ctrl':False,'alt':True		申請メニュー（自身の申請）
  - 'A': 'shift':True,'ctrl':False,'alt':True		申請メニュー（全て）
  - 'E': 'shift':True,'ctrl':False,'alt':True		申請メニュー（完了）
  - 'H': 'shift':True,'ctrl':False,'alt':True		申請メニュー（操作履歴）
  - 'T': 'shift':True,'ctrl':False,'alt':True		ダークモード/ライトモード切り替え
  - 'Q': 'shift':True,'ctrl':False,'alt':True		ログアウト
  - 'Y': 'shift':True,'ctrl':False,'alt':True		Semantic Debugger 有効/無効（デバッグ用）
  - 'V': 'shift':True,'ctrl':False,'alt':True		セッション情報のログ出力（デバッグ用）
  - 'Z': 'shift':True,'ctrl':False,'alt':True		キーボードショートカット一覧のログ出力（デバッグ用）

* 新規作成画面
  - 'F': 'shift':True,'ctrl':False,'alt':True		コントロールフォーカスの初期化（デバッグ用）
  - 'N': 'shift':True,'ctrl':False,'alt':True		次へ、申請する
  - 'P': 'shift':True,'ctrl':False,'alt':True		戻る
  - 'X': 'shift':True,'ctrl':False,'alt':True		キャンセル
  - '0'-'9': 'shift':True,'ctrl':False,'alt':False		仮想マシンの選択・選択解除(変更対象の仮想マシン)
  - '0'-'9': 'shift':True,'ctrl':False,'alt':True		変更対象仮想マシンの選択・選択解除(変更対象の仮想マシン(複数指定))
  - '0'-'9': 'shift':True,'ctrl':True,'alt':False		変更対象のスナップショットの選択・選択解除(スナップショットの指定)

* 編集画面
  * 全申請項目共通
    - 'F': 'shift':True,'ctrl':False,'alt':True		コントロールフォーカスの初期化（デバッグ用）
    - 'N': 'shift':True,'ctrl':False,'alt':True		実行
    - 'P': 'shift':True,'ctrl':False,'alt':True		戻る
    - 'S': 'shift':True,'ctrl':False,'alt':True		保存
    - 'D': 'shift':True,'ctrl':False,'alt':True		複製
    - 'X': 'shift':True,'ctrl':False,'alt':True		キャンセル
    - 'G': 'shift':True,'ctrl':False,'alt':True		共通タブに切り替え
    - 'A': 'shift':True,'ctrl':False,'alt':True		管理情報タブに切り替え
  * 「CPUコア/メモリの割り当て変更」の申請固有
    - 'I': 'shift':True,'ctrl':False,'alt':True		vCenterタブに切り替え
    - 'O': 'shift':True,'ctrl':False,'alt':True		変更対象の仮想マシンタブに切り替え
    - '0'-'9': 'shift':True,'ctrl':False,'alt':False		仮想マシンの選択・選択解除(変更対象の仮想マシンタブ)
    - '0'-'9': 'shift':True,'ctrl':False,'alt':True		変更対象仮想マシンの選択・選択解除(変更対象の仮想マシンタブ)
    - 'ArrowRight': 'shift':True,'ctrl':False,'alt'		選択した仮想マシンを変更対象に追加(変更対象の仮想マシンタブ)
    - 'ArrowLeft': 'shift':True,'ctrl':False,'alt'		選択した仮想マシンを変更対象から削除(変更対象の仮想マシンタブ)
    - 'C': 'shift':True,'ctrl':False,'alt':True		CPUタブに切り替え
    - 'M': 'shift':True,'ctrl':False,'alt':True		メモリタブに切り替え
  * 「サーバの停止/起動」の申請固有
    - 'I': 'shift':True,'ctrl':False,'alt':True		vCenterタブに切り替え
    - 'O': 'shift':True,'ctrl':False,'alt':True		変更対象の仮想マシンタブに切り替え
    - '0'-'9': 'shift':True,'ctrl':False,'alt':False		仮想マシンの選択・選択解除(変更対象の仮想マシンタブ)
    - '0'-'9': 'shift':True,'ctrl':False,'alt':True		変更対象仮想マシンの選択・選択解除(変更対象の仮想マシンタブ)
    - 'ArrowRight': 'shift':True,'ctrl':False,'alt'		選択した仮想マシンを変更対象に追加(変更対象の仮想マシンタブ)
    - 'ArrowLeft': 'shift':True,'ctrl':False,'alt'		選択した仮想マシンを変更対象から削除(変更対象の仮想マシンタブ)
    - 'B': 'shift':True,'ctrl':False,'alt':True		起動/停止タブに切り替え
  * 「スナップショットの操作」の申請固有
    - 'I': 'shift':True,'ctrl':False,'alt':True		vCenterタブに切り替え
    - 'O': 'shift':True,'ctrl':False,'alt':True		変更対象の仮想マシンタブに切り替え
    - '0'-'9': 'shift':True,'ctrl':False,'alt':False		仮想マシンの選択・選択解除(変更対象の仮想マシンタブ)
    - '0'-'9': 'shift':True,'ctrl':False,'alt':True		変更対象仮想マシンの選択・選択解除(変更対象の仮想マシンタブ)
    - 'ArrowRight': 'shift':True,'ctrl':False,'alt'		選択した仮想マシンを変更対象に追加(変更対象の仮想マシンタブ)
    - 'ArrowLeft': 'shift':True,'ctrl':False,'alt'		選択した仮想マシンを変更対象から削除(変更対象の仮想マシンタブ)
    - 'B': 'shift':True,'ctrl':False,'alt':True		スナップショットの操作タブに切り替え
    - 'C': 'shift':True,'ctrl':False,'alt':True		スナップショットの指定タブに切り替え
    - '0'-'9': 'shift':True,'ctrl':True,'alt':False		変更対象のスナップショットの選択・選択解除(スナップショットの指定タブ)
