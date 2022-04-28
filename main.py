from time import sleep
# selenium 4.1.3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

''' 
seems out of date
# to be modified by calling system commands
binary_location = "/usr/bin/google-chrome"
driver_location = "/usr/bin/chromedriver"
'''
homeURL = "https://jcr.clarivate.com/jcr/home?app=jcr&referrer=target%3Dhttps:%2F%2Fjcr.clarivate.com%2Fjcr%2Fhome&Init=Yes&authCode=null&SrcApp=IC2LS"
driver = None

WAIT_ELEMENT = 30
SEARCH_BAR_ID = "search-bar"
COOKIE_BUTTON_ID = "onetrust-accept-btn-handler"
RESULT_CLASSNAME = "pop-content.journal-title"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def init_driver():
    global driver
    # create an instance of Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # to-do: should be headless
''' 
    seems out of date
    # create an instance of chrome options and the Chrome
    options = webdriver.ChromeOptions()
    options.binary_location = binary_location
    driver = webdriver.Chrome(executable_path=driver_location, options=options)
'''


i=0
def open_journal_page(issn):
    global driver
    global i
    i = i+1
    driver.get(homeURL)
    WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.ID, SEARCH_BAR_ID))).send_keys(issn)
    # not good. to be figure out later
    if i == 1:
        WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.ID, COOKIE_BUTTON_ID))).click()
    # click the journal page in the drop-down
    WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.CLASS_NAME, RESULT_CLASSNAME))).click()
    sleep(3)


def get_quartiles(issn):
    if driver is None:
        init_driver()
    open_journal_page(issn)


def main():
    for issn in ['0005-1098', '0001-0782', '0018-9340', '1558-7916', '0278-0070']:
        # original issn: ['0005-1098', '0001-0782', '00189340', '1558-7916', '0278 0070'],
        # to-do: format as 4 digits + hyphen + 4 digits?
        open_journal_page(issn)
    # better to use atexit
    driver.quit()


if __name__ == '__main__':
    main()