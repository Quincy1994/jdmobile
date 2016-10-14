# coding=utf-8
import urllib
import re
from selenium import webdriver

price_url = 'http://item.jd.com/1963190765.html'
# browser = webdriver.PhantomJS()
# browser.get(price_url)
# content = browser.page_source

content = urllib.urlopen(price_url).read()

print content
price_pattern = re.compile("<span class=\"big-price\">(.*?)</span>")
price = price_pattern.findall(content)

print price[0]

