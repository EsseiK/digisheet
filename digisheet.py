# coding:utf-8
# pylint:disable=E0401

"""
勤怠報告 (DigiSheet) の勤怠入力自働化用スクリプトです。

■　機能
指定月の未入力の勤怠に対し、指定した時間を入力し登録します。

※　エラー処理は行っていません。
※　回線環境により動作が不安定な場合があります。

■　動作環境
以下の動作環境で動作を確認しています。
・Windows 10 [64bit]
・Python: 3.6.5
・selenium: 3.11.0

※　環境構築方法及び使用方法については、Git もしくは Quiita のページを参照してください。


■　TODO
・パスワードを平文で保存する仕様を変更したい。
・ページ遷移の処理に time.sleep を使用している個所をなくしたい。
　（通信環境によらず安定して動作するようにしたい）

■　既知のバグ
・DIGISHEET のページがセッション切れとなる場合がある。

"""

__author__ = "Essei Kuroda"
__credits__ = ["Essei Kuroda"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Essei Kuroda"
__email__ = "e-kuroda@progresstech.jp"
__status__ = "Production"
__date__ = "16 June 2018"

import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.options import Options

# Chrome をインストールすること。
# Chrome のバージョンに応じた chromedriver をインストールすること。
# (例) https://chromedriver.storage.googleapis.com/index.html?path=2.4/


class Digisheet:

    ## クラス変数 ################################################################################

    """ Web ページ、ロード完了までの最大待ち時間。 """
    TIME_TO_WAIT_LOAD = 10

    ## コンストラクター ##########################################################################

    def __init__(self):
        """
        デフォルト・コンストラクター。
        """

        options = Options()

        # デバッグ時は下記をコメントアウトする。
        #  ⇒ Chrome画面が表示される。（速度は遅くなる）
        # options.add_argument('--headless')

        # Chrome 起動
        self._browser = webdriver.Chrome(
            executable_path='./chromedriver.exe', chrome_options=options)

        return

    ## プライベート・メソッド ####################################################################

    def _set_forcus_to(self, target):
        """フレームのフォーカスを設定する。"""
        self._browser.switch_to.default_content()
        self._browser.switch_to.frame(target)
        return

    def _get_element(self, target, base=None):
        """XPATH で指定した target を（ページロードを待ち）得る。"""
        if base is None:
            base = self._browser
        return WebDriverWait(base, Digisheet.TIME_TO_WAIT_LOAD).until(
            EC.presence_of_element_located((
                By.XPATH, target)))

    def _click(self, target):
        """XPATH で指定した target をクリックする。"""
        self._get_element(target).click()
        return

    def _send_key(self, target, value):
        """XPATH で指定した target をに値 value を設定する。"""
        self._get_element(target).send_keys(value)
        return

    def _select(self, target, value):
        """XPATH で指定した trget(Select) 内の value に一致するものを選択する。"""
        if isinstance(value, str) is False:
            value = str(value)
        Select(self._get_element(target)).select_by_visible_text(value)
        return

    def _wait_for_load_timelog(self):
        """勤怠一覧画面が最後まで読み込まれるのを待機する。"""
        self._set_forcus_to('main')
        # 最後の方に読み込まれる要素を指定し、読み込み待ち。
        self._wait_for_load('//*[@id="topb"]')
        return

    def _wait_for_load(self, target):
        """指定 XPATH が読み込まれるまで待機する。"""
        self._get_element(target)
        return

    def _get_days(self, search_type):
        """
        未入力日／入力日のリスト取得。

        search_type = "uninput" の場合、未入力日のリストを戻す。
        search_type = "input" の場合、入力済みの日のリストを戻す。
        search_type = "holiday" の場合、休日設定されている日のリストを戻す。


        （前提）
        ・勤怠報告ページに遷移していること。
        """
        target = '/html/body/form/table/tbody/tr[7]/td/table/tbody/tr'

        # 勤怠入力のページの読み込み完了待ち。
        self._wait_for_load_timelog()

        if search_type == "uninput":
            search_target = "hidden"
        elif search_type == "input":
            search_target = "checkbox"
        elif search_type == "holiday":
            pass
        else:
            raise Exception('ArgumentException', 'search_type')

        # メインページを設定対象にする。
        self._set_forcus_to('main')

        ret = []
        # リスト取得。
        trList = self._browser.find_elements_by_xpath(target)

        # bgcolor が white ⇒ 平日 かつ、type が hidden ⇒ チェックボックスが表示されていない ⇒ 未入力 の
        # 日付を得る。
        for i, trTmp in enumerate(trList):
            tmpBgcolor = trTmp.get_attribute("bgcolor")
            if tmpBgcolor == "white":

                tmpType = self._get_element(
                    base=trTmp, target='./td/input[2]').get_attribute('type')
                if tmpType == search_target:
                    ret.append(i)
            elif search_target == "horiday":
                ret.append(i)

        return ret

    ## パブリック・メソッド ######################################################################

    def login(self, hc, ui, pw):
        """ログイン実行。"""

        # 共通 XPATH。
        base = '/html/body/form/center/table/tbody/tr/td/table/tbody'

        # ログインページにアクセス。
        self._browser.get('https://www2.digisheet.com/staffLogin')

        # ログインに必要な情報を入力。
        self._send_key(
            base + '/tr[3]/td/input', hc)
        self._send_key(
            base + '/tr[4]/td/input', ui)
        self._send_key(
            base + '/tr[5]/td/input', pw)

        # ログインボタン押下。
        self._click(
            base + '/tr[6]/td/table/tbody/tr/th[1]/input')

        return

    def goto_timelog(self):
        """
        勤怠報告ページに移動。

        （前提）
        ・ログインが完了していること。
        """
        self._set_forcus_to('menu')

        # 勤務報告 クリック。
        self._click('/html/body/form/div[5]/table/tbody/tr[7]/td/a')

        return

    def change_timelog_month(self, month):
        """
        勤怠報告の月次を変更。

        （前提）
        ・勤怠報告ページに遷移していること。
        """

        # 勤怠入力のページの読み込み完了待ち。
        self._wait_for_load_timelog()

        base = '/html/body/form/table/tbody/tr[1]/td/table/tbody/tr'

        self._set_forcus_to('main')

        # 月を入力
        self._select(base + '/td[2]/select[2]', month)

        # 入力反映。（ページ移動）
        self._click(base + '/td[5]/input')

        return

    def get_uninput_days(self):
        """
        未入力の日付リスト取得。

        （前提）
        ・勤怠報告ページに遷移していること。
        """
        return self._get_days("uninput")

    def get_input_days(self):
        """
        入力済の日付リスト取得。

        （前提）
        ・勤怠報告ページに遷移していること。
        """
        return self._get_days("input")

    def goto_timelog_input(self, day):
        """
        勤務入力ページに遷移する。

        （前提）
        ・勤怠報告ページに遷移していること。
        """
        if day < 1 or day > 31:
            return

        self._set_forcus_to('main')
        target = '/html/body/form/table/tbody/tr[7]/td/table/tbody/tr[{0}]/td[3]/a'.format(
            day + 1)
        self._click(target)
        return

    def register_timelog(self, time_start, time_end):
        """
        勤務入力に始業時間と終業時間を入力する。

        （前提）
        ・勤怠報告入力ページに遷移していること。
        """

        base = '/html/body/form/table/tbody/tr[3]/td/table/tbody/'
        base2 = 'tr[4]/td/table/tbody/'
        base3 = 'td[2]/table/tbody/tr/td/'

        self._set_forcus_to('main')

        # インスタンスをDatetime型に統一。
        if isinstance(time_start, str) is True:
            time_start = datetime.datetime.strptime(time_start, '%H:%M')
        if isinstance(time_end, str) is True:
            time_end = datetime.datetime.strptime(time_end, '%H:%M')

        # 値を選択。
        self._select(base + base2 + 'tr[1]/' +
                     base3 + 'select[1]', str(time_start.hour))
        self._select(base + base2 + 'tr[1]/' +
                     base3 + 'select[2]', str(time_start.minute).zfill(2))
        self._select(base + base2 + 'tr[2]/' +
                     base3 + 'select[1]', str(time_end.hour))
        self._select(base + base2 + 'tr[2]/' +
                     base3 + 'select[2]', str(time_end.minute).zfill(2))

        # 登録する。
        self._click(base + '/tr[7]/td/table/tbody/tr/td/input[1]')

        return

    def delete_timelog(self):
        """
        入力された勤務時間を削除する。

        （前提）
        ・勤怠報告入力ページに遷移していること。
        """

        # 削除する。
        self._click(
            '/html/body/form/table/tbody/tr[3]/td/table/tbody/tr[7]/td/table/tbody/tr/td/input[2]')
        return


if __name__ == "__main__":

    import sys
    import configparser
    import time

    # 必要な情報の設定 ###########################################################################

    # ini ファイルよりデーターを得る。
    INIFILE = configparser.ConfigParser()
    INIFILE.read('./digisheet.ini', 'UTF-8')

    # ログイン情報を取得する。
    CD = INIFILE.get('login', 'cd')
    ID = INIFILE.get('login', 'id')
    PASS = INIFILE.get('login', 'pass')
    if not PASS:
        print("DigiSheetへのログインパスワードを入力してください：", end="")
        PASS = input()

    # 登録内容をあらかじめ取得する。
    MONTH = int(INIFILE.get('logtime', 'month'))
    DAY = int(INIFILE.get('logtime', 'day'))
    TIME_START = str(INIFILE.get('logtime', 'start'))
    TIME_END = str(INIFILE.get('logtime', 'end'))

    # 情報表示・確認 #############################################################################

    print("-------------------------------------------------")
    print("DigiSheet 勤怠入力自働化ソフトウェア (ver.{0})\n".format(__version__))

    print("　以下の設定で勤怠入力を実行します。よろしいですか？")
    print("　・対象月：{0}月".format(MONTH))
    if DAY == 0:
        print("　・対象日：全て")
    else:
        print("　・対象日：{0}日".format(DAY))
    print("　・勤務時間：{0} ～ {1}".format(TIME_START, TIME_END))

    while(True):
        print("　([y]/n):", end="")
        TMP_INPUT = input()
        if TMP_INPUT == "" or TMP_INPUT.upper() == "Y":
            break
        elif TMP_INPUT.upper() == "N":
            print("終了します。")
            sys.exit()
        else:
            print("y か n を入力してください。")

    # 処理実行 ###################################################################################

    print("-------------------------------------------------")

    DIGISHEET = Digisheet()

    print("(1) ログイン実行")
    DIGISHEET.login(CD, ID, PASS)

    print("(2) 勤務報告ページに移動")
    DIGISHEET.goto_timelog()

    time.sleep(3)

    print("(3) 指定の月（{0}月）に移動".format(MONTH))
    DIGISHEET.change_timelog_month(MONTH)

    # ページの遷移開始待ち。
    time.sleep(3)

    if DAY == 0:
        print("(4) 未入力日のリスト取得")
        TARGET_DAYS = DIGISHEET.get_uninput_days()

        print(" (4-1) 未入力は{0}日あります".format(len(TARGET_DAYS)))
    else:
        print("(4) 指定の日付を得る")
        TARGET_DAYS = [DAY]

    print("(5) 指定日に入力実行")
    for i, day in enumerate(TARGET_DAYS):

        print(" (5-1) {0}月{1}日 の勤務入力ページに遷移 ({2}/{3})".format(MONTH, day,
                                                             i, len(TARGET_DAYS)))
        DIGISHEET.goto_timelog_input(day)
        time.sleep(5)
        print(" (5-2) 勤務時間{0}-{1}を入力し、登録".format(TIME_START, TIME_END))
        DIGISHEET.register_timelog(TIME_START, TIME_END)

    print("(6) 終了")
