import urllib
import http.cookiejar
import requests
from selenium import webdriver
from time import sleep


URL = "https://jcr.clarivate.com/jcr/home"

# Not working. Empty list.
def extract_cookies1():
    cookie_jar = http.cookiejar.CookieJar()
    url_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    url_opener.open(URL)
    print(url_opener)
    print(cookie_jar)
    for cookie in cookie_jar:
        print(cookie.name, ": ", cookie.value)

# Not working. Empty list
def extract_cookies2():
    response = requests.get(URL)
    print(response)
    print(response.cookies)
    for cookie in response.cookies:
        print(cookie.name, ": ", cookie.value)

# Working
def extract_cookies3():
    driver = webdriver.Chrome()
    driver.get(URL)
    sleep(3)
    cookies = driver.get_cookies()
    for cookie in cookies:
        if cookie["name"] == "PSSID":
            print(cookie["value"])

# Weird but working
def extract_cookies4():
    driver = webdriver.Chrome()
    driver.get(URL)
    sleep(3)
    cookie = driver.execute_script("return document.cookie.match(\"PSSID=(.*?);\")")
    print(cookie[1])


if __name__ == "__main__":
    print("Result from extract_cookies3")
    extract_cookies3()
    print("Result from extract_cookies4")
    extract_cookies4()
