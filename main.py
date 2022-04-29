from time import sleep
# selenium 4.1.3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs
import json

''' 
seems out of date
# to be modified by calling system commands
binary_location = "/usr/bin/google-chrome"
driver_location = "/usr/bin/chromedriver"
'''
homeURL = "https://jcr.clarivate.com/jcr/home?app=jcr&referrer=target%3Dhttps:%2F%2Fjcr.clarivate.com%2Fjcr%2Fhome&Init=Yes&authCode=null&SrcApp=IC2LS"
driver = None

WAIT_ELEMENT = 100
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


def extract_cookie():
    cookies = driver.get_cookies()
    for cookie in cookies:
        if cookie["name"] == "PSSID" and cookie["value"][0] != '"':
            return cookie["value"]


def extract_jcr_abbreviation(url):
    print(url)
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    print(query)
    return str(query['journal'][0])


def get_request_json():
    # just to show the structure
    request_json = {'headers': {'content-type': 'application/json', 'x-1p-inc-sid': ''},
                    'body': '',
                    'method': 'POST'}
    request_json['headers']['x-1p-inc-sid'] = extract_cookie()
    body = {'journal': extract_jcr_abbreviation(driver.current_url)}
    request_json['body'] = json.dumps(body)
    print(json.dumps(request_json))

    return request_json


def get_response_test():
    targe_url = '"https://jcr.clarivate.com/api/jcr3/journalprofile/v1/rank-byjif"'
    # script = '''return document.location'''
    driver.switch_to.window(driver.window_handles[1])
    script = '''return await fetch(''' + targe_url + ''', ''' + json.dumps(get_request_json()) + ''')''' + '''.then(response => {return response.json();})'''
    print(script)
    # script = '''return document.location.toString()'''
    response = driver.execute_script(script)
    print(response['data'][0]['category'])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

i=0
def open_journal_page(issn):
    global driver
    global i
    i = i+1
    # This is useful. To avoid problems caused by dynamic load
    # If not working, close and run again
    # To be fixed
    # This is so wired. Why the "Accept cookies" botton element is indeed located by coordinates? It worked well before and the problem arises today
    driver.maximize_window()
    driver.get(homeURL)
    WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.ID, SEARCH_BAR_ID))).send_keys(issn)

    # not good. to be figure out later
    if i == 1:
        WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.ID, COOKIE_BUTTON_ID))).click()

    # click the journal page in the drop-down
    WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.CLASS_NAME, RESULT_CLASSNAME))).click()
    # sleep(3)
    get_response_test()



def get_quartiles(issn):
    if driver is None:
        init_driver()
    open_journal_page(issn)


def main():
    for issn in ['0005-1098', '0001-0782', '0018-9340', '1558-7916', '0278-0070']:
        # original issn: ['0005-1098', '0001-0782', '00189340', '1558-7916', '0278 0070'],
        # to-do: format as 4 digits + hyphen + 4 digits?
        print(issn)
        open_journal_page(issn)
    # better to use atexit
    driver.quit()


if __name__ == '__main__':
    main()
