# selenium 4.1.3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse, parse_qs
import time
import json


homeURL = "https://jcr.clarivate.com/jcr/home"
response_json_targe_url = '"https://jcr.clarivate.com/api/jcr3/journalprofile/v1/rank-byjif"'
driver = None
action = None

WAIT_ELEMENT = 30
SEARCH_BAR_ID = "search-bar"
COOKIE_BUTTON_ID = "onetrust-accept-btn-handler"
RESULT_CLASSNAME = "pop-content.journal-title"


def extract_cookie():
    cookies = driver.get_cookies()
    for cookie in cookies:
        if cookie["name"] == "PSSID" and cookie["value"][0] != '"':  # the cookie is duplicate
            return cookie["value"]


def extract_jcr_abbreviation(url):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    assert 'journal' in query, f'The current url is {url}, please check if the jcr abbreviation is included in the url'

    return str(query['journal'][0])


def get_request_json():
    request_json = {'headers': {'content-type': 'application/json', 'x-1p-inc-sid': ''},
                    'body': '',
                    'method': 'POST'}
    request_json['headers']['x-1p-inc-sid'] = extract_cookie()
    body = {'journal': extract_jcr_abbreviation(driver.current_url)}
    request_json['body'] = json.dumps(body)

    return request_json


def get_response_json():
    # Move control to the newly opened journal page
    driver.switch_to.window(driver.window_handles[1])
    script = '''return await fetch(''' + response_json_targe_url + ''', ''' + json.dumps(get_request_json()) + ''')''' + '''.then(response => {return response.json();})'''
    print(script)
    response = driver.execute_script(script)
    driver.close()
    # Move control back to the home page
    driver.switch_to.window(driver.window_handles[0])

    return response


def get_quartiles():
    result = []
    response = get_response_json()
    for data in response['data']:
        rank_by_category = {'category': data['category'], 'quartiles': {}}
        for Jifrank in data['rankByJif']:
            year = Jifrank['year']
            quartile = Jifrank['quartile']
            if quartile != 'n/a':
                rank_by_category['quartiles'][year] = quartile
        result.append(rank_by_category)

    return result


def crawl_page(issn):
    print(driver.current_url)
    search_bar = WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.ID, SEARCH_BAR_ID)))
    search_bar.send_keys(issn)
    # click the link to the journal page in the drop-down
    WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.CLASS_NAME, RESULT_CLASSNAME))).click()

    # Wanted to be more efficient. Avoid loading the homepage multiple times
    # Have to do it this way. It seems Element.clear() doesn't work on react elements. There is a bug report
    # Clean the search bar
    action.move_to_element(search_bar).click().key_down(Keys.CONTROL).send_keys("a").perform()
    search_bar.send_keys(Keys.DELETE)
    # time.sleep(3)
    return get_quartiles()


def get_homepage():
    # The driver.maximize_window() line may be useful. To avoid problems caused by dynamic load
    # Although the "accept cookies" button is identified by ID, It seems somehow it is actually located by the coordinates
    # W/o this line, *SOMETIMES* the "Message: element click intercepted: Element is not clickable at point (631, 758)"/Message: element not interactable exception arises
    # Maximize the window may tackle the problem. If it does not work, the exception will be caught and dealt with by driver.execute_script('document.querySelector("#onetrust-accept-btn-handler").click()')
    driver.maximize_window()
    driver.get(homeURL)
    try:
        # The argument of presence_of_element_located() is a tuple
        WebDriverWait(driver, WAIT_ELEMENT).until(EC.presence_of_element_located((By.ID, COOKIE_BUTTON_ID))).click()
    except (ElementClickInterceptedException, ElementNotInteractableException) as e:
        driver.execute_script('''document.querySelector("#''' + COOKIE_BUTTON_ID + '''").click()''')
        print('here')
        print(e)


def format_issn(issn):
    # Convert 'xxxxxxxx' to 'xxxx-xxxx'
    if len(issn) == 8:
        issn = issn[:4] + '-' + issn[4:]
    # Convert 'xxxx xxxx' to 'xxxx-xxxx'
    if len(issn) == 9:
        if issn[4] != '-':
            issn = issn[:4] + '-' + issn[5:]
    assert len(issn) == 9, f'One of the issn is {issn}, please check if it is valid'

    return issn


def init_all():
    global driver
    global action
    options = Options()
    options.headless = True
    # create an instance of Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # For clearing the search bar. Used in crawl_page(). Put it here so it can be initialized only once
    action = webdriver.ActionChains(driver)


def main():
    init_all()
    get_homepage()
    # {'specific_issn': [{'category': category,
    #                    'quartiles': {'specific_year': quartile, ...}}, ...]
    #  ,...
    #  }"
    res = {}
    for issn in ['0005-1098', '0001-0782', '00189340', '1558-7916', '0278 0070']:
        formatted_issn = format_issn(issn)
        res[formatted_issn] = crawl_page(formatted_issn)
    driver.quit()

    for issn, ranks in res.items():
        print('issn: ' + issn)
        for category in ranks:
            print('category: ' + category['category'])
            for year, quartile in category['quartiles'].items():
                print(year + ': ' + quartile)
        print("---------------------------------------------------------------")


if __name__ == '__main__':
    main()
