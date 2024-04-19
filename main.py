# This is a sample Python script.
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import traceback
import zipfile

import requests
from colorama import Fore, Style, init
from selenium.webdriver import Chrome, ChromeOptions, ChromeService
from selenium.webdriver import Edge, EdgeOptions, EdgeService
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxService

EMAIL_API = None
DEBUG_MODE = False
DEFAULT_MAX_ITER = 30
DEFAULT_DELAY = 1
GET_EBN = 'document.getElementsByName'
GET_EBCN = 'document.getElementsByClassName'
GET_EBID = 'document.getElementById'
GET_EBTN = 'document.getElementByTagName'
GET_EBAV = 'getElementByAttrValue'
CLICK_WITH_BOOL = 'clickWithBool'
PARSE_10MINUTEMAIL_INBOX = 'parse_10minutemail_inbox()'
DEFINE_GET_EBAV_FUNCTION = """
function getElementByAttrValue(tagName, attrName, attrValue) {
    for (let element of document.getElementsByTagName(tagName)) {
        if(element.getAttribute(attrName) === attrValue)
            return element } }"""
DEFINE_CLICK_WITH_BOOL_FUNCTION = """
function clickWithBool(object) {
    try {
        object.click()
        return true }
    catch {
        return false } }"""
init()


class LoggerType:
    def __init__(self, sborder, eborder, title, color, fill_text):
        self.sborder = sborder
        self.eborder = eborder
        self.title = title
        self.color = color
        self.fill_text = fill_text

    @property
    def data(self):
        return self.sborder + self.color + self.title + Style.RESET_ALL + self.eborder


ERROR = LoggerType('[ ', ' ]', 'FAILED', Fore.RED, True)
OK = LoggerType('[   ', '   ]', 'OK', Fore.GREEN, False)
INFO = LoggerType('[  ', '  ]', 'INFO', Fore.LIGHTBLACK_EX, True)
DEVINFO = LoggerType('[ ', ' ]', 'DEBUG', Fore.CYAN, True)


def console_log(text='', logger_type=None, fill_text=None):
    if isinstance(logger_type, LoggerType):
        ni = 0
        for i in range(0, len(text)):
            if text[i] != '\n':
                ni = i
                break
            print()
        if logger_type.fill_text and fill_text is None:
            fill_text = True
        if logger_type.fill_text and fill_text:
            print(logger_type.data + ' ' + logger_type.color + text[ni:] + Style.RESET_ALL)
        else:
            print(logger_type.data + ' ' + text[ni:])
    else:
        print(text)


