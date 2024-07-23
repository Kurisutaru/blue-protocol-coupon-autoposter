import tools


def log_ok(text=""):
    tools.console_log(text, tools.OK)


def log_info(text=""):
    tools.console_log(text, tools.INFO)


def log_warning(text=""):
    tools.console_log(text, tools.WARN)


def log_error(text=""):
    tools.console_log(text, tools.ERROR)


def log_devinfo(text=""):
    tools.console_log(text, tools.DEVINFO)


class WebDriver(object):

    def __init__(self, browser_name=None, browser_path=None):
        log_info("Initializing WebDriver...")
        if browser_name is not None:
            self.driver = tools.SharedTools.initSeleniumWebDriver(browser_name=browser_name,
                                                                  browser_path=browser_path)
            self.driver_js = self.driver.execute_script

    def go_to_url(self, url):
        self.driver.get(url)

    def execute_script_by_id(self, script):
        return self.driver_js(f"return {tools.GET_EBID}{script}")

    def execute_script_by_name(self, script):
        return self.driver_js(f"return {tools.GET_EBN}{script}")

    def execute_script_by_class_name(self, script):
        return self.driver_js(f"return {tools.GET_EBCN}{script}")

    def execute_script_by_tag_name(self, script):
        return self.driver_js(f"return {tools.GET_EBTN}{script}")

    def execute_script_raw(self, script):
        return self.driver_js(f"return {script}")

    def quit(self):
        if self.driver:
            self.driver.quit()
