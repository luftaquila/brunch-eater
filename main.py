import os
import re
import sys
import time
import json
import getopt
import datetime
import selenium
import threading
import configparser
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib import request, parse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Back, Style

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def main(argv):
  # Parsing options
  KEYWORD = None # single keyword or keyword array
  MULTIPLE = False # Multiple keyword input switch
  SCAN_NUMBER = None # Maxminum article scan counts
  OUTPUT = None # output file location
  
  try:
    opts, etc_args = getopt.getopt(argv[1:], "k:mn:o:", ["keyword=", "multiple", "number=", "output="])
  except getopt.GetoptError as e:
    print(Fore.RED + 'fail\n' + str(e))
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
        sys.exit(1)

    elif opt in ("-o", "--output"):
      OUTPUT = arg

  if len(KEYWORD) < 1:
    print(Fore.RED + '-k or --keyword option is mandatory')
    sys.exit(1)
    
  if MULTIPLE:
    KEYWORD = KEYWORD.split(',')
  
  
  # Loading Selenium driver
  print(Fore.RESET + 'Loading Selenium driver... ', end='')
  sys.stdout.flush()
  try:
    #driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=chrome_options)
  except selenium.common.exceptions.WebDriverException as e:
    print(Fore.RED + 'fail\n' + str(e))
    sys.exit()
  print(Fore.GREEN + 'OK')
  sys.stdout.flush()
  
  
  # Start scanning keywords
  if isinstance(KEYWORD, str): # if KEYWORD is a single string
    keyword_scan(KEYWORD)
  else: # if KEYWORD is a keyword array
    for keyword in KEYWORD:
      keyword_scan(keyword)

      
def keyword_scan(KEYWORD):
  print(Fore.RESET + 'Scanning keyword: ' + KEYWORD)
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
    sys.exit()
  print(Fore.GREEN + 'OK')
  sys.stdout.flush()

  # Scan list of articles until maximum scan number met
  if not SCAN_NUMBER: # if no maximum scan number is set
    while True: # infinite loop. Break on moreList == false
      break
  else: # if there is a maximum scan number
    while article_count < SCAN_NUMBER:
      break
      
  time.sleep(3) # Wait until all articles are loaded. Nominal article count value is 20
  article_count = len(driver.find_element(By.CSS_SELECTOR, 'ul.list_article.list_common').find_elements(By.TAG_NAME, 'li'))
  print(article_count)
  # Looking for <script> tag with B.Keyword.init()
  for script_content in driver.find_element(By.TAG_NAME, 'body').find_elements(By.TAG_NAME, 'script'):
    script = script_content.get_attribute('innerHTML').strip()
    #if script[:14] == 'B.Keyword.init':


      
      
      
      
      

def crawler(driver, config, code, timeline):
  # Crawling item info
  print(Fore.RESET + 'Crawling item info... ', end='')
  sys.stdout.flush()
  try:
    driver.get('https://www.ros-bot.com/user/' + code + '/bot-activity')
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "edit-item-destination")))
    Select(driver.find_element(By.ID, 'edit-item-destination')).select_by_visible_text('Stashed')
    driver.find_element(By.ID, 'edit-item-destination').submit()
    # Getting timeline points
    timepoints = driver.find_elements(By.CSS_SELECTOR, 'div.timeline-item div.row')
    print(Fore.GREEN + 'OK')
    sys.stdout.flush()

    for point in timepoints:
      soup = BeautifulSoup(point.get_attribute('innerHTML'), 'html.parser')
      elem = soup.select_one('div.date').findAll(text=True, recursive=False)
      date = None
      # Identifying timeline point
      for el in elem:
        date = re.sub('\n', '', el).strip()
        if date: break
      # Getting timeline detail if new timeline appears
      if not timeline.issuperset({ date }):
        payload = { 'destination': config['user']['telegram'], 'date': date, 'contents': [] }
        timeline.add(date)
        items = soup.select_one('div.content').select('div p span')
        for item in items:
          payload['contents'].append({ 'title': item['data-title'], 'detail': re.sub('<br />\n', '\n', item['data-content']) })
          
        # Sending data to server
        print(Fore.RESET + 'Transmitting data... ', end='')
        sys.stdout.flush()
        try:
          req = request.Request('https://luftaquila.io/api/telepath/report', data=parse.urlencode(payload).encode())
          res = request.urlopen(req)
        except urllib.error.HTTPError as e:
          print(Fore.RED + 'fail')
          print(e)
          continue
        print(Fore.GREEN + 'OK')
        sys.stdout.flush()
        
  except:
    print(Fore.RED + 'fail')
    print(sys.exc_info()[0])
    sys.exit()
    
  try:
    target_time = datetime.datetime.now() + datetime.timedelta(0, int(config['rover']['refresh']))
    print(Fore.RESET + 'Waiting for next execution: ', end='')
    print(Fore.CYAN + str(target_time))
    while(target_time - datetime.datetime.now()).total_seconds() > 0 :
      print(Fore.RESET + '  Countdown: ', end='')
      print(Fore.CYAN + str(target_time - datetime.datetime.now()), end='\r')
      sys.stdout.flush()

    print(Fore.RESET + '  Countdown: ', end='')
    print(Fore.CYAN + '0:00:00.000000\n')
    sys.stdout.flush()
  except:
    print(Fore.RED + 'fail')
    print(sys.exc_info()[0])
    sys.exit()
    
  crawler(driver, config, code, timeline)
  #threading.Timer(int(config['rover']['refresh']), crawler, [driver, config, code, timeline]).start()

if __name__ == "__main__":
  main(sys.argv)