class SharedTools(object):
    def untilConditionExecute(driver_obj, js: str, delay=DEFAULT_DELAY, max_iter=DEFAULT_MAX_ITER, positive_result=True,
                              raise_exception_if_failed=True, return_js_result=False):
        driver_obj.execute_script(f'window.{GET_EBAV} = {DEFINE_GET_EBAV_FUNCTION}')
        driver_obj.execute_script(f'window.{CLICK_WITH_BOOL} = {DEFINE_CLICK_WITH_BOOL_FUNCTION}')
        pre_js = [
            DEFINE_GET_EBAV_FUNCTION,
            DEFINE_CLICK_WITH_BOOL_FUNCTION
        ]
        ojs = js
        js = '\n'.join(pre_js + [js])
        if DEBUG_MODE:
            # js_logfile.write(
            #     (f'\nuntilConditionExecute:\njs={ojs}\npositive_result={positive_result}\n').encode('utf-8'))
            console_log(f'\nuntilConditionExecute:\njs={ojs}\npositive_result={positive_result}\n')
        for _ in range(max_iter):
            try:
                result = driver_obj.execute_script(js)
                if DEBUG_MODE:
                    # js_logfile.write((f'\nuntilConditionExecute:\nexecute result={result}\n').encode('utf-8'))
                    console_log(f'\nuntilConditionExecute:\nexecute result={result}\n')
                if return_js_result and result is not None:
                    return result
                elif result == positive_result:
                    return True
            except Exception as E:
                pass
            time.sleep(delay)
        if raise_exception_if_failed:
            raise RuntimeError('untilConditionExecute: the code did not return the desired value! TRY VPN!')

    def initSeleniumWebDriver(browser_name: str, webdriver_path=None, browser_path='', headless=True):
        driver_options = None
        driver = None
        if browser_name.lower() == 'chrome':
            driver_options = ChromeOptions()
            driver_options.binary_location = browser_path
            driver_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver_options.add_argument("--log-level=3")
            driver_options.add_argument("--lang=en-US")
            if headless:
                driver_options.add_argument('--headless')
            driver_service = ChromeService(executable_path=webdriver_path)
            if os.name == 'posix':  # For Linux
                if sys.platform.startswith('linux'):
                    console_log('Initializing chrome-webdriver for Linux', INFO)
                elif sys.platform == "darwin":
                    console_log('Initializing chrome-webdriver for macOS', INFO)
                driver_options.add_argument('--no-sandbox')
                driver_options.add_argument('--disable-dev-shm-usage')
            elif os.name == 'nt':
                console_log('Initializing chrome-webdriver for Windows', INFO)
            driver = Chrome(options=driver_options, service=driver_service)
        elif browser_name.lower() == 'firefox':
            driver_options = FirefoxOptions()
            driver_options.binary_location = browser_path
            driver_service = FirefoxService(executable_path=webdriver_path)
            driver_options.set_preference('intl.accept_languages', 'en-US')
            if headless:
                driver_options.add_argument('--headless')
            if os.name == 'posix':  # For Linux
                if sys.platform.startswith('linux'):
                    console_log('Initializing firefox-webdriver for Linux', INFO)
                elif sys.platform == "darwin":
                    console_log('Initializing firefox-webdriver for macOS', INFO)
                driver_options.add_argument('--no-sandbox')
                driver_options.add_argument("--disable-dev-shm-usage")
            else:
                console_log('Initializing firefox-webdriver for Windows', INFO)
            driver = Firefox(options=driver_options, service=driver_service, )
        elif browser_name.lower() == 'edge':
            driver_options = EdgeOptions()
            driver_options.use_chromium = True
            driver_options.binary_location = browser_path
            driver_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver_options.add_argument("--log-level=3")
            driver_options.add_argument("--lang=en-US")
            if headless:
                driver_options.add_argument('--headless')
            driver_service = EdgeService(executable_path=webdriver_path)
            if os.name == 'posix':  # For Linux
                if sys.platform.startswith('linux'):
                    console_log('Initializing edge-webdriver for Linux', INFO)
                elif sys.platform == "darwin":
                    console_log('Initializing edge-webdriver for macOS', INFO)
                driver_options.add_argument('--no-sandbox')
                driver_options.add_argument('--disable-dev-shm-usage')
            elif os.name == 'nt':
                console_log('Initializing edge-webdriver for Windows', INFO)
            driver = Edge(options=driver_options, service=driver_service)
        return driver


