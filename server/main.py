import os
import re
import sys
import math
import time
import json
import getopt
import platform
import datetime
import requests
import selenium
import threading
import pandas as pd
from konlpy.tag import Hannanum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Back, Style

hannanum = Hannanum()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
DATA = { 'count': 0, 'data': [ ], 'keyword': { } }

def main(argv):
  init_time = time.time()
  # Parsing options
  KEYWORD = None # single keyword or keyword array
  MULTIPLE = False # Multiple keyword input switch
  SCAN_NUMBER = None # Maxminum article scan counts
  OUTPUT = None # output file location
  DRIVER = None # selenium chromedriver location
  
  try:
    opts, etc_args = getopt.getopt(argv[1:], "k:mn:o:d:", ["keyword=", "multiple", "number=", "output=", "driver="])
  except getopt.GetoptError as e:
    print(Fore.RED + 'fail\n' + str(e))
    print(Fore.RESET)
    sys.exit(1)
    
  for opt, arg in opts:
    if opt in ("-k", "--keyword"):
      KEYWORD = arg
    
    elif opt in ("-m", "--multiple"): # multiple keywords scan
      MULTIPLE = True
    
    elif opt in ("-n", "--number"):
      try:
        SCAN_NUMBER = int(arg)
      except ValueError as e:
        print(Fore.RED + '-n or --number option parameter must be integer number')
        print(Fore.RESET)
        sys.exit(1)

    elif opt in ("-o", "--output"):
      OUTPUT = arg
      
    elif opt in ("-d", "--driver"):
      DRIVER = arg

  if len(KEYWORD) < 1:
    print(Fore.RED + '-k or --keyword option is mandatory')
    print(Fore.RESET)
    sys.exit(1)
    
  if MULTIPLE:
    KEYWORD = KEYWORD.split(',')
  
  
  # Loading Selenium driver
  print(Fore.RESET + 'Loading Selenium driver... ', end='')
  sys.stdout.flush()
  try:
    # Identifying OS
    OS = platform.system()
    if OS == 'Linux': chromedriver = 'chromedriver'
    elif OS == 'Darwin': chromedriver = 'chromedriver'
    elif OS == 'Windows': chromedriver = 'chromedriver.exe'
    else: chromedriver = None
      
    driver = webdriver.Chrome(executable_path=DRIVER if DRIVER else chromedriver, options=chrome_options)
  except selenium.common.exceptions.WebDriverException as e:
    print(Fore.RED + 'fail\n' + str(e))
    print(Fore.RESET)
    sys.exit(1)
  print(Fore.GREEN + 'OK')
  sys.stdout.flush()
  
  '''
  # Initializing output file
  with open(OUTPUT if OUTPUT else 'output.json', "w") as f:
    f.write(json.dumps(DATA, ensure_ascii = False))
  '''
  
  # Starting keywords scan
  if isinstance(KEYWORD, str): # if KEYWORD is a single string
    keyword_scan(KEYWORD, SCAN_NUMBER, OUTPUT, driver)
  else: # if KEYWORD is a keyword array
    for keyword in KEYWORD:
      keyword_scan(keyword, SCAN_NUMBER, OUTPUT, driver)
  
  
  # Keyword scan complete. Starting article scan
  print(Fore.GREEN + 'Keyword scan complete. Collected: ' + str(DATA['count']) + '\n')
  print(Fore.RESET + 'Scanning collected articles... #0 / ' + str(DATA['count']), end='')
  article_scan_count = 0
  
  # For each articles
  for article in DATA['data']:
    article['keyword'] = [ ]
    # Loading target article

    try:
      driver.get('https://brunch.co.kr/@' + str(article['profileId']) + '/' + str(article['no']))
      WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.cover_title')))
    except selenium.common.exceptions.TimeoutException as e:
      #print(Fore.RED + '\nFAIL:', e)
      #print(Fore.RESET)
      continue # skip failed request
    
    # Do some analysis on article
    articleText = ''
    contents = driver.find_element(By.CSS_SELECTOR, 'div.wrap_body').find_elements(By.TAG_NAME, 'p')
    for content in contents: articleText += content.get_attribute('innerText')
    articleText = re.sub('[0-9]+', '', articleText) # Removing numbers
    articleText = re.sub(u'\xa0', u' ', articleText) # Removing \xa0, which is &nbsp;
    articleText = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ·!』\\‘’|\(\)\[\]\<\>`\'…》]', '', articleText) # Removing special characters
    article['word'] = pd.Series(hannanum.nouns(articleText)).value_counts().to_dict() # 형태소 추출 및 출현 빈도수 합산

    # Analysis on keywords list
    keywords = driver.find_element(By.CSS_SELECTOR, 'ul.list_keyword').find_elements(By.TAG_NAME, 'li')
    for keyword in keywords:
      target = keyword.find_element(By.TAG_NAME, 'a').get_attribute('innerText')
      
      # Update each data's keyword list
      article['keyword'].append(target)

      # Update DATA['keyword']
      if target in DATA['keyword']:
        DATA['keyword'][target]['count'] = DATA['keyword'][target]['count'] + 1
        DATA['keyword'][target]['share'] = DATA['keyword'][target]['share'] + article['socialShareTotalCount']
      else: DATA['keyword'][target] = { "count": 1, "share": article['socialShareTotalCount'] }
    '''
    # Writing into file after each article scan is finished.
    with open(OUTPUT if OUTPUT else 'output.json', "w") as f:
      f.write(json.dumps(DATA, ensure_ascii = False))
    '''

    # Updating counter
    article_scan_count = article_scan_count + 1
    for i in range(len(str(article_scan_count - 1)) + 3 + len(str(DATA['count']))): print('\b', end='')
    print(str(article_scan_count) + ' / ' + str(DATA['count']), end='')
    sys.stdout.flush()


  # Writing into file
  print(Fore.RESET + '\nPerforming final data writing... ', end='')
  filename = str(math.floor(time.time())) + ',' + ('$'.join(KEYWORD) if MULTIPLE else KEYWORD) + '.json'
  
  try:
    with open(OUTPUT if OUTPUT else filename, "w", -1, 'utf-8') as f:
      f.write(json.dumps(DATA, ensure_ascii = False))
      print(Fore.GREEN + 'OK')
      sys.stdout.flush()
  except FileNotFoundError: # If there is no route to output folder
    os.makedirs(os.path.dirname(OUTPUT) if OUTPUT else '')
    with open(OUTPUT if OUTPUT else filename, "w", -1, 'utf-8') as f:
      f.write(json.dumps(DATA, ensure_ascii = False))
      print(Fore.GREEN + 'OK')
      sys.stdout.flush()
    
  driver.quit()
  terminate_time = time.time()
  spent_time = terminate_time - init_time
  #spent_time = str(datetime.timedelta(seconds=(terminate_time - init_time)))
  print(Fore.GREEN + 'Scan finished. ' + str(round(spent_time, 1)) + 's spent.')
  print(Fore.RESET + 'OUTPUT: ' + filename)
  print(Fore.RESET)
  sys.stdout.flush()
  
  

def keyword_scan(KEYWORD, SCAN_NUMBER, OUTPUT, driver):
  keyword_scan_count = 0
  print(Fore.RESET + '\nScanning keyword: ' + KEYWORD)
  sys.stdout.flush()

  # Loading keyword page
  url = 'https://brunch.co.kr/keyword/' + KEYWORD
  print(Fore.RESET + '  Loading page: ' + url + '... ', end='')
  sys.stdout.flush()
  try:
    driver.get(url)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.list_article.list_common')))
  except selenium.common.exceptions.TimeoutException as e: 
    print(Fore.RED + 'fail\n' + str(e))
    print(Fore.RESET)
    sys.exit(1)
  print(Fore.GREEN + 'OK')
  sys.stdout.flush()

  # Looking for <script> tag with B.Keyword.init()
  print(Fore.RESET + '  Locating initialization script... ', end='')
  sys.stdout.flush()
  script_flag = False
  for script_content in driver.find_element(By.TAG_NAME, 'body').find_elements(By.TAG_NAME, 'script'):
    script = script_content.get_attribute('innerHTML').strip()
    if script[:14] == 'B.Keyword.init':
      script_flag = script

  if script_flag:
    print(Fore.GREEN + 'OK')
    print(Fore.RESET + '  Parsing initialization script... ', end='')
    sys.stdout.flush()

    try:
      object = script_flag[15:-17]
      timestamp = script_flag[-15:-2]
      object = object.replace('moreList', '"moreList"', 1).replace('keywordType', '"keywordType"', 1).replace("'single'", '"single"', 1).replace('articleList', '"articleList"', 1)
      object = json.loads(object)
      print(Fore.GREEN + 'OK')
      sys.stdout.flush()

    except:
      print(Fore.RED + 'fail')
      print(sys.exc_info()[0])
      print(Fore.RESET)
      sys.exit(1)

    # Scan list of articles until maximum scan number met
    print(Fore.RESET + '  Parsing JSON object... #', end='')
    print(keyword_scan_count, end='')
    sys.stdout.flush()

    # scan first B.Keyword.init lists
    for article in object['articleList']:
      DATA['data'].append({
        'likeCount': article['article']['likeCount'],
        'title': article['article']['title'],
        'readSeconds': article['article']['readSeconds'],
        'userId': article['article']['userId'],
        'profileId': article['article']['profileId'],
        'no': article['article']['no'],
        'socialShareTotalCount': article['article']['socialShareTotalCount'],
        'url': 'https://brunch.co.kr/@' + str(article['article']['profileId']) + '/' + str(article['article']['no']),
        'authorComment': article['article']['authorComment'],
        'contentSummary': article['article']['contentSummary'],
        'subTitle': article['article']['subTitle'],
        'userName': article['profile']['userName'],
        'articleCount': article['profile']['articleCount'],
        'followerCount': article['profile']['followerCount'],
        'description': article['profile']['description']
      })
      DATA['count'] = DATA['count'] + 1
      keyword_scan_count = keyword_scan_count + 1
      for i in range(len(str(keyword_scan_count - 1))): print('\b', end='')
      print(keyword_scan_count, end='')
      sys.stdout.flush()

    while True: # lazyloading contents
      timestamp, keyword_scan_count = scan(KEYWORD, SCAN_NUMBER, timestamp, keyword_scan_count)
      if not timestamp: break
    print()

  else: # Parsing initialization script failed
    print(Fore.RED + 'fail')
    print('Keyword scan failed. KEYWORD: ' + KEYWORD)
    sys.stdout.flush()
    return

  
def scan(KEYWORD, SCAN_NUMBER, timestamp, keyword_scan_count):
  URL = 'https://api.brunch.co.kr/v1/top/keyword/' + KEYWORD
  params = { 'publishTime': timestamp }
  headers = { 'Sec-Fetch-Mode': 'cors', 'Accept': 'application/json, text/javascript, */*; q=0.01' }
  response = requests.get(URL, params=params, headers=headers)
  response = response.json()

  for article in response['data']['articleList']:
    DATA['data'].append({
      'likeCount': article['article']['likeCount'],
      'title': article['article']['title'],
      'readSeconds': article['article']['readSeconds'],
      'userId': article['article']['userId'],
      'profileId': article['article']['profileId'],
      'no': article['article']['no'],
      'socialShareTotalCount': article['article']['socialShareTotalCount'],
      'url': 'https://brunch.co.kr/@' + str(article['article']['profileId']) + '/' + str(article['article']['no']),
      'authorComment': article['article']['authorComment'],
      'contentSummary': article['article']['contentSummary'],
      'subTitle': article['article']['subTitle'],
      'userName': article['profile']['userName'],
      'articleCount': article['profile']['articleCount'],
      'followerCount': article['profile']['followerCount'],
      'description': article['profile']['description']
    })
    timestamp = article['timestamp']
    DATA['count'] = DATA['count'] + 1
    keyword_scan_count = keyword_scan_count + 1
    for i in range(len(str(keyword_scan_count - 1))): print('\b', end='')
    print(keyword_scan_count, end='')
    sys.stdout.flush()

    if SCAN_NUMBER:
      if keyword_scan_count >= SCAN_NUMBER:
        return False, keyword_scan_count # Break when SCAN_NUMBER met

  if not response['data']['moreList']: return False, keyword_scan_count # Break when moreList is False
  return timestamp, keyword_scan_count # continue scanning, passing last timestamp parameter

if __name__ == "__main__":
  main(sys.argv)
