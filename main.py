import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime
from dateutil import parser

from colorama import init

import kuri_tools
import tools

init()


def posting_to_game8(web_driver, coupon_string):
    web_driver.go_to_url(coupon_site_link["game8"])
    kuri_tools.log_info("Loading Game8 BP Coupon Pages")
    time.sleep(1)
    web_driver.execute_script_by_id(f"('js-comment-form-textarea').value = '{coupon_string}'")
    time.sleep(0.5)
    web_driver.execute_script_by_id("('js-comment-post').click()")
    kuri_tools.log_ok("Posting Game8 BP Coupon Pages - Done !")


def posting_to_h1g(web_driver, coupon_string):
    web_driver.go_to_url(coupon_site_link["h1g"])
    kuri_tools.log_info("Loading H1G BP Coupon Pages")
    time.sleep(1)
    web_driver.execute_script_by_id(f"('comment').value = '{coupon_string}';")
    time.sleep(0.2)
    web_driver.execute_script_by_class_name("('btn-submit','forum-detail-comment__writing')[0].click()")
    kuri_tools.log_ok("Posting H1G BP Coupon Pages - Done !")


def posting_to_kamigame(web_driver, coupon_string):
    web_driver.go_to_url(coupon_site_link["kamigame"])
    kuri_tools.log_info("Loading Kamigame BP Coupon Pages")
    time.sleep(1)
    kuri_tools.log_warning("DELETING Google Ads IFrame")
    web_driver.execute_script_raw("document.querySelectorAll('iframe').forEach(item => item.remove());")
    web_driver.execute_script_raw("document.querySelectorAll('.ad').forEach(item => item.remove());")
    web_driver.execute_script_raw("document.getElementById('overlay_ad_pc').remove();")
    time.sleep(1)
    web_driver.execute_script_by_class_name("('button_comment')[0].firstChild.click();")
    time.sleep(0.5)
    # This site need to simulate send key, can't using JS.value. Maybe bot prevention ?
    textbox = web_driver.execute_script_by_name("('body')[0];")
    textbox.clear()
    textbox.click()
    textbox.send_keys(coupon_string)
    time.sleep(0.5)
    web_driver.execute_script_by_class_name("('button_comment')[0].firstChild.click();")
    kuri_tools.log_ok("Posting Kamigame BP Coupon Pages - Done !")


def posting_to_gamerch(web_driver, coupon_string):
    web_driver.go_to_url(coupon_site_link["gamerch"])
    kuri_tools.log_info("Loading GamerCh BP Coupon Pages")
    time.sleep(1)
    web_driver.execute_script_by_class_name("('insert-post-area')[0].click();")
    time.sleep(0.5)
    textbox = web_driver.execute_script_by_name("('body')[0];")
    textbox.send_keys(coupon_string)
    time.sleep(0.5)
    web_driver.execute_script_by_class_name("('post__contents--submit')[0].firstChild.click();")
    kuri_tools.log_ok("Posting GamerCh BP Coupon Pages - Done !")


def replace_template(json_object=None):
    template_string = json_object['template']

    for key, value in json_object.items():
        if key == "expired":
            template_string = template_string.format(key=datetime.strptime(value, "%Y-%m-%d %H:%M"))
        else:
            template_string = template_string.format(key=value)

    return template_string


args_parser = argparse.ArgumentParser()
# Required
# Site target
args_target = args_parser.add_mutually_exclusive_group(required=True)
args_target.add_argument('--game8', action='store_true', help='game8.jp')
args_target.add_argument('--h1g', action='store_true', help='h1g.jp')
args_target.add_argument('--kamigame', action='store_true', help='kamigame.jp')
args_target.add_argument('--gamerch', action='store_true', help='gamerch.com')
# Browsers
args_browsers = args_parser.add_mutually_exclusive_group(required=True)
args_browsers.add_argument('--chrome', action='store_true', help='Launching the project via Google Chrome browser')
args_browsers.add_argument('--firefox', action='store_true', help='Launching the project via Mozilla Firefox browser')
args_browsers.add_argument('--edge', action='store_true', help='Launching the project via Microsoft Edge browser')
# Modes of operation
# args_parser.add_argument('--coupon', type=str, default='', help='BP Coupon', required=True)
# Optional
args_parser.add_argument('--custom-browser-location', type=str, default='',
                         help='Set path to the custom browser (to the binary file, useful when using non-standard '
                              'releases, for example, Firefox Developer Edition)')

driver = None
coupon_site_link = {
    "game8": "https://game8.jp/blue-protocol/535164",
    "h1g": "https://h1g.jp/blue-protocol/?%E3%80%90%E6%8A%95%E7%A8%BF%E3%80%91%E3%82%AF%E3%83%BC%E3%83%9D%E3%83"
           "%B3%E6%8A%95%E7%A8%BF%E6%9D%BF",
    "kamigame": "https://kamigame.jp/blue-protocol/page/268092818390530750.html",
    "gamerch": "https://gamerch.com/blue-protocol/entry/773081",
}

try:
    try:
        args = vars(args_parser.parse_args())
    except:
        time.sleep(3)
        exit(0)

    kuri_tools.log_info(f"Script runtime at {datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}, with "
                        f"parameter {', '.join(sys.argv[1:])}")

    # initialization and configuration of everything necessary for work
    webdriver_installer = tools.WebDriverInstaller()

    browser_name = 'chrome'
    browser_path = ''
    if args['firefox']:
        browser_name = 'firefox'
    elif args['edge']:
        browser_name = 'edge'
    else:
        kuri_tools.log_error("Wut browser ?")
        exit(0)

    if args['custom_browser_location']:
        browser_path = args['custom_browser_location']

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    if not os.path.isfile(config_path):
        kuri_tools.log_error("Config file not found")
        exit(0)

    file = open(config_path, encoding="utf-8", mode="r")
    json_data = json.load(file)

    # Check config, coupon, expired, and template are a must in config.json
    if (json_data is None or json_data['template'] is None or json_data['coupon'] is None
            or json_data['expired'] is None):
        kuri_tools.log_error("Config error !")
        exit(0)

    expired = parser.parse(json_data['expired'])
    now = datetime.now()

    # Check Expire
    if now > expired:
        kuri_tools.log_info("Coupon Expired")
        exit(0)

    full_body = json_data['template'].format(**json_data)
    driver = kuri_tools.WebDriver(browser_name=browser_name, browser_path=browser_path)

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
    kuri_tools.log_error(traceback_string)
    exit(0)
    # time.sleep(3)  # exit-delay
finally:
    if driver:
        driver.quit()