class WebDriverInstaller(object):
    def __init__(self):
        self.platform = ['', []]
        if sys.platform.startswith('win'):
            self.platform[0] = 'win'
            if sys.maxsize > 2 ** 32:
                self.platform[1] = ['win64', 'win32']
            else:
                self.platform[1] = ['win32']
        elif sys.platform.startswith('linux'):
            self.platform[0] = 'linux'
            if sys.maxsize > 2 ** 32:
                self.platform[1].append('linux64')
            else:
                self.platform[1].append('linux32')
        elif sys.platform == "darwin":
            self.platform[0] = 'mac'
            if platform.processor() == "arm":
                self.platform[1] = ['mac-arm64', 'mac_arm64', 'mac64_m1']
            elif platform.processor() == "i386":
                self.platform[1] = ['mac64', 'mac-x64']
        if self.platform[0] == '' or self.platform[1] == []:
            raise RuntimeError('WebDriverInstaller: impossible to define the system!')

    def get_chrome_version(self):
        if self.platform[0] == "linux":
            path = None
            for executable in (
                    "google-chrome", "google-chrome-stable", "google-chrome-beta", "google-chrome-dev",
                    "chromium-browser",
                    "chromium"):
                path = shutil.which(executable)
                if path is not None:
                    with subprocess.Popen([path, "--version"], stdout=subprocess.PIPE) as proc:
                        chrome_version = \
                            proc.stdout.read().decode("utf-8").replace("Chromium", "").replace("Google Chrome",
                                                                                               "").strip().split()[0]
        elif self.platform[0] == "mac":
            process = subprocess.Popen(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                                       stdout=subprocess.PIPE)
            chrome_version = process.communicate()[0].decode("UTF-8").replace("Google Chrome", "").strip()
        elif self.platform[0] == "win":
            paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\",
                os.environ.get('LOCALAPPDATA') + "\\Google\\Chrome\\Application\\"
            ]
            for path in paths:
                try:
                    with open(path + 'chrome.VisualElementsManifest.xml', 'r') as f:
                        for line in f.readlines():
                            line = line.strip()
                            if line.startswith('Square150x150Logo'):
                                chrome_version = line.split('=')[1].split('\\')[0][1:]
                                break
                except:
                    pass
        if chrome_version is not None:
            chrome_version = [chrome_version] + chrome_version.split('.')  # [full, major, _, minor, micro]
        else:
            raise RuntimeError('WebDriverInstaller: google chrome is not detected installed on your device!')
        return chrome_version

    def get_chromedriver_download_url(self, chrome_major_version=None):
        if chrome_major_version is None:
            chrome_major_version = self.get_chrome_version()[1]
        if int(chrome_major_version) >= 115:  # for new drivers ( [115.0.0000.0, ...] )
            drivers_data = requests.get(
                'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json')
            drivers_data = drivers_data.json()['versions'][::-1]  # start with the latest version
            for driver_data in drivers_data:
                driver_version = driver_data['version']
                driver_major_version = driver_version.split('.')[0]  # major, _, minor, micro
                if driver_major_version == chrome_major_version:  # return latest driver version for current major chrome version
                    for driver_url in driver_data['downloads'].get('chromedriver', None):
                        if driver_url['platform'] in self.platform[1]:
                            return driver_url['url']
        else:  # for old drivers ( [..., 115.0.0000.0) )
            latest_old_driver_version = requests.get(
                'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{0}'.format(chrome_major_version))
            if latest_old_driver_version.status_code != 200:
                raise RuntimeError('WebDriverInstaller: the required chrome driver was not found!')
            latest_old_driver_version = latest_old_driver_version.text
            driver_url = 'https://chromedriver.storage.googleapis.com/{0}/chromedriver_'.format(
                latest_old_driver_version)
            for arch in self.platform[1]:
                current_driver_url = driver_url + arch + '.zip'
                driver_size = requests.head(current_driver_url).headers.get('x-goog-stored-content-length', None)
                if driver_size is not None and int(driver_size) > 1024 ** 2:
                    return current_driver_url
            raise RuntimeError('WebDriverInstaller: the required chrome driver was not found!')

    def download_webdriver(self, path: str, url=None,
                           edge=False):  # Only for Google Chrome (default) and Microsoft Edge (edge=True)
        if url is None:
            if edge:
                url = self.get_edgedriver_download_url()
            else:
                url = self.get_chromedriver_download_url()
        zip_path = path.replace('\\', '/') + '/data.zip'
        f = open(zip_path, 'wb')
        f.write(requests.get(url).content)
        f.close()
        if edge:
            webdriver_name = 'msedgedriver'  # macOS, linux
        else:
            webdriver_name = 'chromedriver'  # macOS, linux
        if self.platform[0].startswith('win'):  # windows
            webdriver_name += '.exe'
        with zipfile.ZipFile(zip_path, 'r') as zip:
            webdriver_zip_path = ''
            if not edge:
                if len(zip.namelist()[0].split('/')) > 1:  # for new Google Chrome webdriver zip format
                    webdriver_zip_path = zip.namelist()[0].split('/')[0] + '/'
            with open(path + '/' + webdriver_name, 'wb') as f:
                f.write(zip.read(webdriver_zip_path + webdriver_name))
        try:
            os.remove(zip_path)
        except:
            pass
        return True

    def get_edge_version(self):  # Only for windows
        cmd = 'powershell -Command "Get-ItemPropertyValue -Path "HKCU:\\SOFTWARE\\Microsoft\\Edge\\BLBeacon" -Name "version""'
        edge_version = None
        try:
            edge_version = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
            edge_version = [edge_version] + edge_version.split('.')  # [full, major, _, minor, micro]
        except:
            raise RuntimeError('WebDriverInstaller: microsoft edge is not detected installed on your device!')
        return edge_version

    def get_edgedriver_download_url(self, edge_version=None):
        archs = self.platform[1]
        if edge_version is None:
            edge_version = self.get_edge_version()
        driver_url = 'https://msedgedriver.azureedge.net/{0}/edgedriver_'.format(edge_version[0])
        for arch in archs:
            current_driver_url = driver_url + arch + '.zip'
            driver_size = requests.head(current_driver_url).headers.get('Content-Length', None)
            if driver_size is not None and int(driver_size) > 1024 ** 2:
                return current_driver_url
        raise RuntimeError('WebDriverInstaller: the required chrome driver was not found!')

    def webdriver_installer_menu(self,
                                 edge=False):  # auto updating or installing google chrome or microsoft edge webdrivers
        if edge:
            browser_name = 'Microsoft Edge'
        else:
            browser_name = 'Google Chrome'
        console_log('-- WebDriver Auto-Installer --\n'.format(browser_name))
        if edge:
            browser_version = self.get_edge_version()
        else:
            browser_version = self.get_chrome_version()
        current_webdriver_version = None
        if edge:
            webdriver_name = 'msedgedriver'
        else:
            webdriver_name = 'chromedriver'
        if self.platform[0] == 'win':
            webdriver_name += '.exe'
        if os.path.exists(webdriver_name):
            os.chmod(webdriver_name, 0o777)
            out = subprocess.check_output([os.path.join(os.getcwd(), webdriver_name), "--version"],
                                          stderr=subprocess.PIPE)
            if out is not None:
                if edge:
                    current_webdriver_version = out.decode("utf-8").split(' ')[3]
                else:
                    current_webdriver_version = out.decode("utf-8").split(' ')[1]
        console_log('{0} version: {1}'.format(browser_name, browser_version[0]), INFO, False)
        console_log('{0} webdriver version: {1}'.format(browser_name, current_webdriver_version), INFO, False)
        webdriver_path = None
        if current_webdriver_version is None:
            console_log('{0} webdriver not detected, download attempt...'.format(browser_name), INFO)
        elif current_webdriver_version.split('.')[0] != browser_version[1]:  # major version match
            console_log('{0} webdriver version doesn\'t match version of the installed {1}, trying to update...'.format(
                browser_name, browser_name), ERROR)
        if current_webdriver_version is None or current_webdriver_version.split('.')[0] != browser_version[1]:
            if edge:
                driver_url = self.get_edgedriver_download_url()
            else:
                driver_url = self.get_chromedriver_download_url()
            if driver_url is not None:
                console_log('\nFound a suitable version for your system!', OK)
                console_log('Downloading...', INFO)
                if self.download_webdriver('.', driver_url, edge):
                    console_log('{0} webdriver was successfully downloaded and unzipped!\n'.format(browser_name), OK)
                    webdriver_path = os.path.join(os.getcwd(), webdriver_name)
                else:
                    console_log('Error downloading or unpacking!\n', ERROR)
        else:
            console_log('The driver has already been updated to the browser version!\n', OK)
            webdriver_path = os.path.join(os.getcwd(), webdriver_name)
        return webdriver_path


