import time

from web_crawl import crawl_and_save as crawl_and_save_web
from api_crawl import crawl_and_save as crawl_and_save_api

crawl_and_save_web()

time.sleep(60)

crawl_and_save_api()
