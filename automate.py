import time
from selenium import webdriver
import shutil
import stat
from pathlib import Path
import os


class Selenium:
    driver = None
    element = None

    # ファイル実行権限を付与する関数
    def addExecutePermission(self, path: Path, target: str = "u"):
        # https://www.lifewithpython.com/2017/10/python-add-file-permission.html
        # stat : https://docs.python.org/ja/3/library/stat.html
        mode_map = {
            "u": stat.S_IXUSR,
            "g": stat.S_IXGRP,
            "o": stat.S_IXOTH,
            "a": stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
        }

        # 現在所有するファイル権限をmode変数へ集約する。
        mode = path.stat().st_mode
        # 追加したいファイル権限を格納する。
        for t in target:
            # http://www.tohoho-web.com/python/operators.html
            mode |= mode_map[t]

        # chmod : https://www.lifewithpython.com/2017/10/python-add-file-permission.html
        path.chmod(mode)

    def settingDriver(self, driverPath, replaceDriverPath, headlessPath, replaceHeadlessPath):
        # copy and change permission
        # GoogleCloudFunctionsへデプロイすると、chromedriverなどのファイルはカレントディレクトリ"/user_code"にあります。
        # ただしこの配下のファイルにはアクセスできません。代わりに"/tmp"フォルダであればユーザーが自由にアクセスできます。
        # https://qiita.com/NearMugi/items/8146306168dd6b41b217
        # copyfile : https://python.keicode.com/lang/file-copy.php#1
        shutil.copyfile(os.getcwd() + driverPath, replaceDriverPath)
        # Path : https://note.nkmk.me/python-pathlib-usage/
        self.addExecutePermission(Path(replaceDriverPath), "ug")

        # copy and change permission
        # GoogleCloudFunctionsへデプロイすると、chromedriverなどのファイルはカレントディレクトリ"/user_code"にあります。
        # ただしこの配下のファイルにはアクセスできません。代わりに"/tmp"フォルダであればユーザーが自由にアクセスできます。
        # https://qiita.com/NearMugi/items/8146306168dd6b41b217
        shutil.copyfile(os.getcwd() + headlessPath, replaceHeadlessPath)
        # Path : https://note.nkmk.me/python-pathlib-usage/
        self.addExecutePermission(Path(replaceHeadlessPath), "ug")

    def __init__(self):
        driverPath = "/chromedriver"
        headlessPath = "/headless-chromium"
        replaceDriverPath = '/tmp' + driverPath
        replaceHeadlessPath = '/tmp' + headlessPath

        self.settingDriver(driverPath, replaceDriverPath,
                           headlessPath, replaceHeadlessPath)

        # https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.chrome.options
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        # https://developers.google.com/web/updates/2017/04/headless-chrome?hl=ja
        options.add_argument("--disable-gpu")
        # ウィンドウ幅設定
        options.add_argument("--window-size=1280x1696")
        # https://daily.belltail.jp/?p=2691
        options.add_argument("--no-sandbox")
        # スクロールバーを表示しない
        options.add_argument("--hide-scrollbars")
        # ログ周り : https://qiita.com/grohiro/items/718239cdd36da42bd517#%E3%83%AD%E3%82%B0%E3%82%92%E5%87%BA%E3%81%99
        options.add_argument("--enable-logging")
        # ログ周り : https://qiita.com/grohiro/items/718239cdd36da42bd517#%E3%83%AD%E3%82%B0%E3%82%92%E5%87%BA%E3%81%99
        options.add_argument("--log-level=0")
        # http://chrome.half-moon.org/43.html#e25988df
        options.add_argument("--single-process")
        # ssh証明書周りのエラー回避
        options.add_argument("--ignore-certificate-errors")
        # https://daily.belltail.jp/?p=2691
        options.add_argument("--disable-dev-shm-usage")

        options.binary_location = replaceHeadlessPath

        self.driver = webdriver.Chrome(
            replaceDriverPath, chrome_options=options)

    def access(self, url):
        self.driver.get(url)

    def find_element_by_id(self, name):
        self.element = self.driver.find_element_by_id(name)

    def get_element(self):
        return self.element

    def stop(self, num):
        time.sleep(num)

    def quit(self):
        self.driver.quit()