def posting_to_game8(web_driver=None, coupon_string=""):
    exec_js = web_driver.execute_script
    url = "https://game8.jp/blue-protocol/535164"
    web_driver.get(url)
    console_log("Loading Game8 BP Coupon Pages", INFO)
    time.sleep(1)
    exec_js(f"{GET_EBID}('js-comment-form-textarea').value = '{coupon_string}'")
    time.sleep(0.5)
    exec_js(f"{GET_EBID}('js-comment-post').click()")
    console_log("Posting Game8 BP Coupon Pages - Done !", INFO)


def posting_to_h1g(web_driver=None, coupon_string=""):
    exec_js = web_driver.execute_script
    url = ("https://h1g.jp/blue-protocol/?%E3%80%90%E6%8A%95%E7%A8%BF%E3%80%91%E3%82%AF%E3%83%BC%E3%83%9D%E3%83"
           "%B3%E6%8A%95%E7%A8%BF%E6%9D%BF")
    web_driver.get(url)
    console_log("Loading H1G BP Coupon Pages", INFO)
    time.sleep(1)
    exec_js(f"{GET_EBID}('comment').value = '{coupon_string}';")
    time.sleep(0.2)
    exec_js(f"{GET_EBCN}('btn-submit','forum-detail-comment__writing')[0].click()")
    console_log("Posting H1G BP Coupon Pages - Done !", INFO)


