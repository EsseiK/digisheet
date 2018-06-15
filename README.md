# digisheet

## 概要
ASPEX社のサービス[DigiSheet](
http://www.aspex.co.jp/service/digisheet_agency/)を python 上から操作するためのライブラリーです。

## 機能
以下の機能を持ちます。
- ログイン
- 勤務報告のページに移動
- 指定月への移動
- 未入力日（休日・祝日設定の日を除く）一覧の取得
- 指定日への勤怠入力ページへの移動
- （勤怠入力ページで）始業時刻／終業時刻の入力及び登録
- （勤怠入力ページで）登録削除

## 動作環境
Windows 環境で動作確認しています。
- python3
- selenium
- Chrome (Webブラウザー)
- Chrome Driver

## インストール方法

[こちら](https://www.inet-solutions.jp/technology/python-selenium/#Selenium)の記事が画像付きで丁寧に解説してくださっています。
以下は、分かっている人向けに簡単に記載しています。

### python3
特に難しい点はありません、以下を参考にしてください。

https://bi.biopapyrus.jp/os/win/win-install-python.html

### selenium
python3 をインストール後、コマンドプロンプトを起動し、 
`pip install selenium` を実行してください。

### Chrome

https://support.google.com/chrome/answer/95346?co=GENIE.Platform%3DDesktop&hl=ja

※　ブラウザーとして使用しているChoromeがある場合、そのまま使用できます。

### ChromeDriver
http://chromedriver.chromium.org/home

インストール済みのChromeの[バージョンを調べ](chrome://settings/help)、
[Download](http://chromedriver.chromium.org/downloads) ページより、対応するバージョンのドライバーをダウンロード、解凍してください。対応バージョンは当該ページに "Supports Chrome" として記述があります。

解凍後生成される chromedriver.exe を、digisheet.py と同じフォルダに移動させてください。（digisheet.py は相対パスで chromedriver.exe を呼び出す作りとしています。）


## サンプル
### 概要
`__init__` に、サンプルとして設定ファイルから月を指定し、その月の未入力勤怠を全て指定の始業／終業時刻で埋めるスクリプトを設けています。

### 使用準備
設定ファイルにあらかじめ情報を登録しておく必要があります。

digisheet.ini をテキストエディタで開き、下記の様内容を編集してください。
- `cd = 1234` のように派遣元CDを入力
- `id = 678910` のようにスタッフIDを入力
- `pass = PASSWORD` のようにパスワードを入力（空欄可。空欄の場合はスクリプト実行時に入力を求められる）
- `month = 6` のように対象となる月を入力
- `day = 0` とすると対象月の未入力の平日全てが入力対象日となる（通常はこちら）
- `day = 31` のように日付を指定すると、指定した日付が入力対象日となる
- `start = 9:00` のように始業時間を入力
- `end = 18:00` のように終業時間を入力

### 使用方法
1. コマンドプロンプトを起動し、本フォルダに移動してください。
1. `python dighisheet.py` と入力し、本スクリプトを起動してください。
1. 実行内容の確認を元まれます。何も入力せずに[Enter]もしくは 'y' あるいは 'Y' を入力し、[Enter] 押下でスクリプトを実行します。（'n' もしくは 'N' を入力した場合スクリプトは停止します）
1. （Chrome が起動し、自動入力を開始します）
1. 全ての項目の自動入力が終了後、スクリプトは自動的に終了します。