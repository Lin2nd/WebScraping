from time import sleep
# selenium 4.1.3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse, parse_qs
import json


homeURL = "https://jcr.clarivate.com/jcr/home?app=jcr&referrer=target%3Dhttps:%2F%2Fjcr.clarivate.com%2Fjcr%2Fhome&Init=Yes&authCode=null&SrcApp=IC2LS"
driver = None

WAIT_ELEMENT = 30
SEARCH_BAR_ID = "search-bar"
COOKIE_BUTTON_ID = "onetrust-accept-btn-handler"
RESULT_CLASSNAME = "pop-content.journal-title"


def init_driver():
    global driver
    options = Options()
    # options.headless = True
    # create an instance of Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def extract_cookie():
    cookies = driver.get_cookies()
    for cookie in cookies:
        if cookie["name"] == "PSSID" and cookie["value"][0] != '"':  # the cookie is duplicate
            return cookie["value"]


def extract_jcr_abbreviation(url):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    return str(query['journal'][0])


def get_request_json():
    # just to show the structure
    request_json = {'headers': {'content-type': 'application/json', 'x-1p-inc-sid': ''},
                    'body': '',
                    'method': 'POST'}
    request_json['headers']['x-1p-inc-sid'] = extract_cookie()
    body = {'journal': extract_jcr_abbreviation(driver.current_url)}
    request_json['body'] = json.dumps(body)

    return request_json


def get_response_test():
    targe_url = '"https://jcr.clarivate.com/api/jcr3/journalprofile/v1/rank-byjif"'
    driver.switch_to.window(driver.window_handles[1])
    script = '''return await fetch(''' + targe_url + ''', ''' + json.dumps(get_request_json()) + ''')''' + '''.then(response => {return response.json();})'''
    print(script)
    response = driver.execute_script(script)
    print(response['data'][0]['category'])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def open_journal_page(issn):
    print(driver.current_url)
    search_bar = WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.ID, SEARCH_BAR_ID)))
    search_bar.send_keys(issn)
    # click the journal page in the drop-down
    WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.CLASS_NAME, RESULT_CLASSNAME))).click()
    # Wanted to be more efficient. Avoid loading the homepage multiple times
    # Have to do it this way. It seems Element.clear() doesn't work on react elements. Saw bug report
    action = webdriver.ActionChains(driver)
    # Clean the search bar
    action.move_to_element(search_bar).click().key_down(Keys.CONTROL).send_keys("a").perform()
    search_bar.send_keys(Keys.DELETE)
    # sleep(3)
    get_response_test()


def get_quartiles(issn):
    if driver is None:
        init_driver()
    open_journal_page(issn)


def get_homepage():
    if driver is None:
        init_driver()

    '''The driver.maximize_window() line is useful. To avoid problems caused by dynamic load
    Although the "accept cookies" button is identified by class name, It seems it is actually located by the coordinates
    W/o this line, *SOMETIMES* the "Message: element click intercepted: Element is not clickable at point (631, 758)" exception arises
    Maximize the window may tackle the problem. If it does not work, the exception will be caught and dealt with by driver.execute_script('document.querySelector("#onetrust-accept-btn-handler").click()')
    '''
    # driver.maximize_window()
    driver.get(homeURL)
    try:
        WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.ID, COOKIE_BUTTON_ID))).click()
    except ElementClickInterceptedException:
        driver.execute_script('document.querySelector("#onetrust-accept-btn-handler").click()')
        print('here')



def main():
    get_homepage()
    for issn in ['0005-1098', '0001-0782', '0018-9340', '1558-7916', '0278-0070']:
        # original issn: ['0005-1098', '0001-0782', '00189340', '1558-7916', '0278 0070'],
        # to-do: format as 4 digits + hyphen + 4 digits?
        print(issn)
        get_quartiles(issn)
    # better to use atexit
    driver.quit()


if __name__ == '__main__':
    main()