def posting_to_kamigame(web_driver=None, coupon_string=""):
    exec_js = web_driver.execute_script
    url = "https://kamigame.jp/blue-protocol/page/268092818390530750.html"
    web_driver.get(url)
    console_log("Loading Kamigame BP Coupon Pages", INFO)
    time.sleep(1)
    exec_js(f"{GET_EBCN}('button_comment')[0].firstChild.click();")
    time.sleep(0.5)
    textbox = exec_js(f"return {GET_EBN}('body')[0];")
    textbox.send_keys(coupon_string)
    time.sleep(0.5)
    exec_js(f"{GET_EBCN}('button_comment')[0].firstChild.click();")
    console_log("Posting Kamigame BP Coupon Pages - Done !", INFO)


def posting_to_gamerch(web_driver=None, coupon_string=""):
    exec_js = web_driver.execute_script
    url = "https://gamerch.com/blue-protocol/entry/773081"
    web_driver.get(url)
    console_log("Loading GamerCh BP Coupon Pages", INFO)
    time.sleep(1)
    exec_js(f"{GET_EBCN}('insert-post-area')[0].click();")
    time.sleep(0.5)
    textbox = exec_js(f"return {GET_EBN}('body')[0];")
    textbox.send_keys(coupon_string)
    time.sleep(0.5)
    exec_js(f"{GET_EBCN}('post__contents--submit')[0].firstChild.click();")
    console_log("Posting GamerCh BP Coupon Pages - Done !", INFO)


args_parser = argparse.ArgumentParser()
# Required
## Site target
args_target = args_parser.add_mutually_exclusive_group(required=True)
args_target.add_argument('--game8', action='store_true', help='game8.jp')
args_target.add_argument('--h1g', action='store_true', help='h1g.jp')
args_target.add_argument('--kamigame', action='store_true', help='kamigame.jp')
args_target.add_argument('--gamerch', action='store_true', help='gamerch.com')
## Browsers
args_browsers = args_parser.add_mutually_exclusive_group(required=True)
args_browsers.add_argument('--chrome', action='store_true', help='Launching the project via Google Chrome browser')
args_browsers.add_argument('--firefox', action='store_true', help='Launching the project via Mozilla Firefox browser')
args_browsers.add_argument('--edge', action='store_true', help='Launching the project via Microsoft Edge browser')
## Modes of operation
# args_parser.add_argument('--coupon', type=str, default='', help='BP Coupon', required=True)
## Optional
args_parser.add_argument('--custom-browser-location', type=str, default='',
                         help='Set path to the custom browser (to the binary file, useful when using non-standard '
                              'releases, for example, Firefox Developer Edition)')

driver = None

try:

    try:
        args = vars(args_parser.parse_args())
    except:
        time.sleep(3)
        exit(0)

    # initialization and configuration of everything necessary for work
    webdriver_installer = WebDriverInstaller()

    browser_name = 'chrome'
    browser_path = ''
    if args['firefox']:
        browser_name = 'firefox'
    elif args['edge']:
        browser_name = 'edge'
    else:
        console_log("Wut browser ?", ERROR)
        exit(0)

    if args['custom_browser_location']:
        browser_path = args['custom_browser_location']

    driver = SharedTools.initSeleniumWebDriver(browser_name=browser_name, browser_path=browser_path)
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    if not os.path.isfile(config_path):
        console_log("Config file not found", ERROR)
        exit(0)

    file = open(config_path, encoding="utf-8", mode="r")
    json_data = json.load(file)
    coupon = json_data['coupon']
    template = json_data['template']

    full_body = template.format(coupon=coupon)

    # Posting to Game8.jp
    if args['game8']:
        posting_to_game8(web_driver=driver, coupon_string=full_body)
    # Posting to h1g.jp
    if args['h1g']:
        posting_to_h1g(web_driver=driver, coupon_string=full_body)
    # Posting to kamigame.jp
    if args['kamigame']:
        posting_to_kamigame(web_driver=driver, coupon_string=full_body)
    # Posting to gamerch.com
    if args['gamerch']:
        posting_to_gamerch(web_driver=driver, coupon_string=full_body)
    # end
    driver.quit()

except Exception as E:
    traceback_string = traceback.format_exc()
    if str(type(E)).find('selenium') and traceback_string.find('Stacktrace:') != -1:  # disabling stacktrace output
        traceback_string = traceback_string.split('Stacktrace:', 1)[0]
    console_log(traceback_string, ERROR)
    exit(0)
    # time.sleep(3)  # exit-delay
finally:
    if driver:
        driver.quit()
